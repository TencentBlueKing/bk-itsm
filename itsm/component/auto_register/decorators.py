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

from django.db import models

from .contants import ADMIN_FIELDS
from .strategy import StrategyDispatcher
from .utils import get_fields_from_model, create_admin_class, register_admin_class


def register(cls: models.Model = None, **kwargs) -> models.Model:
    """
    通过装饰器将model自动注册到django_admin 中
    :param cls: models.Model
    :param kwargs:需要覆盖的默认配置 {
            "list_display" : ['x', 'y', 'z']
            ......
        }
    :return: cls
    """
    if "list_display" in kwargs:
        kwargs["list_display_links"] = kwargs["list_display"]

    def register_admin(cls):
        fields = get_fields_from_model(cls)
        config = {}
        for admin_field in ADMIN_FIELDS:
            if admin_field in kwargs:
                config[admin_field] = kwargs.get(admin_field)
                continue
            dispatcher = StrategyDispatcher(admin_field)
            config[admin_field] = dispatcher.get_value(fields)
        admin_class = create_admin_class(cls, **config)
        register_admin_class(cls, admin_class)
        return cls

    if cls is not None:
        return register_admin(cls)

    return register_admin
