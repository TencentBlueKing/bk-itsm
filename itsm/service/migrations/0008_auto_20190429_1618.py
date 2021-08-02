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

import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0013_auto_20190429_1618'),
        ('service', '0007_propertyrecord_display_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
            ],
            options={
                'verbose_name': '\u670d\u52a1\u5206\u7c7b\u8868',
                'verbose_name_plural': '\u670d\u52a1\u5206\u7c7b\u8868',
            },
        ),
        migrations.CreateModel(
            name='DictData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'creator',
                    models.CharField(
                        default='system', max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                (
                    'updated_by',
                    models.CharField(
                        default='system', max_length=64, null=True, verbose_name='\u4fee\u6539\u4eba', blank=True
                    ),
                ),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4', blank=True)),
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                ('key', models.CharField(max_length=255, verbose_name='\u7f16\u7801')),
                ('name', models.CharField(max_length=255, verbose_name='\u540d\u79f0')),
                ('is_readonly', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53ea\u8bfb')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={'verbose_name': '\u5b57\u5178\u6570\u636e', 'verbose_name_plural': '\u5b57\u5178\u6570\u636e',},
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                ('key', models.CharField(default='DEFAULT', max_length=64, verbose_name='\u670d\u52a1\u7f16\u53f7')),
                ('name', models.CharField(max_length=255, verbose_name='\u670d\u52a1\u540d\u79f0')),
                ('desc', models.CharField(default='', max_length=255, verbose_name='\u670d\u52a1\u63cf\u8ff0')),
                ('is_valid', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548')),
            ],
            options={'verbose_name': '\u670d\u52a1', 'verbose_name_plural': '\u670d\u52a1',},
        ),
        migrations.CreateModel(
            name='ServiceCatalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'creator',
                    models.CharField(
                        default='system', max_length=64, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True
                    ),
                ),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                (
                    'updated_by',
                    models.CharField(
                        default='system', max_length=64, null=True, verbose_name='\u4fee\u6539\u4eba', blank=True
                    ),
                ),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4', blank=True)),
                (
                    'is_deleted',
                    models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u8f6f\u5220\u9664'),
                ),
                ('key', models.CharField(unique=True, max_length=255, verbose_name='\u76ee\u5f55\u5173\u952e\u5b57')),
                ('name', models.CharField(max_length=64, verbose_name='\u76ee\u5f55\u540d\u79f0')),
                (
                    'desc',
                    models.CharField(
                        default='', max_length=255, null=True, verbose_name='\u76ee\u5f55\u63cf\u8ff0', blank=True
                    ),
                ),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                (
                    'parent',
                    mptt.fields.TreeForeignKey(
                        related_name='children',
                        verbose_name='\u4e0a\u7ea7\u76ee\u5f55',
                        blank=True,
                        to='service.ServiceCatalog',
                        null=True,
                        on_delete=models.CASCADE
                    ),
                ),
            ],
            options={'verbose_name': '\u670d\u52a1\u76ee\u5f55', 'verbose_name_plural': '\u670d\u52a1\u76ee\u5f55',},
        ),
        migrations.CreateModel(
            name='Sla',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                ('name', models.CharField(max_length=255, verbose_name='\u540d\u79f0')),
                (
                    'level',
                    models.IntegerField(
                        default=1,
                        verbose_name='\u7ea7\u522b',
                        choices=[(0, '\u4e00\u822c'), (1, '\u4f4e'), (2, '\u4e2d'), (3, '\u9ad8')],
                    ),
                ),
                ('resp_time', models.CharField(max_length=64, verbose_name='\u54cd\u5e94\u65f6\u95f4\u8981\u6c42')),
                ('deal_time', models.CharField(max_length=64, verbose_name='\u89e3\u51b3\u65f6\u95f4\u8981\u6c42')),
                (
                    'desc',
                    models.CharField(default='', max_length=255, null=True, verbose_name='\u63cf\u8ff0', blank=True),
                ),
            ],
            options={'verbose_name': '\u670d\u52a1\u7ea7\u522b', 'verbose_name_plural': '\u670d\u52a1\u7ea7\u522b',},
        ),
        migrations.CreateModel(
            name='SysDict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=64, verbose_name='\u521b\u5efa\u4eba')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('updated_by', models.CharField(max_length=64, verbose_name='\u4fee\u6539\u4eba')),
                ('end_at', models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8f6f\u5220\u9664')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5185\u7f6e')),
                ('key', models.CharField(max_length=255, verbose_name='\u7f16\u7801')),
                ('name', models.CharField(max_length=255, verbose_name='\u540d\u79f0')),
                (
                    'desc',
                    models.CharField(default='', max_length=255, null=True, verbose_name='\u63cf\u8ff0', blank=True),
                ),
                ('is_enabled', models.BooleanField(default=True, verbose_name='\u662f\u5426\u542f\u7528')),
                ('is_readonly', models.BooleanField(default=False, verbose_name='\u662f\u5426\u53ea\u8bfb')),
            ],
            options={'verbose_name': '\u6570\u636e\u5b57\u5178', 'verbose_name_plural': '\u6570\u636e\u5b57\u5178',},
        ),
        migrations.AddField(
            model_name='service',
            name='sla',
            field=models.ForeignKey(
                related_name='sla_services',
                to='service.Sla',
                help_text='\u5173\u8054\u7684\u670d\u52a1\u7ea7\u522b',
                null=True,
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='workflow',
            field=models.ForeignKey(
                related_name='services', to='workflow.WorkflowVersion', help_text='\u5173\u8054\u6d41\u7a0b\u7248\u672c',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='dictdata',
            name='dict_table',
            field=models.ForeignKey(
                related_name='dict_data', to='service.SysDict', help_text='\u5173\u8054\u5b57\u5178\u9879',
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='dictdata',
            name='parent',
            field=mptt.fields.TreeForeignKey(
                related_name='children',
                verbose_name='\u4e0a\u7ea7\u76ee\u5f55',
                blank=True,
                to='service.DictData',
                null=True,
                on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name='catalogservice',
            name='catalog',
            field=models.ForeignKey(help_text='\u5173\u8054\u670d\u52a1\u76ee\u5f55', to='service.ServiceCatalog',
                                    on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='catalogservice',
            name='service',
            field=models.ForeignKey(help_text='\u5173\u8054\u670d\u52a1\u6761\u76ee', to='service.Service',
                                    on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(name='dictdata', unique_together=set([('dict_table', 'key')]),),
    ]
