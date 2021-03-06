# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-05-28 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0019_delete_variablemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('logger_name', models.SlugField(
                    max_length=128, verbose_name='logger \u540d\u79f0')),
                ('level_name', models.SlugField(max_length=32,
                                                verbose_name='\u65e5\u5fd7\u7b49\u7ea7')),
                ('message', models.TextField(null=True,
                                             verbose_name='\u65e5\u5fd7\u5185\u5bb9')),
                ('exception', models.TextField(null=True,
                                               verbose_name='\u5f02\u5e38\u4fe1\u606f')),
                ('logged_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='\u8f93\u51fa\u65f6\u95f4')),
                ('node_id', models.CharField(db_index=True,
                                             max_length=32, verbose_name='\u8282\u70b9 ID')),
                ('history_id', models.IntegerField(default=-
                1, verbose_name='\u8282\u70b9\u6267\u884c\u5386\u53f2 ID')),
            ],
        ),
    ]
