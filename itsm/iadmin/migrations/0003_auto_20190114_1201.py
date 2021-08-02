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
        ('iadmin', '0002_auto_20181214_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='customnotice',
            name='service',
            field=models.CharField(
                default='', max_length=32, null=True, verbose_name='\u5de5\u5355\u7c7b\u578b', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='customnotice',
            name='content_template',
            field=models.TextField(
                default='',
                help_text='\u5de5\u5355\u5b57\u6bb5\u7684\u503c\u53ef\u4ee5\u4f5c\u4e3a\u53c2\u6570\u5199\u5230\u6a21\u677f\u4e2d\uff0c\u683c\u5f0f\u5982\uff1a\u5355\u53f7:${sn}',
                null=True,
                verbose_name='\u5185\u5bb9\u6a21\u677f',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='customnotice',
            name='title_template',
            field=models.CharField(
                default='',
                max_length=255,
                blank=True,
                help_text='\u5de5\u5355\u5b57\u6bb5\u7684\u503c\u53ef\u4ee5\u4f5c\u4e3a\u53c2\u6570\u5199\u5230\u6a21\u677f\u4e2d\uff0c\u683c\u5f0f\u5982\uff1a\u3010ITSM\u3011${service}\u7ba1\u7406\u5355\u3010${action}\u3011\u63d0\u9192',
                null=True,
                verbose_name='\u6807\u9898\u6a21\u677f',
            ),
        ),
        migrations.AlterField(
            model_name='customnotice',
            name='type',
            field=models.CharField(
                default='default',
                max_length=32,
                verbose_name='\u901a\u77e5\u7c7b\u578b',
                choices=[
                    ('change', '\u53d8\u66f4\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                    ('event', '\u4e8b\u4ef6\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                    ('request', '\u8bf7\u6c42\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                    ('question', '\u95ee\u9898\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                    ('terminate', '\u7ec8\u6b62\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                    ('follow', '\u5173\u6ce8\u4eba\u901a\u77e5\u6a21\u677f'),
                    ('invite', '\u9080\u8bf7\u8bc4\u4ef7'),
                    ('supervise', '\u7763\u529e\u6a21\u677f'),
                    ('suspend', '\u6302\u8d77\u6a21\u677f'),
                    ('unsuspend', '\u6062\u590d\u6302\u8d77\u6a21\u677f'),
                    ('default', '\u9ed8\u8ba4\u901a\u77e5\u6a21\u677f'),
                ],
            ),
        ),
    ]
