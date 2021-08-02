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
        ('role', '0002_init_role_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roletype',
            name='desc',
            field=models.CharField(default='', max_length=128, verbose_name='\u89d2\u8272\u63cf\u8ff0'),
        ),
        migrations.AlterField(
            model_name='roletype',
            name='name',
            field=models.CharField(max_length=64, verbose_name='\u89d2\u8272\u540d\u79f0'),
        ),
        migrations.AlterField(
            model_name='roletype',
            name='type',
            field=models.CharField(max_length=64, verbose_name='\u89d2\u8272\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='access',
            field=models.CharField(max_length=128, verbose_name='\u5bf9\u5e94\u670d\u52a1'),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(max_length=64, verbose_name='\u89d2\u8272\u547d\u540d'),
        ),
    ]
