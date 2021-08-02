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

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.db import models


def get_fields_from_model(model_class: models.Model) -> list:
    """
    获取到某个模型下所有的字段，包含基础字段，外键
    :param model_class: Model
    :return: [Field, Field, Field]
    """
    field_list = []
    for field in model_class._meta.fields:
        field_list.append(field)
    # 多对多外键本身并不在fields中，需要单独处理
    field_list.extend(model_class._meta.many_to_many)
    return field_list


def create_admin_class(model: models.Model, **kwargs) -> admin.ModelAdmin:
    """
    :param model: models.Model
    :param kwargs: {
                        list_display=['x', 'y', 'z']
                        ...
                    }
    :return: admin.ModelAdmin obj
    """
    model_name = model.__name__
    # 动态构建一个admin.ModelAdmin子类并填充参数
    model_admin_class = type(model_name + 'Admin', (admin.ModelAdmin,), kwargs)
    return model_admin_class


def register_admin_class(model: models.Model, admin_class: admin.ModelAdmin) -> None:
    try:
        admin.site.register(model, admin_class)
    except AlreadyRegistered:
        pass
