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
        ('service', '0002_init_service_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyrecord',
            name='data',
            field=jsonfield.fields.JSONField(
                null=True, verbose_name='\u5bf9\u5e94\u5c5e\u6027\u5b57\u6bb5\u7684\u503c', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='propertyrecord',
            name='flows',
            field=jsonfield.fields.JSONField(
                default=[],
                null=True,
                verbose_name='\u5173\u8054\u4e86\u5bf9\u5e94\u5c5e\u6027\u7684workflow\u7684id\u96c6\u5408',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='propertyrecord',
            name='pk_value',
            field=models.CharField(
                default='',
                max_length=64,
                null=True,
                verbose_name='\u5bf9\u5e94\u7684\u4e3b\u952e\u540d\uff0c\u4e3a\u5c5e\u6027\u8bbe\u7f6e\u7684\u4e3b\u952e\u4fe1\u606f',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='propertyrecord',
            name='tickets',
            field=jsonfield.fields.JSONField(
                default=[],
                null=True,
                verbose_name='\u5173\u8054\u4e86\u5bf9\u5e94\u5c5e\u6027\u7684ticket\u7684id\u96c6\u5408',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='serviceproperty',
            name='fields',
            field=jsonfield.fields.JSONField(
                default=[], null=True, verbose_name='\u5c5e\u6027\u5305\u542b\u7684\u5b57\u6bb5', blank=True
            ),
        ),
    ]
