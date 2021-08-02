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

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RoleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('name', models.CharField(max_length=64, verbose_name='\u89d2\u8272\u7684\u540d\u79f0')),
                ('type', models.CharField(max_length=64, verbose_name='\u89d2\u8272\u7684\u7c7b\u578b')),
                (
                    'is_processor',
                    models.BooleanField(default=True, verbose_name='\u53ef\u5426\u64cd\u4f5c\u5355\u636e'),
                ),
                ('is_display', models.BooleanField(default=True, verbose_name='\u662f\u5426\u663e\u793a')),
                ('desc', models.CharField(default='', max_length=128, verbose_name='\u89d2\u8272\u7684\u63cf\u8ff0')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u89d2\u8272\u7c7b\u578b',
                'verbose_name_plural': '\u7528\u6237\u89d2\u8272\u7c7b\u578b',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('role_type', models.CharField(max_length=64, verbose_name='\u5bf9\u5e94\u89d2\u8272\u7c7b\u578b')),
                ('name', models.CharField(max_length=64, verbose_name='\u89d2\u8272\u7684\u547d\u540d')),
                ('members', models.CharField(max_length=128, verbose_name='\u89d2\u8272\u7ec4\u6210\u4eba\u5458')),
                ('access', models.CharField(max_length=128, verbose_name='\u5bf9\u5e94\u7684\u670d\u52a1')),
                ('desc', models.CharField(max_length=128, verbose_name='\u8bf4\u660e')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u89d2\u8272\u548c\u6743\u9650\u8868',
                'verbose_name_plural': '\u7528\u6237\u89d2\u8272\u548c\u6743\u9650\u8868',
            },
        ),
    ]
