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

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CustomNotice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'title_template',
                    models.CharField(
                        default='',
                        max_length=255,
                        blank=True,
                        help_text='\u5de5\u5355\u5b57\u6bb5\u7684\u503c\u53ef\u4ee5\u4f5c\u4e3a\u53c2\u6570\u5199\u5230\u6a21\u677f\u4e2d\uff0c\u683c\u5f0f\u5982\uff1a\u3010ITSM\u3011{service}\u7ba1\u7406\u5355\u3010{action}\u3011\u63d0\u9192,service\u4e3a\u670d\u52a1key\u503c',
                        null=True,
                        verbose_name='\u6807\u9898\u6a21\u677f',
                    ),
                ),
                (
                    'content_template',
                    models.TextField(
                        default='',
                        help_text='\u5de5\u5355\u5b57\u6bb5\u7684\u503c\u53ef\u4ee5\u4f5c\u4e3a\u53c2\u6570\u5199\u5230\u6a21\u677f\u4e2d\uff0c\u683c\u5f0f\u5982\uff1a\u6807\u9898:{title}\uff0ctitle\u4e3a\u5b57\u6bb5\u7684key\u503c',
                        null=True,
                        verbose_name='\u5185\u5bb9\u6a21\u677f',
                        blank=True,
                    ),
                ),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                (
                    'type',
                    models.CharField(
                        default='default',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u7c7b\u578b',
                        choices=[
                            ('change', '\u53d8\u66f4\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                            ('event', '\u4e8b\u4ef6\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                            ('request', '\u8bf7\u6c42\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                            ('question', '\u95ee\u9898\u7ba1\u7406\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                            ('terminable', '\u7ec8\u6b62\u5355\u636e\u901a\u77e5\u6a21\u677f'),
                            ('follow', '\u5173\u6ce8\u4eba\u901a\u77e5\u6a21\u677f'),
                            ('invite', '\u9080\u8bf7\u8bc4\u4ef7'),
                            ('default', '\u9ed8\u8ba4\u901a\u77e5\u6a21\u677f'),
                        ],
                    ),
                ),
                (
                    'notify_type',
                    models.CharField(
                        default='EMAIL',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u65b9\u5f0f',
                        choices=[('WEIXIN', '\u5fae\u4fe1'), ('EMAIL', '\u90ae\u7bb1'), ('SMS', '\u77ed\u4fe1')],
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
            options={'verbose_name': '\u901a\u77e5\u6a21\u677f', 'verbose_name_plural': '\u901a\u77e5\u6a21\u677f',},
        ),
    ]
