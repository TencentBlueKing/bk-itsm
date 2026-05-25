# -*- coding: utf-8 -*-
"""
修复新库中 service_service.workflow_id 指向旧 WorkflowVersion 的异常数据。

问题根因：
  旧库数据同步时，service_service 表被旧数据覆盖，导致 service.workflow_id 指向的
  WorkflowVersion 不是该 Workflow 下 id 最大（最新）的版本。
  而 Workflow.get_iam_resource() 使用 WorkflowVersion.objects.filter(workflow_id=...).last()
  取最大 id 的版本，再通过 Service.objects.filter(workflow=latest_wv.id) 查找服务，
  找不到时抛出"服务初始化异常"。

修复逻辑：
  遍历所有未删除的 service，找出 service.workflow_id 与对应 Workflow 下最新
  WorkflowVersion.id 不一致的记录，将 service.workflow_id 更新为最新版本 id。

用法：
  # 扫描 + 修复（默认）
  python manage.py fix_service_workflow_id

  # 仅扫描，不执行修复
  python manage.py fix_service_workflow_id --dry-run

  # 只修复指定 service id
  python manage.py fix_service_workflow_id --svc-ids=51,184
"""

from django.core.management.base import BaseCommand

from itsm.service.models import Service
from itsm.workflow.models import Workflow, WorkflowVersion


class Command(BaseCommand):
    help = "修复 service.workflow_id 指向旧 WorkflowVersion 的异常数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="只扫描，不执行修复写入",
        )
        parser.add_argument(
            "--svc-ids",
            type=str,
            default="",
            help="只检查指定的 service id，逗号分隔（不填则全量扫描）",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        svc_ids_str = options["svc_ids"].strip()

        if dry_run:
            self.stdout.write(self.style.WARNING("【DRY-RUN 模式】只扫描，不执行任何写入"))

        # ===== 第一步：确定扫描范围 =====
        qs = Service._objects.filter(is_deleted=False)
        if svc_ids_str:
            svc_id_list = [int(x.strip()) for x in svc_ids_str.split(",") if x.strip()]
            qs = qs.filter(id__in=svc_id_list)
            self.stdout.write(f"指定扫描 service id: {svc_id_list}")
        else:
            self.stdout.write(f"全量扫描，共 {qs.count()} 条 service 记录")

        # ===== 第二步：扫描异常记录 =====
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("【扫描阶段】检查 service.workflow_id 是否指向最新 WorkflowVersion")
        self.stdout.write("=" * 60)

        # broken: [(service_id, service_name, current_wv_id, latest_wv_id)]
        broken = []
        # orphan: workflow_id 对应的 WorkflowVersion 不存在（外键悬空）
        orphan = []

        for svc in qs.iterator():
            try:
                wv = WorkflowVersion.objects.filter(id=svc.workflow_id).first()
                if not wv:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ⚠️  service.id={svc.id} name={svc.name} "
                            f"workflow_id={svc.workflow_id} → WorkflowVersion 不存在（外键悬空，需人工处理）"
                        )
                    )
                    orphan.append((svc.id, svc.name, svc.workflow_id))
                    continue

                # 取该 workflow 下 id 最大的版本（与 get_iam_resource 逻辑一致）
                latest_wv = WorkflowVersion.objects.filter(
                    workflow_id=wv.workflow_id
                ).last()
                if not latest_wv:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  service.id={svc.id} workflow_id={wv.workflow_id} "
                            f"→ 该 Workflow 下无任何 WorkflowVersion，跳过"
                        )
                    )
                    continue

                if latest_wv.id != svc.workflow_id:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ❌  service.id={svc.id:<6} name={svc.name[:40]:<40} "
                            f"当前 workflow_id={svc.workflow_id} → 最新版本 id={latest_wv.id}（需修复）"
                        )
                    )
                    broken.append((svc.id, svc.name, svc.workflow_id, latest_wv.id))
                # else: 正常，跳过

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  service.id={svc.id} 检查时异常: {e}")
                )

        self.stdout.write(
            f"\n扫描完成：发现 {len(broken)} 条需修复，{len(orphan)} 条外键悬空（需人工处理）"
        )

        if not broken:
            self.stdout.write(self.style.SUCCESS("\n✅ 无需修复，所有 service.workflow_id 均正常"))
            return

        # ===== 第三步：执行修复 =====
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            "【修复阶段】" + ("（DRY-RUN，跳过写入）" if dry_run else "更新 service.workflow_id")
        )
        self.stdout.write("=" * 60)

        fixed = 0
        failed = 0

        for svc_id, svc_name, old_wv_id, new_wv_id in broken:
            if dry_run:
                self.stdout.write(
                    f"  [DRY-RUN] service.id={svc_id:<6} {svc_name[:40]:<40} "
                    f"{old_wv_id} → {new_wv_id}"
                )
                fixed += 1
                continue

            try:
                Service._objects.filter(id=svc_id).update(workflow_id=new_wv_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅  service.id={svc_id:<6} {svc_name[:40]:<40} "
                        f"{old_wv_id} → {new_wv_id}"
                    )
                )
                fixed += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌  service.id={svc_id} 修复失败: {e}")
                )
                failed += 1

        self.stdout.write(
            f"\n修复完成：{'预览' if dry_run else '成功'} {fixed} 条，失败 {failed} 条"
        )

        if dry_run or failed > 0:
            return

        # ===== 第四步：验证修复结果 =====
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("【验证阶段】调用 get_iam_resource() 确认修复有效")
        self.stdout.write("=" * 60)

        ok = 0
        err = 0

        for svc_id, svc_name, old_wv_id, new_wv_id in broken:
            try:
                svc = Service._objects.get(id=svc_id)
                wv = WorkflowVersion.objects.get(id=svc.workflow_id)
                wf = Workflow.objects.get(id=wv.workflow_id)
                resource = wf.get_iam_resource()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅  service.id={svc_id} get_iam_resource 正常 "
                        f"→ 返回 service.id={resource.id}, name={resource.name}"
                    )
                )
                ok += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌  service.id={svc_id} 仍然异常: {e}")
                )
                err += 1

        self.stdout.write(f"\n验证结果：正常 {ok} 条，仍异常 {err} 条")

        if err == 0:
            self.stdout.write(self.style.SUCCESS("\n🎉 所有异常 service 修复验证通过！"))
        else:
            self.stdout.write(
                self.style.ERROR(f"\n⚠️  仍有 {err} 条 service 异常，请人工排查")
            )
