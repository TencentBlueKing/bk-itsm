# -*- coding: utf-8 -*-
"""
基于日志表增量驱动的 Ticket 同步 Django Command：旧库 → 新库

用法：
  python manage.py migrate_ticket_from_old_db
  python manage.py migrate_ticket_from_old_db --dry-run

参数：
  --src-host        旧库 host（必填）
  --src-port        旧库 port（默认 3306）
  --src-user        旧库 user（必填）
  --src-password    旧库 password（必填）
  --src-db          旧库库名（必填）
  --dst-host        新库 host（环境变量 DST_MYSQL_HOST）
  --dst-port        新库 port（环境变量 DST_MYSQL_PORT，默认 3306）
  --dst-user        新库 user（环境变量 DST_MYSQL_USER）
  --dst-password    新库 password（环境变量 DST_MYSQL_PASSWORD）
  --dst-db          新库库名（环境变量 DST_MYSQL_NAME）
  --dry-run         只预览，不执行任何写入
  --batch-size      每批处理行数（默认 500）
"""

import os
import traceback

import pymysql
from django.core.management.base import BaseCommand

# ============================================================
# ticket 关联子表配置
# 格式：(表名, ticket关联字段名, 同步策略)
# 策略：
#   "replace"  = INSERT ON DUPLICATE KEY UPDATE（适合数据会更新的表）
#   "insert"   = 只插入新库没有的数据（ON DUPLICATE KEY SKIP，适合只增不改的日志类表）
# ============================================================
TICKET_SUB_TABLES = [
    ("ticket_ticketfield",          "ticket_id",      "replace"),   # 表单字段值（会更新）
    ("ticket_ticketcomment",        "ticket_id",      "replace"),   # 满意度评价（会更新）
    ("ticket_ticketeventlog",       "ticket_id",      "insert"),    # 操作日志（只增不改）
    ("ticket_statustransitlog",     "ticket_id",      "insert"),    # 状态流转日志（只增不改）
    ("ticket_attentionusers",       "ticket_id",      "replace"),   # 关注人（会变化）
    ("ticket_ticketremark",         "ticket_id",      "replace"),   # 备注（会更新）
    ("ticket_tickettoticket",       "from_ticket_id", "replace"),   # 单据关联（会变化）
    ("ticket_status",               "ticket_id",      "replace"),   # 节点处理状态（核心数据，会更新）
    ("ticket_ticket_node_status",   "ticket_id",      "replace"),   # M2M中间表：ticket与节点状态的关联（核心，缺失会导致 node_status QuerySet 为空）
    ("ticket_ticketglobalvariable", "ticket_id",      "replace"),   # 自动节点全局变量（会更新）
    ("ticket_ticketstatedraft",     "ticket_id",      "replace"),   # 节点草稿（处理中的临时数据）
    ("ticket_follownotifylog",      "ticket_id",      "insert"),    # 关注人通知日志（只增不改）
    ("ticket_supervisenotifylog",   "ticket_id",      "insert"),    # 督办通知日志（只增不改）
]

LOG_TABLE    = "ticket_ticketeventlog"
TICKET_TABLE = "ticket_ticket"

# 新库自增 ID 起点阈值：新库本地产生的记录 id >= 此值，旧库同步过来的记录 id < 此值
# 水位线计算时只取 id < NATIVE_ID_THRESHOLD 的最大值，避免新库本地数据干扰增量识别
NATIVE_ID_THRESHOLD = 10_000_000


# ============================================================
# 工具函数
# ============================================================

def get_connection(host, port, user, password, db):
    """创建数据库连接"""
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_columns(cursor, db_name, table_name):
    """获取指定库表的列名列表"""
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s "
        "ORDER BY ORDINAL_POSITION",
        [db_name, table_name]
    )
    return [row["COLUMN_NAME"] for row in cursor.fetchall()]


def get_common_cols(src_cursor, dst_cursor, table_name, src_db, dst_db):
    """获取新旧库公共列名列表"""
    src_cols = get_columns(src_cursor, src_db, table_name)
    dst_cols = set(get_columns(dst_cursor, dst_db, table_name))
    return [c for c in src_cols if c in dst_cols]


def fetch_rows_by_ids(cursor, table_name, id_field, id_list, col_list, batch_size):
    """按 id 列表分批查询数据，返回所有行"""
    if not id_list:
        return []
    col_str = ", ".join(f"`{c}`" for c in col_list)
    all_rows = []
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i: i + batch_size]
        placeholders = ", ".join(["%s"] * len(batch_ids))
        cursor.execute(
            f"SELECT {col_str} FROM `{table_name}` WHERE `{id_field}` IN ({placeholders})",
            batch_ids
        )
        all_rows.extend(cursor.fetchall())
    return all_rows


