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
        ('ticket', '0006_ticketfield_custom_regex'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'stars',
                    models.IntegerField(verbose_name='\u8bc4\u4ef7\u7b49\u7ea71~5\uff0c5\u661f\u4e3a\u6700\u597d'),
                ),
                ('comments', models.TextField(null=True, verbose_name='\u8bc4\u4ef7\u4fe1\u606f', blank=True)),
                (
                    'source',
                    models.CharField(
                        max_length=64, verbose_name='\u8bc4\u4ef7\u6765\u6e90\uff08\u5de5\u5355\u9700\u6c42\u65b9\uff09'
                    ),
                ),
                (
                    'creator',
                    models.CharField(
                        max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba/\u63d0\u5355\u4eba', blank=True
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                (
                    'ticket',
                    models.ForeignKey(
                        related_name='comments', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355',
                        on_delete=models.CASCADE
                        
                    ),
                ),
            ],
            options={'verbose_name': '\u5de5\u5355\u8bc4\u4ef7', 'verbose_name_plural': '\u5de5\u5355\u8bc4\u4ef7',},
        ),
    ]
