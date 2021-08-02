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
        ('ticket', '0017_fix_deal_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketStateDraft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('ticket_id', models.IntegerField(verbose_name='\u5355\u636eid')),
                ('state_id', models.IntegerField(verbose_name='\u8282\u70b9id')),
                (
                    'draft',
                    jsonfield.fields.JSONCharField(
                        default=[],
                        max_length=10000,
                        null=True,
                        verbose_name='\u5355\u636e\u59d0\u6b38\u6309\u8349\u7a3f\u5b57\u6bb5',
                        blank=True,
                    ),
                ),
            ],
            options={
                'verbose_name': '\u5355\u636e\u8282\u70b9\u8349\u7a3f',
                'verbose_name_plural': '\u5355\u636e\u8282\u70b9\u8349\u7a3f',
            },
        ),
        migrations.AlterField(
            model_name='ticket',
            name='current_assignor_type',
            field=models.CharField(
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
        migrations.AlterField(
            model_name='ticket',
            name='current_processors_type',
            field=models.CharField(
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
        migrations.AlterField(
            model_name='ticketeventlog',
            name='processors_type',
            field=models.CharField(
                default='OPEN',
                max_length=32,
                verbose_name='\u4e8b\u4ef6\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
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
    ]