def upsert_rows(dst_cursor, dst_conn, table_name, col_list, rows, batch_size):
    """
    INSERT ... ON DUPLICATE KEY UPDATE 所有列（全量覆盖更新）
    用于 ticket 主表：新增插入，已有则更新所有字段
    """
    if not rows:
        return 0
    col_str = ", ".join(f"`{c}`" for c in col_list)
    placeholders = ", ".join(["%s"] * len(col_list))
    update_cols = [c for c in col_list if c != "id"]
    update_str = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in update_cols)
    sql = (
        f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {update_str}"
    )
    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    try:
        for i in range(0, len(rows), batch_size):
            batch = [tuple(row[c] for c in col_list) for row in rows[i: i + batch_size]]
            dst_cursor.executemany(sql, batch)
            dst_conn.commit()
    finally:
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        dst_conn.commit()
    return len(rows)


def replace_sub_table(src_cursor, dst_cursor, dst_conn, table_name, ticket_id_field,
                      ticket_ids, dry_run, src_db, dst_db, batch_size):
    """
    upsert 策略：INSERT ON DUPLICATE KEY UPDATE，新增插入，已有则覆盖更新
    """
    common_cols = get_common_cols(src_cursor, dst_cursor, table_name, src_db, dst_db)
    if not common_cols:
        print(f"    [WARN]  {table_name}  无公共列，跳过")
        return 0

    rows = []
    col_str_fetch = ", ".join(f"`{c}`" for c in common_cols)
    for i in range(0, len(ticket_ids), batch_size):
        batch_ids = ticket_ids[i: i + batch_size]
        placeholders = ", ".join(["%s"] * len(batch_ids))
        src_cursor.execute(
            f"SELECT {col_str_fetch} FROM `{table_name}` WHERE `{ticket_id_field}` IN ({placeholders})",
            batch_ids
        )
        rows.extend(src_cursor.fetchall())

    if dry_run:
        print(f"    [DRY]   {table_name}  待同步 {len(rows)} 行（upsert策略，{ticket_id_field}）")
        return len(rows)

    col_str = ", ".join(f"`{c}`" for c in common_cols)
    placeholders = ", ".join(["%s"] * len(common_cols))
    update_cols = [c for c in common_cols if c != "id"]
    insert_sql = (
        f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {', '.join(f'`{c}`=VALUES(`{c}`)' for c in update_cols)}"
    )

    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    try:
        for i in range(0, len(rows), batch_size):
            batch = [tuple(row[c] for c in common_cols) for row in rows[i: i + batch_size]]
            dst_cursor.executemany(insert_sql, batch)
            dst_conn.commit()
    finally:
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        dst_conn.commit()

    print(f"    [OK]    {table_name}  同步完成 {len(rows)} 行")
    return len(rows)


def insert_sub_table(src_cursor, dst_cursor, dst_conn, table_name, ticket_id_field,
                     ticket_ids, dry_run, src_db, dst_db, batch_size):
    """
    insert 策略：只插入新库没有的数据（ON DUPLICATE KEY SKIP）
    适合只增不改的日志类表
    """
    common_cols = get_common_cols(src_cursor, dst_cursor, table_name, src_db, dst_db)
    if not common_cols:
        print(f"    [WARN]  {table_name}  无公共列，跳过")
        return 0

    rows = fetch_rows_by_ids(src_cursor, table_name, ticket_id_field, ticket_ids, common_cols, batch_size)

    if dry_run:
        print(f"    [DRY]   {table_name}  待同步 {len(rows)} 行（insert策略，ticket_id字段={ticket_id_field}）")
        return len(rows)

    col_str = ", ".join(f"`{c}`" for c in common_cols)
    placeholders = ", ".join(["%s"] * len(common_cols))
    first_col = f"`{common_cols[0]}`"
    insert_sql = (
        f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {first_col}={first_col}"
    )

    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    try:
        for i in range(0, len(rows), batch_size):
            batch = [tuple(row[c] for c in common_cols) for row in rows[i: i + batch_size]]
            dst_cursor.executemany(insert_sql, batch)
            dst_conn.commit()
    finally:
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        dst_conn.commit()

    print(f"    [OK]    {table_name}  同步完成 {len(rows)} 行")
    return len(rows)


def _upsert_table(dst_cursor, dst_conn, table_name, col_list, rows, batch_size):
    """通用 upsert 辅助函数，供 sync_engine_tables 内部使用"""
    if not rows:
        return
    col_str = ", ".join(f"`{c}`" for c in col_list)
    placeholders = ", ".join(["%s"] * len(col_list))
    update_cols = [c for c in col_list if c != "id"]
    if update_cols:
        update_str = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in update_cols)
        sql = f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_str}"
    else:
        sql = f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE `id`=`id`"
    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    try:
        for i in range(0, len(rows), batch_size):
            batch = [tuple(row[c] for c in col_list) for row in rows[i: i + batch_size]]
            dst_cursor.executemany(sql, batch)
            dst_conn.commit()
    finally:
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        dst_conn.commit()


