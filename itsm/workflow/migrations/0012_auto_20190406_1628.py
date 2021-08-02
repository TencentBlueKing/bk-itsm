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
        ('workflow', '0011_init_builtin_workflow_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultfield',
            name='meta',
            field=jsonfield.fields.JSONField(default={}, verbose_name='\u590d\u6742\u63cf\u8ff0\u4fe1\u606f'),
        ),
        migrations.AddField(
            model_name='field',
            name='meta',
            field=jsonfield.fields.JSONField(default={}, verbose_name='\u590d\u6742\u63cf\u8ff0\u4fe1\u606f'),
        ),
        migrations.AlterField(
            model_name='defaultfield',
            name='type',
            field=models.CharField(
                default='STRING',
                max_length=32,
                verbose_name='\u5b57\u6bb5\u7c7b\u578b',
                choices=[
                    ('STRING', '\u5355\u884c\u6587\u672c'),
                    ('TEXT', '\u591a\u884c\u6587\u672c'),
                    ('INT', '\u6570\u5b57'),
                    ('DATE', '\u65e5\u671f'),
                    ('DATETIME', '\u65f6\u95f4'),
                    ('DATETIMERANGE', '\u65f6\u95f4\u95f4\u9694'),
                    ('TABLE', '\u8868\u683c'),
                    ('SELECT', '\u5355\u9009\u4e0b\u62c9\u6846'),
                    ('MULTISELECT', '\u591a\u9009\u4e0b\u62c9\u6846'),
                    ('CHECKBOX', '\u590d\u9009\u6846'),
                    ('RADIO', '\u5355\u9009\u6846'),
                    ('MEMBERS', '\u591a\u9009\u4eba\u5458\u9009\u62e9'),
                    ('RICHTEXT', '\u5bcc\u6587\u672c'),
                    ('FILE', '\u9644\u4ef6\u4e0a\u4f20'),
                    ('CUSTOMTABLE', '\u81ea\u5b9a\u4e49\u8868\u683c'),
                    ('CASCADE', '\u7ea7\u8054'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='type',
            field=models.CharField(
                default='STRING',
                max_length=32,
                verbose_name='\u5b57\u6bb5\u7c7b\u578b',
                choices=[
                    ('STRING', '\u5355\u884c\u6587\u672c'),
                    ('TEXT', '\u591a\u884c\u6587\u672c'),
                    ('INT', '\u6570\u5b57'),
                    ('DATE', '\u65e5\u671f'),
                    ('DATETIME', '\u65f6\u95f4'),
                    ('DATETIMERANGE', '\u65f6\u95f4\u95f4\u9694'),
                    ('TABLE', '\u8868\u683c'),
                    ('SELECT', '\u5355\u9009\u4e0b\u62c9\u6846'),
                    ('MULTISELECT', '\u591a\u9009\u4e0b\u62c9\u6846'),
                    ('CHECKBOX', '\u590d\u9009\u6846'),
                    ('RADIO', '\u5355\u9009\u6846'),
                    ('MEMBERS', '\u591a\u9009\u4eba\u5458\u9009\u62e9'),
                    ('RICHTEXT', '\u5bcc\u6587\u672c'),
                    ('FILE', '\u9644\u4ef6\u4e0a\u4f20'),
                    ('CUSTOMTABLE', '\u81ea\u5b9a\u4e49\u8868\u683c'),
                    ('CASCADE', '\u7ea7\u8054'),
                ],
            ),
        ),
    ]
