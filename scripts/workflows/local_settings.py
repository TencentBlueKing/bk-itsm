# -*- coding: utf-8 -*-
import os

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        # 新版插件管理数据库
        "NAME": os.getenv("BK_MYSQL_NAME"),  # 数据库名
        "USER": os.getenv("BK_MYSQL_USER"),
        "PASSWORD": os.getenv("BK_MYSQL_PASSWORD"),
        "HOST": os.getenv("BK_MYSQL_HOST"),
        "PORT": os.getenv("BK_MYSQL_PORT"),
        "OPTIONS": {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            "charset": "utf8mb4",
        },
        "COLLATION": "utf8mb4_general_ci",
        "TEST": {
            "NAME": os.getenv("BK_MYSQL_TEST_NAME"),
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_general_ci",
        },
    },
}

# 本地开发无需权限中心
BK_IAM_SKIP = True
USE_IAM = True if os.getenv("USE_IAM", "false").lower() == "true" else False
if not USE_IAM:
    BK_IAM_SKIP = True

DEBUG = True
