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

    dependencies = [
        ('workflow', '0012_auto_20190406_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                (
                    'updated_by',
                    models.CharField(max_length=64, null=True, verbose_name='\u4fee\u6539\u4eba', blank=True),
                ),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4', blank=True)),
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                ('name', models.CharField(max_length=128, verbose_name='\u6d41\u7a0b\u540d')),
                (
                    'desc',
                    models.CharField(
                        default='', max_length=255, null=True, verbose_name='\u6d41\u7a0b\u63cf\u8ff0', blank=True
                    ),
                ),
                (
                    'flow_type',
                    models.CharField(default='DEFAULT', max_length=64, verbose_name='\u6d41\u7a0b\u5206\u7c7b'),
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
                    'master',
                    jsonfield.fields.JSONField(
                        default=[], null=True, verbose_name='\u4e3b\u5206\u652f\u5217\u8868', blank=True
                    ),
                ),
                (
                    'extras',
                    jsonfield.fields.JSONField(
                        default={'biz_related': False, 'urgers_type': 'EMPTY', 'urgers': '', 'need_urge': False},
                        verbose_name='\u4e1a\u52a1\u914d\u7f6e',
                    ),
                ),
                ('version_number', models.CharField(default='0', max_length=64, verbose_name='\u7248\u672c\u53f7')),
                ('workflow_id', models.IntegerField(verbose_name='\u6d41\u7a0b\u6a21\u677fID')),
                (
                    'fields',
                    jsonfield.fields.JSONField(
                        default={}, null=True, verbose_name='\u5b57\u6bb5\u5feb\u7167\u5b57\u5178', blank=True
                    ),
                ),
                (
                    'states',
                    jsonfield.fields.JSONField(
                        default={}, null=True, verbose_name='\u72b6\u6001\u5feb\u7167\u5b57\u5178', blank=True
                    ),
                ),
                (
                    'transitions',
                    jsonfield.fields.JSONField(
                        default={}, null=True, verbose_name='\u6d41\u8f6c\u5feb\u7167\u5b57\u5178', blank=True
                    ),
                ),
                (
                    'version_message',
                    models.TextField(default='', null=True, verbose_name='\u7248\u672c\u4fe1\u606f', blank=True),
                ),
                (
                    'notify',
                    models.ManyToManyField(
                        help_text='\u53ef\u5173\u8054\u591a\u79cd\u901a\u77e5\u65b9\u5f0f', to='workflow.Notify'
                    ),
                ),
            ],
            options={'verbose_name': '\u6d41\u7a0b\u5feb\u7167', 'verbose_name_plural': '\u6d41\u7a0b\u5feb\u7167',},
        ),
        migrations.AlterModelOptions(
            name='workflow',
            options={
                'ordering': ('-id',),
                'verbose_name': '\u6d41\u7a0b\u6a21\u677f',
                'verbose_name_plural': '\u6d41\u7a0b\u6a21\u677f',
            },
        ),
        migrations.RemoveField(model_name='workflow', name='readonly_fields',),
        migrations.RemoveField(model_name='workflow', name='time_limit',),
        migrations.AddField(
            model_name='defaultfield',
            name='flow_type',
            field=models.CharField(default='DEFAULT', max_length=64, verbose_name='\u6d41\u7a0b\u5206\u7c7b'),
        ),
        migrations.AddField(
            model_name='workflow',
            name='extras',
            field=jsonfield.fields.JSONField(
                default={'biz_related': False, 'urgers_type': 'EMPTY', 'urgers': '', 'need_urge': False},
                verbose_name='\u4e1a\u52a1\u914d\u7f6e',
            ),
        ),
        migrations.AddField(
            model_name='workflow',
            name='flow_type',
            field=models.CharField(default='DEFAULT', max_length=64, verbose_name='\u6d41\u7a0b\u5206\u7c7b'),
        ),
        migrations.AddField(
            model_name='workflow',
            name='version_number',
            field=models.CharField(default='0', max_length=64, verbose_name='\u7248\u672c\u53f7'),
        ),
        migrations.AlterField(
            model_name='defaultfield',
            name='choice',
            field=jsonfield.fields.JSONField(default=[], verbose_name='\u9009\u9879'),
        ),
        migrations.AlterField(
            model_name='defaultfield',
            name='source_type',
            field=models.CharField(
                default='CUSTOM',
                max_length=32,
                verbose_name='\u6570\u636e\u6765\u6e90\u7c7b\u578b',
                choices=[
                    ('CUSTOM', '\u81ea\u5b9a\u4e49\u6570\u636e'),
                    ('API', '\u63a5\u53e3\u6570\u636e'),
                    ('DATADICT', '\u6570\u636e\u5b57\u5178'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='defaultfield',
            name='type',
            field=models.CharField(
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
                    ('CUSTOMTABLE', '\u81ea\u5b9a\u4e49\u8868\u683c'),
                    ('TREESELECT', '\u6811\u5f62\u9009\u62e9'),
                    ('CASCADE', '\u7ea7\u8054'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='choice',
            field=jsonfield.fields.JSONField(default=[], verbose_name='\u9009\u9879'),
        ),
        migrations.AlterField(
            model_name='field',
            name='source_type',
            field=models.CharField(
                default='CUSTOM',
                max_length=32,
                verbose_name='\u6570\u636e\u6765\u6e90\u7c7b\u578b',
                choices=[
                    ('CUSTOM', '\u81ea\u5b9a\u4e49\u6570\u636e'),
                    ('API', '\u63a5\u53e3\u6570\u636e'),
                    ('DATADICT', '\u6570\u636e\u5b57\u5178'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='state',
            field=models.ForeignKey(
                related_name='state_fields',
                blank=True,
                to='workflow.State',
                help_text='\u5173\u8054\u6d41\u7a0b',
                null=True,
                on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='type',
            field=models.CharField(
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
                    ('CUSTOMTABLE', '\u81ea\u5b9a\u4e49\u8868\u683c'),
                    ('TREESELECT', '\u6811\u5f62\u9009\u62e9'),
                    ('CASCADE', '\u7ea7\u8054'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='workflow',
            field=models.ForeignKey(
                related_name='fields', to='workflow.Workflow', help_text='\u5173\u8054\u6d41\u7a0b',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='state',
            name='followers_type',
            field=models.CharField(
                default='EMPTY',
                max_length=32,
                verbose_name='\u5173\u6ce8\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                choices=[
                    ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                    ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                    ('OPEN', '\u4e0d\u9650'),
                    ('PERSON', '\u4e2a\u4eba'),
                    ('STARTER', '\u63d0\u5355\u4eba'),
                    ('BY_ASSIGNOR', '\u6d3e\u5355\u4eba\u6307\u5b9a'),
                    ('EMPTY', '\u65e0'),
                    ('ORGANIZATION', '\u7ec4\u7ec7\u67b6\u6784'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='state',
            name='processors_type',
            field=models.CharField(
                default='OPEN',
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
                    ('ORGANIZATION', '\u7ec4\u7ec7\u67b6\u6784'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='state',
            name='workflow',
            field=models.ForeignKey(
                related_name='states', to='workflow.Workflow', help_text='\u5173\u8054\u6d41\u7a0b',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='transition',
            name='workflow',
            field=models.ForeignKey(
                related_name='transitions', to='workflow.Workflow', help_text='\u5173\u8054\u6d41\u7a0b',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='desc',
            field=models.CharField(
                default='', max_length=255, null=True, verbose_name='\u6d41\u7a0b\u63cf\u8ff0', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='service',
            field=models.CharField(
                default='default',
                max_length=64,
                null=True,
                verbose_name='\u5bf9\u5e94\u7684\u670d\u52a1\u7c7b\u578b\uff0c\u4e3a\u670d\u52a1\u7684\u4e3b\u952e',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='workflow',
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
                    ('ORGANIZATION', '\u7ec4\u7ec7\u67b6\u6784'),
                ],
            ),
        ),
    ]
