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

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ticket', '0022_auto_20190220_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='bk_biz_id',
            field=models.IntegerField(default=-1, null=True, verbose_name='\u4e1a\u52a1id', blank=True),
        ),
        migrations.AddField(
            model_name='ticketeventlog',
            name='is_deleted',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
        ),
        migrations.AddField(
            model_name='ticketeventlog',
            name='processors_snap',
            field=models.CharField(
                default='', max_length=10000, null=True, verbose_name='\u5904\u7406\u4eba\u5feb\u7167', blank=True
            ),
        ),
    ]
