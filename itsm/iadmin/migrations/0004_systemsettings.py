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

from itsm.iadmin.models import SystemSettings


class Migration(migrations.Migration):
    dependencies = [
        ('iadmin', '0003_auto_20190114_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('type', models.CharField(max_length=64, verbose_name='\u7c7b\u578b')),
                ('key', models.CharField(max_length=64, verbose_name='\u5173\u952e\u5b57\u552f\u4e00\u6807\u8bc6')),
                (
                    'value',
                    models.TextField(default='', null=True, verbose_name='\u7cfb\u7edf\u8bbe\u7f6e\u503c', blank=True),
                ),
            ],
            options={'verbose_name': '\u7cfb\u7edf\u8bbe\u7f6e', 'verbose_name_plural': '\u7cfb\u7edf\u8bbe\u7f6e',},
        ),
        migrations.RunPython(SystemSettings.init_default_settings),
    ]
