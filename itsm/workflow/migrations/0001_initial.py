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
            name='DefaultField',
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
                    'category',
                    models.CharField(
                        max_length=128,
                        verbose_name='\u5b57\u6bb5\u5f52\u7c7b\uff0c\u9762\u5411\u4e1a\u52a1\u903b\u8f91\uff0c\u6bd4\u5982\u670d\u52a1\u7c7b\u578b\uff08change|event\uff09',
                    ),
                ),
            ],
            options={
                'verbose_name': '\u5185\u7f6e\u5b57\u6bb5\u8868',
                'verbose_name_plural': '\u5185\u7f6e\u5b57\u6bb5\u8868',
            },
        ),
        migrations.CreateModel(
            name='Field',
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
            ],
            options={'verbose_name': '\u5b57\u6bb5\u8868', 'verbose_name_plural': '\u5b57\u6bb5\u8868',},
        ),
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'name',
                    models.CharField(unique=True, max_length=64, verbose_name='\u901a\u77e5\u65b9\u5f0f\u540d\u79f0'),
                ),
                (
                    'is_builtin',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3a\u7cfb\u7edf\u5185\u7f6e'),
                ),
                (
                    'type',
                    models.CharField(
                        default='EMAIL',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u6e20\u9053',
                        choices=[('WEIXIN', '\u5fae\u4fe1'), ('EMAIL', '\u90ae\u7bb1'), ('SMS', '\u77ed\u4fe1')],
                    ),
                ),
                (
                    'template',
                    models.TextField(
                        default='',
                        verbose_name='\u901a\u77e5\u6a21\u677f\uff1a\u53ef\u4f7f\u7528\u53d8\u91cf\u5982\u4e0b\uff1axxx\uff08TODO\uff09',
                    ),
                ),
            ],
            options={'verbose_name': '\u901a\u77e5\u65b9\u5f0f', 'verbose_name_plural': '\u901a\u77e5\u65b9\u5f0f',},
        ),
        migrations.CreateModel(
            name='State',
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
                ('name', models.CharField(max_length=64, verbose_name='\u72b6\u6001\u540d')),
                ('desc', models.CharField(default='', max_length=64, verbose_name='\u72b6\u6001\u63cf\u8ff0')),
                ('order', models.IntegerField(default=-1, verbose_name='\u4e3b\u6d41\u7a0b\u4e2d\u987a\u5e8f')),
                (
                    'type',
                    models.CharField(
                        default='NORMAL',
                        max_length=32,
                        verbose_name='\u72b6\u6001\u7c7b\u578b',
                        choices=[
                            ('START', '\u5f00\u59cb\u8282\u70b9(\u5706\u5f62)'),
                            ('NORMAL', '\u4e2d\u95f4\u8282\u70b9(\u77e9\u5f62)'),
                            ('ROUTER', '\u7f51\u5173\u8282\u70b9(\u83f1\u5f62)'),
                            ('END', '\u7ed3\u675f\u8282\u70b9(\u5706\u5f62)'),
                        ],
                    ),
                ),
                (
                    'processors_type',
                    models.CharField(
                        default='OPEN',
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
                    'processors',
                    models.CharField(
                        default='',
                        max_length=255,
                        verbose_name="\u5904\u7406\u8005/\u89d2\u8272\u5217\u8868\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                    ),
                ),
                (
                    'distribute_rule',
                    models.CharField(
                        default='ONE',
                        max_length=32,
                        verbose_name='\u8def\u7531\u89c4\u5219',
                        choices=[
                            ('ALL', '\u6267\u884c\u5168\u90e8\u5206\u652f'),
                            ('ONE', '\u6267\u884c\u5355\u4e2a\u5206\u652f'),
                            ('SOME', '\u90e8\u5206\u5206\u652f(\u5206\u652f\u6570>1)'),
                        ],
                    ),
                ),
                (
                    'distribute_keys',
                    jsonfield.fields.JSONCharField(
                        default=[], max_length=255, verbose_name='\u5206\u652f\u5173\u952e\u5b57'
                    ),
                ),
                (
                    'distribute_type',
                    models.CharField(
                        default='WAIT',
                        max_length=32,
                        verbose_name='\u5206\u914d\u65b9\u5f0f',
                        choices=[('AUTO', '\u81ea\u52a8\u5206\u914d'), ('WAIT', '\u7b49\u5f85\u5904\u7406')],
                    ),
                ),
                (
                    'notify_rule',
                    models.CharField(
                        default='NONE',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u89c4\u5219',
                        choices=[
                            ('NONE', '\u4e0d\u901a\u77e5'),
                            ('ONCE', '\u53d1\u9001\u4e00\u6b21'),
                            ('RETRY', '\u91cd\u8bd5\u53d1\u9001\uff0c\u76f4\u5230\u5904\u7406\u5b8c'),
                        ],
                    ),
                ),
                ('notify_freq', models.IntegerField(default=0, verbose_name='\u91cd\u8bd5\u95f4\u9694(s)')),
                (
                    'fields',
                    jsonfield.fields.JSONField(
                        default=[],
                        verbose_name='\u8868\u5355\u5b57\u6bb5(ID\u5217\u8868\uff0c\u6309\u987a\u5e8f\u6392\u5217)',
                    ),
                ),
                (
                    'extras',
                    jsonfield.fields.JSONCharField(
                        default={}, max_length=1000, verbose_name='\u989d\u5916\u4fe1\u606f'
                    ),
                ),
                ('is_draft', models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e3a\u8349\u7a3f')),
                (
                    'is_builtin',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3a\u7cfb\u7edf\u5185\u7f6e'),
                ),
                (
                    'notify',
                    models.ManyToManyField(
                        help_text='\u53ef\u5173\u8054\u591a\u79cd\u901a\u77e5\u65b9\u5f0f', to='workflow.Notify'
                    ),
                ),
            ],
            options={'verbose_name': '\u72b6\u6001', 'verbose_name_plural': '\u72b6\u6001',},
        ),
        migrations.CreateModel(
            name='Transition',
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
                ('name', models.CharField(max_length=64, verbose_name='\u6d41\u8f6c\u64cd\u4f5c')),
                (
                    'type',
                    models.CharField(
                        default='JOIN-NORMAL',
                        max_length=32,
                        verbose_name='\u6d41\u8f6c\u7c7b\u578b',
                        choices=[
                            ('JOIN-NORMAL', '\u666e\u901a\u6d41\u8f6c'),
                            ('JOIN-BRANCH', '\u5206\u652f\u6d41\u8f6c'),
                            ('JOIN-API', '\u81ea\u52a8API\u6d41\u8f6c'),
                        ],
                    ),
                ),
                (
                    'direction',
                    models.CharField(
                        default='FORWARD',
                        max_length=32,
                        verbose_name='\u6d41\u8f6c\u65b9\u5411',
                        choices=[('BACK', '\u5411\u540e'), ('FORWARD', '\u5411\u524d')],
                    ),
                ),
                (
                    'check_needed',
                    models.BooleanField(
                        default=True, verbose_name='\u662f\u5426\u9700\u8981\u6821\u9a8c\u8868\u5355\u5b8c\u6574\u6027'
                    ),
                ),
                (
                    'opt_needed',
                    models.BooleanField(default=True, verbose_name='\u662f\u5426\u9700\u8981\u6267\u884c\u64cd\u4f5c'),
                ),
                (
                    'is_builtin',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3a\u7cfb\u7edf\u5185\u7f6e'),
                ),
                (
                    'from_state',
                    models.ForeignKey(
                        related_name='transitions_from', to='workflow.State', help_text='\u6e90\u72b6\u6001ID',
                        on_delete=models.CASCADE
                    ),
                ),
                (
                    'to_state',
                    models.ForeignKey(
                        related_name='transitions_to', to='workflow.State', help_text='\u76ee\u6807\u72b6\u6001ID',
                        on_delete=models.CASCADE
                    ),
                ),
            ],
            options={'verbose_name': '\u72b6\u6001\u6d41\u8f6c', 'verbose_name_plural': '\u72b6\u6001\u6d41\u8f6c',},
        ),
        migrations.CreateModel(
            name='Workflow',
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
                ('name', models.CharField(max_length=128, verbose_name='\u6d41\u7a0b\u540d')),
                ('desc', models.CharField(max_length=255, verbose_name='\u6d41\u7a0b\u63cf\u8ff0')),
                (
                    'hidden_fields',
                    jsonfield.fields.JSONCharField(
                        default=[], max_length=10000, verbose_name='\u9690\u85cf\u5b57\u6bb5\u5217\u8868'
                    ),
                ),
                (
                    'readonly_fields',
                    jsonfield.fields.JSONCharField(
                        default=['service', 'service_property'],
                        max_length=255,
                        verbose_name='\u53ea\u8bfb\u5b57\u6bb5\u5217\u8868',
                    ),
                ),
                (
                    'is_enabled',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u542f\u7528'),
                ),
                ('is_draft', models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e3a\u8349\u7a3f')),
                (
                    'is_builtin',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3a\u7cfb\u7edf\u5185\u7f6e'),
                ),
                ('time_limit', models.IntegerField(default=0, verbose_name='\u5904\u7406\u65f6\u9650(s)')),
                (
                    'notify_rule',
                    models.CharField(
                        default='NONE',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u89c4\u5219',
                        choices=[
                            ('NONE', '\u4e0d\u901a\u77e5'),
                            ('ONCE', '\u53d1\u9001\u4e00\u6b21'),
                            ('RETRY', '\u91cd\u8bd5\u53d1\u9001\uff0c\u76f4\u5230\u5904\u7406\u5b8c'),
                        ],
                    ),
                ),
                ('notify_freq', models.IntegerField(default=0, verbose_name='\u91cd\u8bd5\u95f4\u9694(s)')),
                (
                    'service',
                    models.CharField(
                        max_length=64,
                        verbose_name='\u5bf9\u5e94\u7684\u670d\u52a1\u7c7b\u578b\uff0c\u4e3a\u670d\u52a1\u7684\u4e3b\u952e',
                    ),
                ),
                (
                    'service_property',
                    jsonfield.fields.JSONField(
                        default={},
                        verbose_name='\u5bf9\u5e94\u670d\u52a1\u7684\u5c5e\u6027\uff0c\u4e3ajson\u5b57\u6bb5',
                    ),
                ),
                (
                    'is_biz_needed',
                    models.BooleanField(default=False, verbose_name='\u662f\u5426\u7ed1\u5b9a\u4e1a\u52a1'),
                ),
                ('master', jsonfield.fields.JSONField(default=[], verbose_name='\u4e3b\u5206\u652f\u5217\u8868')),
                (
                    'notify',
                    models.ManyToManyField(
                        help_text='\u53ef\u5173\u8054\u591a\u79cd\u901a\u77e5\u65b9\u5f0f', to='workflow.Notify'
                    ),
                ),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': '\u5de5\u4f5c\u6d41',
                'verbose_name_plural': '\u5de5\u4f5c\u6d41',
            },
        ),
        migrations.CreateModel(
            name='WorkflowSnap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workflow_id', models.IntegerField(verbose_name='\u5de5\u4f5c\u6d41ID')),
                (
                    'snapshot_time',
                    models.DateTimeField(auto_now_add=True, verbose_name='\u5feb\u7167\u521b\u5efa\u65f6\u95f4'),
                ),
                ('fields', jsonfield.fields.JSONField(default={}, verbose_name='\u5b57\u6bb5\u5feb\u7167\u5b57\u5178')),
                ('states', jsonfield.fields.JSONField(default={}, verbose_name='\u72b6\u6001\u5feb\u7167\u5b57\u5178')),
                (
                    'transitions',
                    jsonfield.fields.JSONField(default={}, verbose_name='\u6d41\u8f6c\u5feb\u7167\u5b57\u5178'),
                ),
                ('master', jsonfield.fields.JSONField(default=[], verbose_name='\u4e3b\u5206\u652f\u5217\u8868')),
                (
                    'notify_rule',
                    models.CharField(
                        default='NONE',
                        max_length=32,
                        verbose_name='\u901a\u77e5\u89c4\u5219',
                        choices=[
                            ('NONE', '\u4e0d\u901a\u77e5'),
                            ('ONCE', '\u53d1\u9001\u4e00\u6b21'),
                            ('RETRY', '\u91cd\u8bd5\u53d1\u9001\uff0c\u76f4\u5230\u5904\u7406\u5b8c'),
                        ],
                    ),
                ),
                ('notify_freq', models.IntegerField(default=0, verbose_name='\u91cd\u8bd5\u95f4\u9694(s)')),
                (
                    'notify',
                    models.ManyToManyField(
                        help_text='\u53ef\u5173\u8054\u591a\u79cd\u901a\u77e5\u65b9\u5f0f', to='workflow.Notify'
                    ),
                ),
            ],
            options={
                'verbose_name': '\u5de5\u4f5c\u6d41\u5feb\u7167',
                'verbose_name_plural': '\u5de5\u4f5c\u6d41\u5feb\u7167',
            },
        ),
        migrations.AddField(
            model_name='transition',
            name='workflow',
            field=models.ForeignKey(
                related_name='transitions', to='workflow.Workflow', help_text='\u5173\u8054\u5de5\u4f5c\u6d41',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='state',
            name='workflow',
            field=models.ForeignKey(
                related_name='states', to='workflow.Workflow', help_text='\u5173\u8054\u5de5\u4f5c\u6d41',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='state',
            field=models.ForeignKey(
                related_name='states', to='workflow.State', help_text='\u5173\u8054\u5de5\u4f5c\u6d41', null=True,
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='workflow',
            field=models.ForeignKey(
                related_name='fields', to='workflow.Workflow', help_text='\u5173\u8054\u5de5\u4f5c\u6d41',
                on_delete=models.CASCADE
            ),
        ),
    ]
