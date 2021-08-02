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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

import datetime
import subprocess

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db import connection
from django.http import HttpResponse
from django.utils.translation import ugettext as _


@permission_required('is_superuser')
def dump_db(request):
    """
    dbdump操作
    """

    db = settings.DATABASES['default']
    dbfile = 'static/{}.sql'.format(db.get('NAME'))
    dumpcmd = 'mysqldump'
    dumpdb = (
        '{dumpcmd} --user={user} '
        '--password={password} '
        '--host={host} '
        '--port={port} '
        '--single-transaction '
        '{dbname} > {dbfile}'.format(
            dumpcmd=dumpcmd,
            user=db.get('USER'),
            password=db.get('PASSWORD'),
            host=db.get('HOST'),
            port=db.get('HOST'),
            dbname=db.get('NAME'),
            dbfile=dbfile,
        )
    )

    p = subprocess.Popen(dumpdb, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    try:
        with open(dbfile, 'rb') as fd:
            file_content = fd.read()
            response = HttpResponse(file_content)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="%s_%s.sql"' % (
                db.get('NAME'),
                datetime.datetime.now(),
            )
    except IOError:
        return HttpResponse(_('<h3>磁盘中不存在该文件!</h3>'))
    except Exception as e:
        return HttpResponse(_('<h3>系统异常!</h3><br><p>%s</p>') % e)
    return response


@permission_required('is_superuser')
def drop_table(request):
    """
    清空表，危险操作
    """

    try:
        cursor = connection.cursor()

        # 取消外键关联
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("show tables;")

        result_tuple = cursor.fetchall()
        for result in result_tuple:
            table_name = result[0]
            drop_table_sql = "drop table " + table_name  # +" if exists "+table_name
            cursor.execute(drop_table_sql)

        return HttpResponse(_('命令执行成功'))
    except Exception as e:
        return HttpResponse(_('命令执行异常:%s') % e)