def sync_base_tables(src_cursor, dst_cursor, dst_conn, ticket_ids, dry_run, src_db, dst_db, batch_size,
                     print_fn=print):
    """
    按 ticket 关联的 flow_id / service_id 精确同步基础配置表。

    采用 INSERT IGNORE 策略：新库已有的记录不覆盖，只补充缺失的。

    同步顺序（按外键依赖顺序）：
      1. workflow_workflowversion   （流程版本快照，ticket.flow_id 指向这里，内含 fields/states JSON 快照）
      2. service_service            （服务，ticket.service_id 指向这里）
      3. service_servicecatalog     （服务目录，service.catalog_id 指向这里，树形结构需递归补全父节点）
      4. service_catalogservice     （服务与目录关联）
      5. service_servicesla         （服务与SLA关联）
    """
    if not ticket_ids:
        return

    ph = ", ".join(["%s"] * len(ticket_ids))

    # ---- 1. 提取 flow_id 和 service_id ----
    src_cursor.execute(
        f"SELECT DISTINCT `flow_id`, `service_id` FROM `ticket_ticket` WHERE `id` IN ({ph})",
        ticket_ids
    )
    rows_meta = src_cursor.fetchall()
    flow_ids    = list({r["flow_id"]    for r in rows_meta if r["flow_id"]})
    service_ids = list({r["service_id"] for r in rows_meta if r["service_id"]})

    # workflow_workflowversion 必须用 UPSERT，因为新库可能存在 transitions/states 字段残缺的旧数据
    UPSERT_TABLES = {"workflow_workflowversion", "service_service"}

    def _sync_by_ids(table_name, id_field, id_list):
        """按 id_list 精确同步指定表，INSERT IGNORE（UPSERT_TABLES 中的表用 ON DUPLICATE KEY UPDATE）"""
        if not id_list:
            print_fn(f"    [SKIP]  {table_name}  无关联ID，跳过")
            return
        common_cols = get_common_cols(src_cursor, dst_cursor, table_name, src_db, dst_db)
        if not common_cols:
            print_fn(f"    [WARN]  {table_name}  无公共列，跳过")
            return
        col_str = ", ".join(f"`{c}`" for c in common_cols)
        all_rows = []
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i: i + batch_size]
            bph = ", ".join(["%s"] * len(batch_ids))
            src_cursor.execute(
                f"SELECT {col_str} FROM `{table_name}` WHERE `{id_field}` IN ({bph})",
                batch_ids
            )
            all_rows.extend(src_cursor.fetchall())
        if dry_run:
            # 对比新库，计算真正需要新增/更新的行数
            existing_ids = set()
            if all_rows and id_field in all_rows[0]:
                row_ids = [row[id_field] for row in all_rows]
                for i in range(0, len(row_ids), batch_size):
                    batch_ids = row_ids[i: i + batch_size]
                    bph2 = ", ".join(["%s"] * len(batch_ids))
                    dst_cursor.execute(
                        f"SELECT `{id_field}` FROM `{table_name}` WHERE `{id_field}` IN ({bph2})",
                        batch_ids
                    )
                    existing_ids.update(row[id_field] for row in dst_cursor.fetchall())
            need_insert = len([r for r in all_rows if r[id_field] not in existing_ids])
            need_update = len([r for r in all_rows if r[id_field] in existing_ids])
            strategy = "UPSERT（覆盖更新）" if table_name in UPSERT_TABLES else "INSERT IGNORE"
            if table_name in UPSERT_TABLES:
                print_fn(
                    f"    [DRY]   {table_name}  旧库 {len(all_rows)} 行"
                    f"（新库已有 {len(existing_ids)} 行，{strategy} 新增 {need_insert} 行 / 覆盖更新 {need_update} 行）"
                )
            else:
                print_fn(
                    f"    [DRY]   {table_name}  旧库 {len(all_rows)} 行"
                    f"（新库已有 {len(existing_ids)} 行，{strategy} 实际新增 {need_insert} 行）"
                )
            return
        if not all_rows:
            print_fn(f"    [SKIP]  {table_name}  旧库无匹配数据")
            return
        placeholders = ", ".join(["%s"] * len(common_cols))
        if table_name in UPSERT_TABLES:
            # UPSERT：新增插入，已有则覆盖更新（确保 JSON 字段等数据完整）
            update_cols = [c for c in common_cols if c != "id"]
            update_str = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in update_cols)
            insert_sql = (
                f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {update_str}"
            )
        else:
            insert_sql = f"INSERT IGNORE INTO `{table_name}` ({col_str}) VALUES ({placeholders})"
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        try:
            for i in range(0, len(all_rows), batch_size):
                batch = [tuple(row[c] for c in common_cols) for row in all_rows[i: i + batch_size]]
                dst_cursor.executemany(insert_sql, batch)
                dst_conn.commit()
        finally:
            dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            dst_conn.commit()
        print_fn(f"    [OK]    {table_name}  同步完成 {len(all_rows)} 行")

    # ---- 2. 同步 workflow_workflowversion（ticket.flow_id 指向这里）----
    _sync_by_ids("workflow_workflowversion", "id", flow_ids)

    # ---- 3. 同步 service_service（ticket.service_id 指向这里）----
    _sync_by_ids("service_service", "id", service_ids)

    # ---- 4. 提取 catalog_id，递归补全 service_servicecatalog 父节点 ----
    # catalog_id 在中间表 service_catalogservice 里，不在 service_service 里
    if service_ids:
        sph = ", ".join(["%s"] * len(service_ids))
        src_cursor.execute(
            f"SELECT DISTINCT `catalog_id` FROM `service_catalogservice` WHERE `service_id` IN ({sph})",
            service_ids
        )
        catalog_ids = list({r["catalog_id"] for r in src_cursor.fetchall() if r["catalog_id"]})

        # 递归向上补全父节点（树形结构）
        all_catalog_ids = set(catalog_ids)
        to_check = list(catalog_ids)
        while to_check:
            cph = ", ".join(["%s"] * len(to_check))
            src_cursor.execute(
                f"SELECT `id`, `parent_id` FROM `service_servicecatalog` WHERE `id` IN ({cph})",
                to_check
            )
            to_check = []
            for row in src_cursor.fetchall():
                if row["parent_id"] and row["parent_id"] not in all_catalog_ids:
                    all_catalog_ids.add(row["parent_id"])
                    to_check.append(row["parent_id"])

        _sync_by_ids("service_servicecatalog", "id", list(all_catalog_ids))

        # ---- 5. 同步 service_catalogservice（服务与目录关联）----
        _sync_by_ids("service_catalogservice", "service_id", service_ids)

        # ---- 6. 同步 service_servicesla（服务与SLA关联）----
        _sync_by_ids("service_servicesla", "service_id", service_ids)


