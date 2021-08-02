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

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PropertyRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                ('key', models.CharField(max_length=255, verbose_name='\u5bf9\u5e94\u7684\u552f\u4e00\u5c5e\u6027key')),
                (
                    'pk_value',
                    models.CharField(
                        default='',
                        max_length=64,
                        verbose_name='\u5bf9\u5e94\u7684\u4e3b\u952e\u540d\uff0c\u4e3a\u5c5e\u6027\u8bbe\u7f6e\u7684\u4e3b\u952e\u4fe1\u606f',
                    ),
                ),
                (
                    'flows',
                    jsonfield.fields.JSONField(
                        default=[],
                        verbose_name='\u5173\u8054\u4e86\u5bf9\u5e94\u5c5e\u6027\u7684workflow\u7684id\u96c6\u5408',
                    ),
                ),
                (
                    'tickets',
                    jsonfield.fields.JSONField(
                        default=[],
                        verbose_name='\u5173\u8054\u4e86\u5bf9\u5e94\u5c5e\u6027\u7684ticket\u7684id\u96c6\u5408',
                    ),
                ),
                ('data', jsonfield.fields.JSONField(verbose_name='\u5bf9\u5e94\u5c5e\u6027\u5b57\u6bb5\u7684\u503c')),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': '\u670d\u52a1\u5c5e\u6027\u8bb0\u5f55',
                'verbose_name_plural': '\u670d\u52a1\u5c5e\u6027\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                (
                    'key',
                    models.CharField(
                        unique=True,
                        max_length=45,
                        verbose_name='\u9ed8\u8ba4\u4e3a\u540d\u79f0\u62fc\u97f3\uff0c\u552f\u4e00\u5b58\u5728\uff0c\u5982\u679c\u6709\u4e00\u6837\u7684\uff0c\u5219\u901a\u8fc7\u968f\u673a\u5b57\u7b26\u5339\u914d',
                    ),
                ),
                ('name', models.CharField(default='', max_length=255, verbose_name='\u670d\u52a1\u540d\u79f0')),
                ('desc', models.CharField(max_length=255, verbose_name='\u670d\u52a1\u63cf\u8ff0')),
            ],
            options={'verbose_name': '\u670d\u52a1\u7c7b\u578b', 'verbose_name_plural': '\u670d\u52a1\u7c7b\u578b',},
        ),
        migrations.CreateModel(
            name='ServiceProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                (
                    'key',
                    models.CharField(
                        max_length=32,
                        verbose_name='\u9ed8\u8ba4\u4e3a\u540d\u79f0\u62fc\u97f3\uff0c\u552f\u4e00\u5b58\u5728\uff0c\u5982\u679c\u6709\u4e00\u6837\u7684\uff0c\u5219\u901a\u8fc7\u62fc\u97f3+\u968f\u673a\u5b57\u7b26\u5339\u914d',
                    ),
                ),
                (
                    'is_cascade',
                    models.BooleanField(
                        default=False, verbose_name='\u5224\u65ad\u662f\u5426\u4e3a\u7ea7\u8054\u5c5e\u6027'
                    ),
                ),
                (
                    'name',
                    models.CharField(default='', max_length=255, verbose_name='\u670d\u52a1\u5c5e\u6027\u540d\u79f0'),
                ),
                ('desc', models.CharField(max_length=255, verbose_name='\u5c5e\u6027\u63cf\u8ff0')),
                (
                    'fields',
                    jsonfield.fields.JSONField(default=[], verbose_name='\u5c5e\u6027\u5305\u542b\u7684\u5b57\u6bb5'),
                ),
                (
                    'service_category',
                    models.ForeignKey(
                        related_name='properties',
                        to='service.ServiceCategory',
                        help_text='\u5173\u8054\u670d\u52a1\u7c7b\u522b',
                        on_delete=models.CASCADE
                    ),
                ),
            ],
            options={'verbose_name': '\u670d\u52a1\u5c5e\u6027', 'verbose_name_plural': '\u670d\u52a1\u5c5e\u6027',},
        ),
        migrations.AddField(
            model_name='propertyrecord',
            name='service_property',
            field=models.ForeignKey(
                related_name='records', to='service.ServiceProperty', help_text='\u5173\u8054\u670d\u52a1\u5c5e\u6027',
                on_delete=models.CASCADE
            ),
        ),
    ]
