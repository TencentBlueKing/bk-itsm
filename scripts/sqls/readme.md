# 数据库手动操作方法

1、登录到中控机
2、source /data/install/utils.fc
3、拷贝sql文件到中控机（可以从appt下载过来）
4、依次执行以下sql

```bash
mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT --default-character-set=utf8 bk_itsm_bkt < ticket_0028.sql
mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT --default-character-set=utf8 bk_itsm_bkt < workflow_0015.sql
mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT --default-character-set=utf8 bk_itsm_bkt < django_migrations.sql
```