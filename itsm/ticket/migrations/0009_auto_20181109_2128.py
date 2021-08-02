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
        ('ticket', '0008_auto_20181109_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketcomment',
            name='comments',
            field=models.CharField(max_length=255, null=True, verbose_name='\u8bc4\u4ef7\u4fe1\u606f', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='creator',
            field=models.CharField(max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='source',
            field=models.CharField(
                default='SYS',
                max_length=64,
                verbose_name='\u8bc4\u4ef7\u6765\u6e90',
                choices=[
                    ('WEB', '\u84dd\u9cb8\u5e73\u53f0'),
                    ('SMS', '\u77ed\u4fe1\u9080\u8bf7'),
                    ('SYS', '\u7cfb\u7edf\u81ea\u8bc4'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='stars',
            field=models.IntegerField(
                default=0, verbose_name='\u8bc4\u4ef7\u7b49\u7ea71~5\uff0c5\u661f\u4e3a\u6700\u597d'
            ),
        ),
    ]