def sync_engine_tables(src_cursor, dst_cursor, dst_conn, ticket_ids, dry_run, src_db, dst_db, batch_size):
    """
    同步 engine 相关表：
      engine_pipelineprocess / engine_pipelinemodel / engine_processsnapshot
      engine_noderelationship / engine_status / engine_data
      engine_history / engine_scheduleservice / ticket_signtask
    """
    if not ticket_ids:
        return

    # root_pipeline_id / ancestor_id 等字段是 VARCHAR，存的是 ticket.id 的字符串形式，需要转换
    ticket_ids_str = [str(tid) for tid in ticket_ids]

    # 1. 同步 engine_pipelineprocess
    table = "engine_pipelineprocess"
    common_cols = get_common_cols(src_cursor, dst_cursor, table, src_db, dst_db)
    if not common_cols:
        print(f"    [WARN]  {table}  无公共列，跳过")
        return

    process_rows = fetch_rows_by_ids(src_cursor, table, "root_pipeline_id", ticket_ids_str, common_cols, batch_size)
    process_ids = [row["id"] for row in process_rows] if process_rows else []

    if dry_run:
        print(f"    [DRY]   {table}  待同步 {len(process_rows)} 行")
    else:
        col_str = ", ".join(f"`{c}`" for c in common_cols)
        placeholders = ", ".join(["%s"] * len(common_cols))
        update_str = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in common_cols if c != "id")
        upsert_sql = f"INSERT INTO `{table}` ({col_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_str}"
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        try:
            for i in range(0, len(process_rows), batch_size):
                batch = [tuple(row[c] for c in common_cols) for row in process_rows[i: i + batch_size]]
                dst_cursor.executemany(upsert_sql, batch)
                dst_conn.commit()
        finally:
            dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            dst_conn.commit()
        print(f"    [OK]    {table}  同步完成 {len(process_rows)} 行")

    # 2. 同步 engine_pipelinemodel
    if process_ids:
        table2 = "engine_pipelinemodel"
        common_cols2 = get_common_cols(src_cursor, dst_cursor, table2, src_db, dst_db)
        if common_cols2:
            model_rows = fetch_rows_by_ids(src_cursor, table2, "process_id", process_ids, common_cols2, batch_size)
            if dry_run:
                print(f"    [DRY]   {table2}  待同步 {len(model_rows)} 行")
            else:
                col_str2 = ", ".join(f"`{c}`" for c in common_cols2)
                placeholders2 = ", ".join(["%s"] * len(common_cols2))
                first_col2 = f"`{common_cols2[0]}`"
                upsert_sql2 = (
                    f"INSERT INTO `{table2}` ({col_str2}) VALUES ({placeholders2}) "
                    f"ON DUPLICATE KEY UPDATE {first_col2}={first_col2}"
                )
                dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                try:
                    for i in range(0, len(model_rows), batch_size):
                        batch = [tuple(row[c] for c in common_cols2) for row in model_rows[i: i + batch_size]]
                        dst_cursor.executemany(upsert_sql2, batch)
                        dst_conn.commit()
                finally:
                    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                    dst_conn.commit()
                print(f"    [OK]    {table2}  同步完成 {len(model_rows)} 行")

    # 3. 同步 engine_processsnapshot（通过 process.snapshot_id 关联）
    if process_ids:
        table_snap = "engine_processsnapshot"
        common_cols_snap = get_common_cols(src_cursor, dst_cursor, table_snap, src_db, dst_db)
        if common_cols_snap:
            snapshot_ids = []
            for i in range(0, len(process_ids), batch_size):
                batch_ids = process_ids[i: i + batch_size]
                ph = ", ".join(["%s"] * len(batch_ids))
                src_cursor.execute(
                    f"SELECT `snapshot_id` FROM `engine_pipelineprocess` WHERE `id` IN ({ph})",
                    batch_ids
                )
                snapshot_ids.extend([row["snapshot_id"] for row in src_cursor.fetchall() if row["snapshot_id"]])
            snap_rows = fetch_rows_by_ids(src_cursor, table_snap, "id", snapshot_ids, common_cols_snap, batch_size)
            if dry_run:
                print(f"    [DRY]   {table_snap}  待同步 {len(snap_rows)} 行")
            else:
                _upsert_table(dst_cursor, dst_conn, table_snap, common_cols_snap, snap_rows, batch_size)
                print(f"    [OK]    {table_snap}  同步完成 {len(snap_rows)} 行")

    # 4. 提取所有节点 UUID（通过 engine_noderelationship）
    # ancestor_id 是 VARCHAR 字段，存的是 ticket.id 的字符串形式
    node_ids = []
    for i in range(0, len(ticket_ids_str), batch_size):
        batch_ids = ticket_ids_str[i: i + batch_size]
        ph = ", ".join(["%s"] * len(batch_ids))
        src_cursor.execute(
            f"SELECT DISTINCT `descendant_id` FROM `engine_noderelationship` WHERE `ancestor_id` IN ({ph})",
            batch_ids
        )
        node_ids.extend([row["descendant_id"] for row in src_cursor.fetchall()])
    node_ids = list(set(node_ids) | set(ticket_ids_str))

    # 5. 同步 engine_noderelationship
    table_nr = "engine_noderelationship"
    common_cols_nr = get_common_cols(src_cursor, dst_cursor, table_nr, src_db, dst_db)
    if common_cols_nr:
        nr_rows = fetch_rows_by_ids(src_cursor, table_nr, "ancestor_id", ticket_ids_str, common_cols_nr, batch_size)
        if dry_run:
            print(f"    [DRY]   {table_nr}  待同步 {len(nr_rows)} 行")
        else:
            _upsert_table(dst_cursor, dst_conn, table_nr, common_cols_nr, nr_rows, batch_size)
            print(f"    [OK]    {table_nr}  同步完成 {len(nr_rows)} 行")

    # 6. 同步 engine_status（节点执行状态，id=节点UUID）
    table_es = "engine_status"
    common_cols_es = get_common_cols(src_cursor, dst_cursor, table_es, src_db, dst_db)
    if common_cols_es:
        es_rows = fetch_rows_by_ids(src_cursor, table_es, "id", node_ids, common_cols_es, batch_size)
        if dry_run:
            print(f"    [DRY]   {table_es}  待同步 {len(es_rows)} 行")
        else:
            _upsert_table(dst_cursor, dst_conn, table_es, common_cols_es, es_rows, batch_size)
            print(f"    [OK]    {table_es}  同步完成 {len(es_rows)} 行")

    # 7. 同步 engine_data（节点输入输出数据，id=节点UUID）
    table_ed = "engine_data"
    common_cols_ed = get_common_cols(src_cursor, dst_cursor, table_ed, src_db, dst_db)
    if common_cols_ed:
        ed_rows = fetch_rows_by_ids(src_cursor, table_ed, "id", node_ids, common_cols_ed, batch_size)
        if dry_run:
            print(f"    [DRY]   {table_ed}  待同步 {len(ed_rows)} 行")
        else:
            _upsert_table(dst_cursor, dst_conn, table_ed, common_cols_ed, ed_rows, batch_size)
            print(f"    [OK]    {table_ed}  同步完成 {len(ed_rows)} 行")

    # 8. 同步 engine_history（节点重试历史，identifier=节点UUID）
    table_eh = "engine_history"
    common_cols_eh = get_common_cols(src_cursor, dst_cursor, table_eh, src_db, dst_db)
    if common_cols_eh:
        eh_rows = fetch_rows_by_ids(src_cursor, table_eh, "identifier", node_ids, common_cols_eh, batch_size)
        if dry_run:
            print(f"    [DRY]   {table_eh}  待同步 {len(eh_rows)} 行")
        else:
            _upsert_table(dst_cursor, dst_conn, table_eh, common_cols_eh, eh_rows, batch_size)
            print(f"    [OK]    {table_eh}  同步完成 {len(eh_rows)} 行")

    # 9. 同步 engine_scheduleservice（调度服务，activity_id=节点UUID）
    table_ss = "engine_scheduleservice"
    common_cols_ss = get_common_cols(src_cursor, dst_cursor, table_ss, src_db, dst_db)
    if common_cols_ss:
        ss_rows = fetch_rows_by_ids(src_cursor, table_ss, "activity_id", node_ids, common_cols_ss, batch_size)
        if dry_run:
            print(f"    [DRY]   {table_ss}  待同步 {len(ss_rows)} 行")
        else:
            _upsert_table(dst_cursor, dst_conn, table_ss, common_cols_ss, ss_rows, batch_size)
            print(f"    [OK]    {table_ss}  同步完成 {len(ss_rows)} 行")

    # 10. 同步 ticket_signtask（通过 ticket_status.id 间接关联 ticket）
    table3 = "ticket_signtask"
    common_cols3 = get_common_cols(src_cursor, dst_cursor, table3, src_db, dst_db)
    if not common_cols3:
        print(f"    [WARN]  {table3}  无公共列，跳过")
        return

    status_ids = []
    for i in range(0, len(ticket_ids), batch_size):
        batch_ids = ticket_ids[i: i + batch_size]
        ph = ", ".join(["%s"] * len(batch_ids))
        src_cursor.execute(
            f"SELECT `id` FROM `ticket_status` WHERE `ticket_id` IN ({ph})",
            batch_ids
        )
        status_ids.extend([row["id"] for row in src_cursor.fetchall()])

    sign_rows = fetch_rows_by_ids(src_cursor, table3, "status_id", status_ids, common_cols3, batch_size)
    if dry_run:
        print(f"    [DRY]   {table3}  待同步 {len(sign_rows)} 行（通过status_id关联）")
    else:
        col_str3 = ", ".join(f"`{c}`" for c in common_cols3)
        placeholders3 = ", ".join(["%s"] * len(common_cols3))
        update_cols3 = [c for c in common_cols3 if c != "id"]
        upsert_sql3 = (
            f"INSERT INTO `{table3}` ({col_str3}) VALUES ({placeholders3}) "
            f"ON DUPLICATE KEY UPDATE {', '.join(f'`{c}`=VALUES(`{c}`)' for c in update_cols3)}"
        )
        dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        try:
            for i in range(0, len(sign_rows), batch_size):
                batch = [tuple(row[c] for c in common_cols3) for row in sign_rows[i: i + batch_size]]
                dst_cursor.executemany(upsert_sql3, batch)
                dst_conn.commit()
        finally:
            dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            dst_conn.commit()
        print(f"    [OK]    {table3}  同步完成 {len(sign_rows)} 行")


