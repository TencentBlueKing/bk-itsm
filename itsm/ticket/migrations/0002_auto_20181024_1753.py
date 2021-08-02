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
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketeventlog',
            options={
                'ordering': ('id',),
                'verbose_name': '\u5355\u636e\u6d41\u8f6c\u65e5\u5fd7',
                'verbose_name_plural': '\u5355\u636e\u6d41\u8f6c\u65e5\u5fd7',
            },
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
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='current_status',
            field=models.CharField(
                default='RUNNING',
                max_length=32,
                verbose_name='\u6d41\u8f6c\u7c7b\u578b',
                choices=[
                    ('RUNNING', '\u5904\u7406\u4e2d'),
                    ('SUSPEND', '\u6302\u8d77'),
                    ('FINISHED', '\u5df2\u7ed3\u675f'),
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
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='type',
            field=models.CharField(
                default='TRANSITION',
                max_length=32,
                verbose_name='\u6d41\u8f6c\u4e8b\u4ef6\u7c7b\u578b',
                choices=[
                    ('TRANSITION', '\u6b63\u5e38\u6d41\u8f6c'),
                    ('DELIVER', '\u8f6c\u5355\u6d41\u8f6c'),
                    ('TERMINATE', '\u7ec8\u6b62\u6d41\u7a0b'),
                    ('SUSPEND', '\u6302\u8d77\u5355\u636e'),
                    ('UNSUSPEND', '\u89e3\u9664\u6302\u8d77'),
                    ('WITHDRAW', '\u64a4\u5355'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
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
                    ('CASCADE', '\u7ea7\u8054'),
                ],
            ),
        ),
    ]
