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
        ('ticket', '0019_auto_20181227_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketFollowerNotifyLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state_id', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u8282\u70b9ID')),
                (
                    'state_name',
                    models.CharField(
                        default='', max_length=64, null=True, verbose_name='\u8282\u70b9\u540d\u79f0', blank=True
                    ),
                ),
                (
                    'creator',
                    models.CharField(
                        default='', max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                (
                    'message',
                    models.TextField(default='', null=True, verbose_name='\u901a\u77e5\u4fe1\u606f', blank=True),
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
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                (
                    'followers',
                    models.CharField(
                        default='', max_length=255, null=True, verbose_name='\u5173\u6ce8\u4eba', blank=True
                    ),
                ),
                (
                    'followers_type',
                    models.CharField(
                        default='EMPTY',
                        max_length=32,
                        verbose_name='\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                        choices=[
                            ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                            ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                            ('OPEN', '\u4e0d\u9650'),
                            ('PERSON', '\u4e2a\u4eba'),
                            ('STARTER', '\u63d0\u5355\u4eba'),
                            ('BY_ASSIGNOR', '\u6d3e\u5355\u4eba\u6307\u5b9a'),
                            ('EMPTY', '\u65e0'),
                        ],
                    ),
                ),
                (
                    'ticket_token',
                    models.CharField(
                        null=True,
                        default='',
                        max_length=10,
                        blank=True,
                        unique=True,
                        verbose_name='\u5173\u6ce8\u94fe\u63a5\u53ea\u8bfb\u6807\u8bc6',
                    ),
                ),
                (
                    'is_sys_sended',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u7cfb\u7edf\u6d41\u7a0b\u53d1\u9001'),
                ),
            ],
            options={
                'verbose_name': '\u5173\u6ce8\u4eba\u901a\u77e5\u65e5\u5fd7',
                'verbose_name_plural': '\u5173\u6ce8\u4eba\u901a\u77e5\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='TicketSuperviseNotifyLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state_id', models.IntegerField(default=0, verbose_name='\u53d1\u9001\u8282\u70b9ID')),
                (
                    'state_name',
                    models.CharField(
                        default='', max_length=64, null=True, verbose_name='\u8282\u70b9\u540d\u79f0', blank=True
                    ),
                ),
                (
                    'creator',
                    models.CharField(
                        default='', max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                (
                    'message',
                    models.TextField(default='', null=True, verbose_name='\u901a\u77e5\u4fe1\u606f', blank=True),
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
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                (
                    'supervised',
                    models.CharField(
                        default='', max_length=255, null=True, verbose_name='\u88ab\u7763\u529e\u7684\u4eba', blank=True
                    ),
                ),
            ],
            options={'verbose_name': '\u7763\u529e\u65e5\u5fd7', 'verbose_name_plural': '\u7763\u529e\u65e5\u5fd7',},
        ),
        migrations.AddField(
            model_name='ticket',
            name='is_supervise_needed',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u9700\u8981\u7763\u529e'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='supervise_type',
            field=models.CharField(
                default='EMPTY',
                max_length=32,
                verbose_name='\u7763\u529e\u4eba\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                choices=[
                    ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                    ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                    ('OPEN', '\u4e0d\u9650'),
                    ('PERSON', '\u4e2a\u4eba'),
                    ('STARTER', '\u63d0\u5355\u4eba'),
                    ('BY_ASSIGNOR', '\u6d3e\u5355\u4eba\u6307\u5b9a'),
                    ('EMPTY', '\u65e0'),
                ],
            ),
        ),
        migrations.AddField(
            model_name='ticket',
            name='supervisor',
            field=models.CharField(
                default='',
                max_length=255,
                null=True,
                verbose_name="\u7763\u529e\u4eba\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='ticketsupervisenotifylog',
            name='ticket',
            field=models.ForeignKey(
                related_name='supervise_notify_logs', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='ticketfollowernotifylog',
            name='ticket',
            field=models.ForeignKey(
                related_name='follower_notify_logs', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355',
                on_delete=models.CASCADE
            ),
        ),
    ]
