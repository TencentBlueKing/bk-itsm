# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import os
import json
import codecs

from django.db import migrations


def add_common_actions(apps, schema_editor):
    """
    添加常用的操作动作
    """

    from iam.contrib.iam_migration.utils import do_migrate
    from iam.contrib.iam_migration import exceptions
    from django.conf import settings

    iam_host = settings.BK_IAM_INNER_HOST
    app_code = settings.APP_CODE
    app_secret = settings.SECRET_KEY

    json_path = getattr(settings, "BK_IAM_MIGRATION_JSON_PATH", "support-files/iam/")
    file_path = os.path.join(settings.BASE_DIR, json_path, "initial_common_actions.json")

    with codecs.open(file_path, mode="r", encoding="utf-8") as fp:
        data = json.load(fp=fp)

    ok, _ = do_migrate.api_ping(iam_host)
    if not ok:
        raise exceptions.NetworkUnreachableError("bk iam ping error")

    client = do_migrate.Client(app_code, app_secret, iam_host)

    ok, message = client.batch_update_common_actions(settings.BK_IAM_SYSTEM_ID, data)
    if not ok:
        raise exceptions.MigrationFailError("iam migrate fail %s" % message)


class Migration(migrations.Migration):
    dependencies = [
        ('auth_iam', '0001_initial'),
        ('iam_migration', '0006_update'),
    ]

    operations = [migrations.RunPython(add_common_actions)]
