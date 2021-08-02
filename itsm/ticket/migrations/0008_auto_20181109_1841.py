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
        ('ticket', '0007_ticketcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketCommentInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numbers', models.CharField(default='', max_length=64, verbose_name='\u624b\u673a\u53f7\u7801')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u9080\u8bf7\u9014\u5f84\u8bb0\u5f55',
                'verbose_name_plural': '\u9080\u8bf7\u9014\u5f84\u8bb0\u5f55',
            },
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='source',
            field=models.CharField(
                default='SYS',
                max_length=64,
                verbose_name='\u8bc4\u4ef7\u6765\u6e90\uff08\u5de5\u5355\u9700\u6c42\u65b9\uff09',
                choices=[
                    ('WEB', '\u84dd\u9cb8\u5e73\u53f0'),
                    ('SMS', '\u77ed\u4fe1\u9080\u8bf7'),
                    ('SYS', '\u7cfb\u7edf\u81ea\u8bc4'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='ticket',
            field=models.OneToOneField(
                related_name='comments', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355', on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='ticketcommentinvite',
            name='comment',
            field=models.ForeignKey(
                related_name='comment', to='ticket.TicketComment', help_text='\u5173\u8054\u8bc4\u8bba',
                on_delete=models.CASCADE
            ),
        ),
    ]