# ============================================================
# Django Command
# ============================================================

class Command(BaseCommand):
    help = "基于日志表增量驱动，将旧库 Ticket 数据同步到新库"

    def add_arguments(self, parser):
        # 旧库连接参数
        parser.add_argument("--src-host", help="旧库 host）")
        parser.add_argument("--src-port", type=int, default=3306, help="旧库 port（默认 3306）")
        parser.add_argument("--src-user", help="旧库 user")
        parser.add_argument("--src-password", help="旧库 password")
        parser.add_argument("--src-db", help="旧库库名")
        # 新库连接参数（优先读取环境变量，也可通过命令行参数覆盖）
        parser.add_argument("--dst-host",     default=os.environ.get("MYSQL_HOST"))
        parser.add_argument("--dst-port",     default=int(os.environ.get("MYSQL_PORT", 3306)), type=int)
        parser.add_argument("--dst-user",     default=os.environ.get("MYSQL_USER"))
        parser.add_argument("--dst-password", default=os.environ.get("MYSQL_PASSWORD"))
        parser.add_argument("--dst-db",       default=os.environ.get("MYSQL_NAME"))
        # 其他参数
        parser.add_argument("--dry-run",      action="store_true",            help="只预览，不执行任何写入")
        parser.add_argument("--batch-size",   default=500,     type=int,      help="每批处理行数（默认 500）")

    def handle(self, *args, **options):
        src_host     = options["src_host"]
        src_port     = options["src_port"]
        src_user     = options["src_user"]
        src_password = options["src_password"]
        src_db       = options["src_db"]
        dst_host     = options["dst_host"]
        dst_port     = options["dst_port"]
        dst_user     = options["dst_user"]
        dst_password = options["dst_password"]
        dst_db       = options["dst_db"]
        dry_run      = options["dry_run"]
        batch_size   = options["batch_size"]

        self.stdout.write("=" * 65)
        self.stdout.write(f"旧库: {src_host}:{src_port}/{src_db}")
        self.stdout.write(f"新库: {dst_host}:{dst_port}/{dst_db}")
        self.stdout.write(f"模式: {'DRY RUN（仅预览，不执行）' if dry_run else '真正执行同步'}")
        self.stdout.write(f"驱动: {LOG_TABLE} 日志表增量")
        self.stdout.write("=" * 65)

        # 连接数据库
        try:
            src_conn = get_connection(src_host, src_port, src_user, src_password, src_db)
            self.stdout.write("\n旧库连接成功")
        except Exception as e:
            self.stderr.write(f"[ERROR] 旧库连接失败: {e}")
            return

        try:
            dst_conn = get_connection(dst_host, dst_port, dst_user, dst_password, dst_db)
            self.stdout.write("新库连接成功\n")
        except Exception as e:
            self.stderr.write(f"[ERROR] 新库连接失败: {e}")
            src_conn.close()
            return

        src_cursor = src_conn.cursor()
        dst_cursor = dst_conn.cursor()

        try:
            # ---- Step 1: 查新库日志表最大 id ----
            # 新库自增 ID 从 NATIVE_ID_THRESHOLD 开始，只取 id < NATIVE_ID_THRESHOLD 的最大值作为水位线
            # 避免新库本地产生的大 ID 干扰旧库增量识别
            dst_cursor.execute(
                f"SELECT IFNULL(MAX(`id`), 0) as max_id FROM `{LOG_TABLE}` WHERE `id` < %s",
                [NATIVE_ID_THRESHOLD]
            )
            dst_max_log_id = dst_cursor.fetchone()["max_id"]
            self.stdout.write(f"新库 {LOG_TABLE} 最大 id = {dst_max_log_id}（仅统计 id < {NATIVE_ID_THRESHOLD} 的旧库同步数据）")

            # ---- Step 2: 查旧库新增的日志记录数 ----
            src_cursor.execute(
                f"SELECT COUNT(*) as cnt FROM `{LOG_TABLE}` WHERE `id` > %s",
                [dst_max_log_id]
            )
            new_log_count = src_cursor.fetchone()["cnt"]
            self.stdout.write(f"旧库新增日志记录数 = {new_log_count}")

            if new_log_count == 0:
                self.stdout.write("\n✅  无新增日志，数据已是最新，无需同步。")
                return

            # ---- Step 3: 提取涉及的 ticket_id 集合 ----
            src_cursor.execute(
                f"SELECT DISTINCT `ticket_id` FROM `{LOG_TABLE}` WHERE `id` > %s",
                [dst_max_log_id]
            )
            ticket_ids = [row["ticket_id"] for row in src_cursor.fetchall()]
            self.stdout.write(f"涉及 ticket 数量 = {len(ticket_ids)}")
            self.stdout.write(
                f"ticket_id 列表（前20个）: {ticket_ids[:20]}{'...' if len(ticket_ids) > 20 else ''}"
            )
            self.stdout.write("")

            if dry_run:
                self.stdout.write("【DRY RUN 预览】以下为待同步内容：\n")

            # ---- Step 4: 同步基础配置表（service / workflow，确保 ticket 依赖的数据先到位）----
            self.stdout.write("  【DRY RUN 基础表预览】" if dry_run else "  【同步基础配置表】")
            sync_base_tables(
                src_cursor, dst_cursor, dst_conn,
                ticket_ids, dry_run, src_db, dst_db, batch_size,
                print_fn=self.stdout.write,
            )
            self.stdout.write("")

            # ---- Step 5: 同步 ticket 主表 ----
            ticket_common_cols = get_common_cols(src_cursor, dst_cursor, TICKET_TABLE, src_db, dst_db)
            ticket_rows = fetch_rows_by_ids(src_cursor, TICKET_TABLE, "id", ticket_ids, ticket_common_cols, batch_size)

            dst_cursor.execute(
                f"SELECT `id` FROM `{TICKET_TABLE}` WHERE `id` IN ({', '.join(['%s'] * len(ticket_ids))})",
                ticket_ids
            )
            existing_ids = {row["id"] for row in dst_cursor.fetchall()}
            new_tickets    = [r for r in ticket_rows if r["id"] not in existing_ids]
            update_tickets = [r for r in ticket_rows if r["id"] in existing_ids]

            if dry_run:
                self.stdout.write(
                    f"  [DRY]   {TICKET_TABLE}  新增 {len(new_tickets)} 条 / 更新 {len(update_tickets)} 条"
                    f"（共 {len(ticket_rows)} 条）"
                )
            else:
                upsert_rows(dst_cursor, dst_conn, TICKET_TABLE, ticket_common_cols, ticket_rows, batch_size)
                self.stdout.write(
                    f"  [OK]    {TICKET_TABLE}  同步完成"
                    f"（新增 {len(new_tickets)} 条 / 更新 {len(update_tickets)} 条）"
                )

            # ---- Step 6: 同步 ticket 关联子表 ----
            self.stdout.write("")
            self.stdout.write("  【DRY RUN 关联子表预览】" if dry_run else "  【同步关联子表】")

            for table_name, ticket_id_field, strategy in TICKET_SUB_TABLES:
                try:
                    if strategy == "replace":
                        replace_sub_table(
                            src_cursor, dst_cursor, dst_conn,
                            table_name, ticket_id_field, ticket_ids,
                            dry_run, src_db, dst_db, batch_size
                        )
                    elif strategy == "insert":
                        insert_sub_table(
                            src_cursor, dst_cursor, dst_conn,
                            table_name, ticket_id_field, ticket_ids,
                            dry_run, src_db, dst_db, batch_size
                        )
                except Exception as e:
                    self.stderr.write(f"    [ERROR] {table_name}  同步失败: {e}")

            # ---- Step 7: 同步 engine 相关表 ----
            self.stdout.write("")
            self.stdout.write("  【DRY RUN engine 表预览】" if dry_run else "  【同步 engine 表】")
            sync_engine_tables(
                src_cursor, dst_cursor, dst_conn,
                ticket_ids, dry_run, src_db, dst_db, batch_size
            )

            # ---- Step 8: 同步日志表本身（最后同步，作为水位线） ----
            self.stdout.write("")
            log_common_cols = get_common_cols(src_cursor, dst_cursor, LOG_TABLE, src_db, dst_db)
            src_cursor.execute(
                f"SELECT COUNT(*) as cnt FROM `{LOG_TABLE}` WHERE `id` > %s",
                [dst_max_log_id]
            )
            new_log_total = src_cursor.fetchone()["cnt"]

            if dry_run:
                self.stdout.write(
                    f"  [DRY]   {LOG_TABLE}  待同步新增日志 {new_log_total} 条（id > {dst_max_log_id}）"
                )
            else:
                col_str = ", ".join(f"`{c}`" for c in log_common_cols)
                placeholders = ", ".join(["%s"] * len(log_common_cols))
                first_col = f"`{log_common_cols[0]}`"
                insert_sql = (
                    f"INSERT INTO `{LOG_TABLE}` ({col_str}) VALUES ({placeholders}) "
                    f"ON DUPLICATE KEY UPDATE {first_col}={first_col}"
                )
                offset = 0
                inserted = 0
                dst_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                try:
                    while True:
                        src_cursor.execute(
                            f"SELECT {col_str} FROM `{LOG_TABLE}` WHERE `id` > %s LIMIT %s OFFSET %s",
                            [dst_max_log_id, batch_size, offset]
                        )
                        rows = src_cursor.fetchall()
                        if not rows:
                            break
                        batch = [tuple(row[c] for c in log_common_cols) for row in rows]
                        dst_cursor.executemany(insert_sql, batch)
                        dst_conn.commit()
                        inserted += len(batch)
                        offset += len(batch)
                finally:
                    dst_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                    dst_conn.commit()
                self.stdout.write(f"  [OK]    {LOG_TABLE}  同步完成 {inserted} 条新增日志")

        except Exception as e:
            self.stderr.write(f"\n[ERROR] 同步过程异常: {e}")
            traceback.print_exc()
        finally:
            src_conn.close()
            dst_conn.close()

        self.stdout.write("")
        self.stdout.write("=" * 65)
        if dry_run:
            self.stdout.write("⚠️  当前为 DRY RUN 模式，以上均未执行。")
            self.stdout.write("   确认无误后加上 --dry-run=false 或去掉 --dry-run 再次运行。")
        else:
            self.stdout.write("✅  增量同步完成。")
        self.stdout.write("=" * 65)
