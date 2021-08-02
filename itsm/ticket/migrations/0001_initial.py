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

import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                ('sn', models.CharField(max_length=64, verbose_name='\u5355\u636e\u53f7', db_index=True)),
                ('title', models.CharField(max_length=64, verbose_name='\u5355\u636e\u540d\u79f0')),
                ('desc', models.CharField(max_length=255, verbose_name='\u63cf\u8ff0')),
                ('deadline', models.DateTimeField(null=True, verbose_name='\u622a\u6b62\u65f6\u95f4')),
                ('is_draft', models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e3a\u8349\u7a3f')),
                (
                    'workflow_snap_id',
                    models.IntegerField(default=0, verbose_name='\u5bf9\u5e94\u7684\u5feb\u7167\u4fe1\u606f'),
                ),
                (
                    'current_status',
                    models.CharField(
                        default='RUNNING',
                        max_length=32,
                        verbose_name='\u6d41\u8f6c\u7c7b\u578b',
                        choices=[('RUNNING', '\u5904\u7406\u4e2d'), ('FINISHED', '\u5df2\u7ed3\u675f')],
                    ),
                ),
                (
                    'current_processors_type',
                    models.CharField(
                        default='EMPTY',
                        max_length=32,
                        verbose_name='\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                        choices=[
                            ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                            ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                            ('OPEN', '\u4e0d\u9650'),
                            ('PERSON', '\u4e2a\u4eba'),
                        ],
                    ),
                ),
                (
                    'current_processors',
                    models.CharField(
                        default='',
                        max_length=255,
                        verbose_name="\u5904\u7406\u8005/\u89d2\u8272\u5217\u8868\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                    ),
                ),
                (
                    'current_state_id',
                    models.CharField(max_length=64, null=True, verbose_name='\u5f53\u524d\u72b6\u6001ID'),
                ),
                (
                    'service',
                    models.CharField(
                        default='custom', max_length=64, verbose_name='\u5bf9\u5e94\u670d\u52a1\u4e3b\u952e'
                    ),
                ),
                (
                    'service_property',
                    jsonfield.fields.JSONCharField(
                        default={}, max_length=255, verbose_name='\u4e1a\u52a1\u7279\u6027json\u5b57\u6bb5'
                    ),
                ),
            ],
            options={'ordering': ('-id',), 'verbose_name': '\u5de5\u5355', 'verbose_name_plural': '\u5de5\u5355',},
        ),
        migrations.CreateModel(
            name='TicketEventLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workflow_id', models.IntegerField(verbose_name='\u5de5\u4f5c\u6d41ID')),
                ('transition_id', models.IntegerField(verbose_name='\u6d41\u8f6cID')),
                ('from_state_id', models.IntegerField(verbose_name='\u5f53\u524d\u72b6\u6001ID')),
                ('to_state_id', models.IntegerField(verbose_name='\u4e0b\u4e00\u4e2a\u72b6\u6001ID')),
                (
                    'type',
                    models.CharField(
                        default='TRANSITION',
                        max_length=32,
                        verbose_name='\u6d41\u8f6c\u4e8b\u4ef6\u7c7b\u578b',
                        choices=[('TRANSITION', '\u6b63\u5e38\u6d41\u8f6c'), ('DELIVER', '\u8f6c\u5355\u6d41\u8f6c')],
                    ),
                ),
                (
                    'processors_type',
                    models.CharField(
                        default='OPEN',
                        max_length=32,
                        verbose_name='\u4e8b\u4ef6\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                        choices=[
                            ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                            ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                            ('OPEN', '\u4e0d\u9650'),
                            ('PERSON', '\u4e2a\u4eba'),
                        ],
                    ),
                ),
                (
                    'processors',
                    models.CharField(
                        default='',
                        max_length=255,
                        verbose_name="\u4e8b\u4ef6\u5904\u7406\u8005/\u89d2\u8272\u5217\u8868\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                    ),
                ),
                (
                    'form_data',
                    jsonfield.fields.JSONField(default={}, verbose_name='\u8868\u5355\u5feb\u7167\u5b57\u5178'),
                ),
                ('operator', models.CharField(max_length=64, verbose_name='\u64cd\u4f5c\u4eba')),
                ('operate_at', models.DateTimeField(auto_now_add=True, verbose_name='\u64cd\u4f5c\u65f6\u95f4')),
                ('message', models.CharField(max_length=1000, verbose_name='\u65e5\u5fd7\u6982\u8ff0')),
                (
                    'is_valid',
                    models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548\u6d41\u7a0b\u8282\u70b9'),
                ),
                (
                    'ticket',
                    models.ForeignKey(related_name='logs', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355',
                                      on_delete=models.CASCADE),
                ),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': '\u5355\u636e\u6d41\u8f6c\u65e5\u5fd7',
                'verbose_name_plural': '\u5355\u636e\u6d41\u8f6c\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='TicketField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                (
                    'is_builtin',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u662f\u5185\u7f6e\u5b57\u6bb5'),
                ),
                ('is_readonly', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53ea\u8bfb')),
                ('is_valid', models.BooleanField(default=True, verbose_name='\u662f\u5426\u751f\u6548')),
                (
                    'display',
                    models.BooleanField(
                        default=False, verbose_name='\u662f\u5426\u663e\u793a\u5728\u5355\u636e\u5217\u8868\u4e2d'
                    ),
                ),
                (
                    'source_type',
                    models.CharField(
                        default='CUSTOM',
                        max_length=32,
                        verbose_name='\u6570\u636e\u6765\u6e90\u7c7b\u578b',
                        choices=[('CUSTOM', '\u81ea\u5b9a\u4e49\u6570\u636e'), ('API', '\u63a5\u53e3\u6570\u636e')],
                    ),
                ),
                ('source_uri', models.CharField(default='', max_length=255, verbose_name='\u63a5\u53e3uri')),
                (
                    'type',
                    models.CharField(
                        default='STRING',
                        max_length=32,
                        verbose_name='\u5b57\u6bb5\u7c7b\u578b',
                        choices=[
                            ('STRING', '\u5355\u884c\u6587\u672c'),
                            ('TEXT', '\u591a\u884c\u6587\u672c'),
                            ('INT', '\u6570\u5b57'),
                            ('DATE', '\u65e5\u671f'),
                            ('DATETIME', '\u65f6\u95f4'),
                            ('DATETIMERANGE', '\u65f6\u95f4\u95f4\u9694'),
                            ('TABLE', '\u8868\u683c'),
                            ('SELECT', '\u5355\u9009\u4e0b\u62c9\u6846'),
                            ('MULTISELECT', '\u591a\u9009\u4e0b\u62c9\u6846'),
                            ('CHECKBOX', '\u590d\u9009\u6846'),
                            ('RADIO', '\u5355\u9009\u6846'),
                            ('MEMBERS', '\u591a\u9009\u4eba\u5458\u9009\u62e9'),
                            ('RICHTEXT', '\u5bcc\u6587\u672c'),
                            ('FILE', '\u9644\u4ef6\u4e0a\u4f20'),
                        ],
                    ),
                ),
                ('key', models.CharField(max_length=255, verbose_name='\u5b57\u6bb5\u6807\u8bc6')),
                ('name', models.CharField(max_length=64, verbose_name='\u5b57\u6bb5\u540d')),
                (
                    'layout',
                    models.CharField(
                        default='COL_6',
                        max_length=32,
                        verbose_name='\u5e03\u5c40',
                        choices=[('COL_6', '\u534a\u884c'), ('COL_12', '\u6574\u884c')],
                    ),
                ),
                (
                    'validate_type',
                    models.CharField(
                        default='REQUIRE',
                        max_length=32,
                        verbose_name='\u6821\u9a8c\u89c4\u5219',
                        choices=[('OPTION', '\u53ef\u9009'), ('REQUIRE', '\u5fc5\u586b')],
                    ),
                ),
                (
                    'regex',
                    models.CharField(default='', max_length=64, verbose_name='\u6b63\u5219\u6821\u9a8c\u89c4\u5219'),
                ),
                ('desc', models.CharField(default='', max_length=128, verbose_name='\u5b57\u6bb5\u63cf\u8ff0')),
                ('default', models.CharField(default='', max_length=10000, verbose_name='\u9ed8\u8ba4\u503c')),
                (
                    'choice',
                    jsonfield.fields.JSONField(
                        default=[],
                        help_text='\u5f53\u6570\u636e\u6765\u6e90\u662fAPI\u7684\u65f6\u5019\uff0c\u4e3aURL\u7684\u8bf7\u6c42\u94fe\u63a5',
                        verbose_name='\u9009\u9879',
                    ),
                ),
                ('related_fields', jsonfield.fields.JSONField(default=[], verbose_name='\u7ea7\u8054\u5b57\u6bb5')),
                (
                    'state_id',
                    models.CharField(default='', max_length=32, verbose_name='\u5bf9\u5e94\u7684\u72b6\u6001id'),
                ),
                ('_value', models.TextField(null=True, verbose_name='\u8868\u5355\u503c', blank=True)),
                (
                    'ticket',
                    models.ForeignKey(related_name='fields', to='ticket.Ticket', help_text='\u5173\u8054\u5de5\u5355',
                                      on_delete=models.CASCADE),
                ),
            ],
            options={
                'verbose_name': '\u8868\u5355\u5b57\u6bb5\u503c',
                'verbose_name_plural': '\u8868\u5355\u5b57\u6bb5\u503c',
            },
        ),
    ]
