# -*- coding: utf-8 -*-
import datetime

from django.apps import AppConfig
from django.conf import settings
from django.db import connection

from common.log import logger


class HelperConfig(AppConfig):
    name = "itsm.helper"

    def is_before_2_6_0(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT `app`, `name` FROM django_migrations where app="account" and name="0002_smart_initial";'
                )
                rows = cursor.fetchall()
                if len(rows) > 0:
                    return True

        except Exception:
            print("This is the first deployment")
            return False

        return False

    def ready(self):
        """
        blueapps的数据升级
        """
        if not self.is_before_2_6_0():
            print("发现非2.6.0 之前的升级版本，已跳过修复")
            return

        migrations = (
            ("account", "0002_init_superuser"),
            ("account", "0003_verifyinfo"),
        )

        print("fix_for_blueapps_after_2_6_0 start")

        if settings.RUN_VER != "open":
            logger.Exception(
                "当前运行环境为:{}，不支持db_fix_for_blueapps_after_2_6_0方法".format(
                    settings.RUN_VER
                )
            )
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT `app`, `name` FROM django_migrations;")
                rows = cursor.fetchall()

                if len(rows) == 0:
                    # 如果没有记录，说明是全新部署，则不插入
                    return

                for migration in migrations:
                    if migration in rows:
                        print("记录已存在, 跳过部署{}".format(migration))
                        continue
                    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    cursor.execute(
                        'INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES ("{}", "{}", "{}");'.format(
                            migration[0], migration[1], dt
                        )
                    )
        except BaseException as err:
            logger.info("fix_for_blueapps_after_2_6_0 error = {}".format(str(err)))

        print("fix_for_blueapps_after_2_6_0 end")
