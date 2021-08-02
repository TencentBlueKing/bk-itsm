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
        ('ticket', '0010_auto_20181113_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='current_status',
            field=models.CharField(
                default='RUNNING',
                max_length=32,
                verbose_name='\u6d41\u8f6c\u7c7b\u578b',
                choices=[
                    ('RUNNING', '\u5904\u7406\u4e2d'),
                    ('SUSPEND', '\u6302\u8d77'),
                    ('RECEIVING', '\u5f85\u8ba4\u9886'),
                    ('DISTRIBUTING', '\u5f85\u5206\u914d'),
                    ('FINISHED', '\u5df2\u7ed3\u675f'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='type',
            field=models.CharField(
                default='TRANSITION',
                max_length=32,
                verbose_name='\u6d41\u8f6c\u4e8b\u4ef6\u7c7b\u578b',
                choices=[
                    ('TRANSITION', '\u6b63\u5e38\u6d41\u8f6c'),
                    ('DELIVER', '\u8f6c\u5355\u6d41\u8f6c'),
                    ('TERMINATE', '\u7ec8\u6b62\u6d41\u7a0b'),
                    ('SUSPEND', '\u6302\u8d77\u5355\u636e'),
                    ('UNSUSPEND', '\u89e3\u9664\u6302\u8d77'),
                    ('WITHDRAW', '\u64a4\u5355'),
                    ('CLAIM', '\u8ba4\u9886\u5de5\u5355'),
                    ('DISTRIBUTE', '\u5206\u6d3e\u5de5\u5355'),
                ],
            ),
        ),
    ]
