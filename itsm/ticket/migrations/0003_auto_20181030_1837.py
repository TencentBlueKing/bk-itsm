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
        ('ticket', '0002_auto_20181024_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='creator',
            field=models.CharField(max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='current_processors',
            field=models.CharField(
                default='',
                max_length=255,
                null=True,
                verbose_name="\u5904\u7406\u8005/\u89d2\u8272\u5217\u8868\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='current_processors_type',
            field=models.CharField(
                default='EMPTY',
                max_length=32,
                verbose_name='\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                choices=[
                    ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                    ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                    ('OPEN', '\u4e0d\u9650'),
                    ('PERSON', '\u4e2a\u4eba'),
                    ('STARTER', '\u63d0\u5355\u4eba'),
                    ('EMPTY', '\u65e0'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='deadline',
            field=models.DateTimeField(null=True, verbose_name='\u622a\u6b62\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='end_at',
            field=models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='service_property',
            field=jsonfield.fields.JSONCharField(
                default={},
                max_length=255,
                null=True,
                verbose_name='\u4e1a\u52a1\u7279\u6027json\u5b57\u6bb5',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='updated_by',
            field=models.CharField(max_length=64, null=True, verbose_name='\u4fee\u6539\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='form_data',
            field=jsonfield.fields.JSONField(
                default={}, null=True, verbose_name='\u8868\u5355\u5feb\u7167\u5b57\u5178', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='message',
            field=models.CharField(max_length=1000, null=True, verbose_name='\u65e5\u5fd7\u6982\u8ff0', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='operator',
            field=models.CharField(max_length=64, null=True, verbose_name='\u64cd\u4f5c\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='processors',
            field=models.CharField(
                default='',
                max_length=255,
                null=True,
                verbose_name="\u4e8b\u4ef6\u5904\u7406\u8005/\u89d2\u8272\u5217\u8868\uff1a\u7a7a\u3001\u5355\u4eba(\u89d2\u8272)\u6216\u8005','\u9694\u5f00\u7684\u591a\u4eba(\u89d2\u8272)",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='ticketeventlog',
            name='processors_type',
            field=models.CharField(
                default='OPEN',
                max_length=32,
                verbose_name='\u4e8b\u4ef6\u5904\u7406\u8005\u7c7b\u578b/\u89d2\u8272\u7c7b\u578b',
                choices=[
                    ('CMDB', 'CMDB\u4e1a\u52a1\u516c\u7528\u89d2\u8272'),
                    ('GENERAL', '\u901a\u7528\u89d2\u8272\u8868'),
                    ('OPEN', '\u4e0d\u9650'),
                    ('PERSON', '\u4e2a\u4eba'),
                    ('STARTER', '\u63d0\u5355\u4eba'),
                    ('EMPTY', '\u65e0'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='creator',
            field=models.CharField(max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='default',
            field=models.CharField(
                default='', max_length=10000, null=True, verbose_name='\u9ed8\u8ba4\u503c', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='desc',
            field=models.CharField(
                default='', max_length=128, null=True, verbose_name='\u5b57\u6bb5\u63cf\u8ff0', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='end_at',
            field=models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='regex',
            field=models.CharField(
                default='', max_length=64, null=True, verbose_name='\u6b63\u5219\u6821\u9a8c\u89c4\u5219', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='related_fields',
            field=jsonfield.fields.JSONField(
                default=[], null=True, verbose_name='\u7ea7\u8054\u5b57\u6bb5', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='source_uri',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='\u63a5\u53e3uri', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='state_id',
            field=models.CharField(
                default='', max_length=32, null=True, verbose_name='\u5bf9\u5e94\u7684\u72b6\u6001id', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='ticketfield',
            name='updated_by',
            field=models.CharField(max_length=64, null=True, verbose_name='\u4fee\u6539\u4eba', blank=True),
        ),
    ]
