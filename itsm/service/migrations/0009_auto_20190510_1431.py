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
        ('service', '0008_auto_20190429_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='display_role',
            field=models.CharField(
                default='', max_length=255, null=True, verbose_name='\u53ef\u89c1\u8303\u56f4', blank=True
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='display_type',
            field=models.CharField(
                default='OPEN',
                max_length=32,
                verbose_name='\u53ef\u89c1\u8303\u56f4\u7c7b\u578b',
                choices=[
                    ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                    ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                    ('OPEN', '\u4e0d\u9650'),
                    ('PERSON', '\u4e2a\u4eba'),
                    ('ORGANIZATION', '\u7ec4\u7ec7\u67b6\u6784'),
                ],
            ),
        ),
        migrations.AddField(
            model_name='servicecatalog',
            name='xt_only',
            field=models.BooleanField(default=False, verbose_name='\u7279\u6b8a\u8fc7\u6ee4'),
        ),
    ]
