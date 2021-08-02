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

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BkWeixinUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('openid', models.CharField(unique=True, max_length=128,
                                            verbose_name='\u5fae\u4fe1\u7528\u6237\u5e94\u7528\u552f\u4e00\u6807\u8bc6')),
                ('nickname', models.CharField(max_length=127,
                                              verbose_name='\u6635\u79f0', blank=True)),
                ('gender', models.CharField(max_length=15,
                                            verbose_name='\u6027\u522b', blank=True)),
                ('country', models.CharField(max_length=63,
                                             verbose_name='\u56fd\u5bb6', blank=True)),
                ('province', models.CharField(max_length=63,
                                              verbose_name='\u7701\u4efd', blank=True)),
                ('city', models.CharField(max_length=63,
                                          verbose_name='\u57ce\u5e02', blank=True)),
                ('avatar_url', models.CharField(max_length=255,
                                                verbose_name='\u5934\u50cf', blank=True)),
                ('date_joined',
                 models.DateTimeField(default=django.utils.timezone.now,
                                      verbose_name='\u52a0\u5165\u65f6\u95f4')),
            ],
            options={
                'db_table': 'bk_weixin_user',
                'verbose_name': '\u5fae\u4fe1\u7528\u6237',
                'verbose_name_plural': '\u5fae\u4fe1\u7528\u6237',
            },
        ),
    ]
