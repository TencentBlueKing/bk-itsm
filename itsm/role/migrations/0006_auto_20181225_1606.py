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
        ('role', '0005_auto_20181030_1837'),
    ]

    operations = [
        migrations.RenameField(model_name='userrole', old_name='desc', new_name='role_key',),
        migrations.AddField(
            model_name='userrole',
            name='desc',
            field=models.CharField(
                default='', max_length=128, null=True, verbose_name='\u7528\u6237\u89d2\u8272\u63cf\u8ff0', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='role_key',
            field=models.CharField(default='', max_length=128, verbose_name='\u89d2\u8272\u552f\u4e00\u6807\u8bc6'),
        ),
    ]
