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

from distutils.version import StrictVersion

import django
from django.db.models import *
from django.conf import settings


def is_boolean(field):
    return isinstance(field, (BooleanField, NullBooleanField))


def is_string(field):
    return isinstance(field, (CharField, EmailField, IPAddressField, SlugField, URLField))


def is_number(field):
    return isinstance(field, (IntegerField, SmallIntegerField, PositiveIntegerField,
                              PositiveSmallIntegerField, BigIntegerField,
                              CommaSeparatedIntegerField, DecimalField, FloatField))


def is_datetime(field):
    return isinstance(field, (DateTimeField, DateField, TimeField))


def is_file(field):
    return isinstance(field, (FileField, FilePathField))


def is_binary(self, field):
    if self.django_greater_than('1.6'):
        return isinstance(field, (BinaryField))
    else:
        return False


def django_greater_than(self, version):
    # Slice to avoid StrictVersion errors with versions like 1.8c1
    DJANGO_VERSION = django.get_version()[0:3]
    return StrictVersion(DJANGO_VERSION) >= StrictVersion(version)


class BaseStrategy:
    """
    基础策略， 封装了策略所需要的字段判定方法
    """
    type = None

    def get_value(self, field_list: list) -> list:
        """

        :param field_list: [Field obj,Field obj, Field obj]
        :return: [field_name]
        """
        return [field.name for field in field_list if self.is_matched(field)]

    def is_matched(self, field: Field):
        return True


class ListRawIdFieldsStrategy(BaseStrategy):
    type = "raw_id_fields"

    def is_matched(self, field: Field):
        return isinstance(field, (ForeignKey, OneToOneField))


class FilterHorizontalStrategy(BaseStrategy):
    type = "filter_horizontal"

    def is_matched(self, field: Field):
        return isinstance(field, (ManyToManyField,))


class ListDisplayStrategy(BaseStrategy):
    type = "list_display"

    def is_matched(self, field: Field):
        return is_string(field) or is_boolean(field) or \
               is_number(field) or is_datetime(field)


class ListDisplayLinksStrategy(BaseStrategy):
    type = "list_display_links"

    def is_matched(self, field: Field):
        return is_string(field) or is_boolean(field) \
               or is_number(field) or is_datetime(field)


class ListFilterStrategy(BaseStrategy):
    type = "list_filter"

    def is_matched(self, field: Field):
        return is_string(field) or is_boolean(field) \
               or is_number(field) or is_datetime(field)


class SearchFieldsStrategy(BaseStrategy):
    type = "search_fields"

    def is_matched(self, field: Field):
        return is_string(field)


class ListPerPageStrategy(BaseStrategy):
    type = "list_per_page"

    def get_value(self, field_list):
        return int(settings.DSA_LIST_PER_PAGE) if hasattr(settings, 'DSA_LIST_PER_PAGE') else 5


class ListMaxShowAllStrategy(BaseStrategy):
    type = "list_max_show_all"

    def get_value(self, field_list):
        return int(settings.DSA_LIST_MAX_SHOW_ALL) if hasattr(settings,
                                                              'DSA_LIST_MAX_SHOW_ALL') else 50


class StrategyDispatcher(object):
    """
    StrategyDispatcher 负责将不同的方法分派到不同的类中去处理
    """
    STRATEGY_CLASS = [
        ListRawIdFieldsStrategy,
        ListDisplayStrategy,
        ListDisplayLinksStrategy,
        ListFilterStrategy,
        SearchFieldsStrategy,
        ListPerPageStrategy,
        ListMaxShowAllStrategy,
        FilterHorizontalStrategy
    ]

    STRATEGY_DICT = dict(
        [(_object.type, _object()) for _object in STRATEGY_CLASS])

    def __init__(self, strategy_type):
        if strategy_type not in self.STRATEGY_DICT:
            raise Exception("The strategy corresponding to Strategy_type does not exist")

        self.strategy_type = strategy_type

    def get_value(self, field_list):
        return self.STRATEGY_DICT[self.strategy_type].get_value(field_list)
