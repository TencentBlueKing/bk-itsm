#!/bin/sh

# 将本地设置文件放到配置目录，该配置会优先生效，用于配置测试DB等
# -f 表示直接覆盖文件不提示
SCRIPT_DIR=$(dirname $(readlink -f "$0"))

cat << EOF
dollar_zero -> "$0"
SCRIPT_DIR -> "$SCRIPT_DIR"
EOF
cp -f "${SCRIPT_DIR}/local_settings.py" "./config/local_settings.py"
cat "./config/local_settings.py"

# 安装pip依赖
pip install -r requirements.txt
pip install -r requirements.dev.txt
pip install -r requirements_open.txt
pip install black

# 删除遗留数据库，并新建一个空的本地数据库
CREATE_DB_SQL="
drop database if exists ${BK_MYSQL_NAME};
drop database if exists ${BK_MYSQL_TEST_NAME};
create database ${BK_MYSQL_NAME} default character set utf8 collate utf8_general_ci;
"

if [ "$BK_MYSQL_PASSWORD" ]; then
  mysql -h"$BK_MYSQL_HOST" -P"$BK_MYSQL_PORT" -u"$BK_MYSQL_USER" -p"$BK_MYSQL_PASSWORD" -sNe "$CREATE_DB_SQL"
else
  # 没有密码时无需-p，防止回车阻塞
  mysql -h"$BK_MYSQL_HOST" -P"$BK_MYSQL_PORT" -u"$BK_MYSQL_USER" -sNe "$CREATE_DB_SQL"
fi

# 构建数据库表
python manage.py migrate
python manage.py createcachetable
