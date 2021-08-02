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

import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _
from rest_framework import serializers

from itsm.service.models import CatalogService, Service, ServiceCategory


__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."


def time_validator(value):
    time = value[-1]
    if time not in ["m", "h", "d"]:
        raise serializers.ValidationError(_('时间单位不正确'))
    try:
        number = int(value[:-1])
        if number > 65536 or number <= 0:
            raise serializers.ValidationError(_('时间超出了设置范围（1~65536）'))
    except ValueError:
        raise serializers.ValidationError(_('数据类型错误，不是合法的时间'))


key_validator = RegexValidator(re.compile('^[_a-zA-Z0-9]+$'), message=_('请输入合法编码：英文数字及下划线'), code='invalid',)

# 正则表达式带中文一定要要带上u，否则校验不通过
name_validator = RegexValidator(
    re.compile(r'^[a-zA-Z0-9_\s()（）\u4e00-\u9fa5]+$'), message=_('请输入合法名称：中英文、中英文括号、数字、空格及下划线'), code='invalid',
)


def service_type_validator(value):
    """服务类型合法校验"""
    if not ServiceCategory.objects.filter(key=value).exists():
        raise serializers.ValidationError(_("服务类型不合法"))


def service_validate(service_id):
    try:
        service = Service.objects.get(id=service_id)
        if not service.is_valid:
            raise serializers.ValidationError({_("服务"): _("服务未启用，请联系管理员！")})
    except Service.DoesNotExist:
        raise serializers.ValidationError({_("服务"): _("服务不存在，请联系管理员！")})

    try:
        catalog_services = CatalogService.objects.get(service_id=service_id, is_deleted=False)
    except CatalogService.DoesNotExist:
        raise serializers.ValidationError({_("服务"): _("服务对应的服务目录不存在")})

    return service, catalog_services
