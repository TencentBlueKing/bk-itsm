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
        ('workflow', '0009_auto_20181206_1131'),
    ]

    operations = [
        migrations.RemoveField(model_name='workflow', name='hidden_fields',),
        migrations.AddField(
            model_name='workflow',
            name='is_supervise_needed',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u9700\u8981\u7763\u529e'),
        ),
        migrations.AddField(
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
                ],
            ),
        ),
        migrations.AddField(
            model_name='workflow',
            name='supervisor',
            field=models.CharField(
                default='',
                max_length=255,
                null=True,
                verbose_name="\u7763\u529e\u4eba\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                blank=True,
            ),
        ),
    ]
