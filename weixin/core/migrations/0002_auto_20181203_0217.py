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
        ('weixin_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bkweixinuser',
            name='email',
            field=models.CharField(
                max_length=128,
                verbose_name='\u90ae\u7bb1',
                blank=True),
        ),
        migrations.AddField(
            model_name='bkweixinuser',
            name='mobile',
            field=models.CharField(
                max_length=11,
                verbose_name='\u624b\u673a\u53f7',
                blank=True),
        ),
        migrations.AddField(
            model_name='bkweixinuser',
            name='qr_code',
            field=models.CharField(
                max_length=128,
                verbose_name='\u4e8c\u7ef4\u7801\u94fe\u63a5',
                blank=True),
        ),
        migrations.AddField(
            model_name='bkweixinuser',
            name='userid',
            field=models.CharField(
                max_length=128,
                null=True,
                verbose_name='\u4f01\u4e1a\u5fae\u4fe1\u7528\u6237\u5e94\u7528\u552f\u4e00\u6807\u8bc6'),
        ),
        migrations.AlterField(
            model_name='bkweixinuser',
            name='openid',
            field=models.CharField(
                max_length=128,
                null=True,
                verbose_name='\u5fae\u4fe1\u7528\u6237\u5e94\u7528\u552f\u4e00\u6807\u8bc6'),
        ),
        migrations.AlterUniqueTogether(
            name='bkweixinuser',
            unique_together=set([('openid', 'userid')]),
        ),
    ]
