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

import inspect
import re
from datetime import date, datetime, time
from decimal import Decimal
from functools import wraps

from six import integer_types, string_types

from .fields import (
    FIELD_DATETIME,
    FIELD_NO_INPUT,
    FIELD_NUMERIC,
    FIELD_SELECT,
    FIELD_SELECT_MULTIPLE,
    FIELD_TEXT,
    FIELD_TIME,
)
from .utils import float_to_decimal, fn_name_to_pretty_label


class BaseType(object):
    def __init__(self, value):
        self.value = self._assert_valid_value_and_cast(value)

    def _assert_valid_value_and_cast(self, value):
        raise NotImplementedError()

    @classmethod
    def get_all_operators(cls):
        methods = inspect.getmembers(cls)
        return [
            {"name": m[0], "label": m[1].label, "input_type": m[1].input_type}
            for m in methods
            if getattr(m[1], "is_operator", False)
        ]

    @classmethod
    def get_display_operators(cls):
        methods = inspect.getmembers(cls)
        return [
            {"name": m[0], "label": m[1].label, "input_type": m[1].input_type}
            for m in methods
            if getattr(m[1], "is_operator", False) and getattr(m[1], "display", False)
        ]


def export_type(cls):
    """Decorator to expose the given class to business_rules.export_rule_data."""
    cls.export_in_rule_data = True
    return cls


def type_operator(input_type, label=None, assert_type_for_arguments=True, display=True):
    """Decorator to make a function into a type operator.

    - assert_type_for_arguments - if True this patches the operator function
      so that arguments passed to it will have _assert_valid_value_and_cast
      called on them to make type errors explicit.
    """

    def wrapper(func):
        func.is_operator = True
        func.label = label or fn_name_to_pretty_label(func.__name__)
        func.input_type = input_type
        func.display = display

        @wraps(func)
        def inner(self, *args, **kwargs):
            if assert_type_for_arguments:
                args = [self._assert_valid_value_and_cast(arg) for arg in args]
                kwargs = dict(
                    (k, self._assert_valid_value_and_cast(v)) for k, v in kwargs.items()
                )
            return func(self, *args, **kwargs)

        return inner

    return wrapper


@export_type
class StringType(BaseType):
    name = "string"

    def _assert_valid_value_and_cast(self, value):
        value = value or ""
        if not isinstance(value, string_types):
            raise AssertionError("{0} is not a valid string type.".format(value))
        return value

    @type_operator(FIELD_TEXT, label="等于")
    def equal_to(self, other_string):
        return self.value == other_string

    @type_operator(FIELD_TEXT, label="不等于")
    def non_equal(self, other_string):
        return self.value != other_string

    @type_operator(FIELD_TEXT, label="等于(忽略大小写)")
    def equal_to_case_insensitive(self, other_string):
        return self.value.lower() == other_string.lower()

    @type_operator(FIELD_TEXT, label="以设定值开始")
    def starts_with(self, other_string):
        return self.value.startswith(other_string)

    @type_operator(FIELD_TEXT, label="以设定值结束")
    def ends_with(self, other_string):
        return self.value.endswith(other_string)

    @type_operator(FIELD_TEXT, label="包含")
    def contains(self, other_string):
        return other_string in self.value

    @type_operator(FIELD_TEXT, label="不包含")
    def non_contains(self, other_string):
        return other_string not in self.value

    @type_operator(FIELD_TEXT, label="正则匹配")
    def matches_regex(self, regex):
        return re.search(regex, self.value)

    @type_operator(FIELD_NO_INPUT, label="不为空")
    def non_empty(self):
        return bool(self.value)

    @type_operator(FIELD_TEXT, label="不在值之内", assert_type_for_arguments=False)
    def not_in(self, other_value):
        return self.value not in other_value


@export_type
class NumericType(BaseType):
    EPSILON = Decimal("0.000001")

    name = "numeric"

    @staticmethod
    def _assert_valid_value_and_cast(value):
        if isinstance(value, float):
            # In python 2.6, casting float to Decimal doesn't work
            return float_to_decimal(value)
        if isinstance(value, integer_types):
            return Decimal(value)
        if isinstance(value, Decimal):
            return value
        else:
            raise AssertionError("{0} is not a valid numeric type.".format(value))

    @type_operator(FIELD_NUMERIC, label="等于")
    def equal_to(self, other_numeric):
        return abs(self.value - other_numeric) <= self.EPSILON

    @type_operator(FIELD_NUMERIC, label="大于")
    def greater_than(self, other_numeric):
        return (self.value - other_numeric) > self.EPSILON

    @type_operator(FIELD_NUMERIC, label="大于或等于")
    def greater_than_or_equal_to(self, other_numeric):
        return self.greater_than(other_numeric) or self.equal_to(other_numeric)

    @type_operator(FIELD_NUMERIC, label="小于")
    def less_than(self, other_numeric):
        return (other_numeric - self.value) > self.EPSILON

    @type_operator(FIELD_NUMERIC, label="小于或等于")
    def less_than_or_equal_to(self, other_numeric):
        return self.less_than(other_numeric) or self.equal_to(other_numeric)


@export_type
class BooleanType(BaseType):
    name = "boolean"

    def _assert_valid_value_and_cast(self, value):
        if type(value) != bool:
            raise AssertionError("{0} is not a valid boolean type".format(value))
        return value

    @type_operator(FIELD_NO_INPUT, display=False)
    def is_true(self):
        return self.value

    @type_operator(FIELD_NO_INPUT, display=False)
    def is_false(self):
        return not self.value

    @type_operator(FIELD_NO_INPUT, label="等于")
    def equal_to(self, other_bool):
        return self.value == other_bool

    @type_operator(FIELD_NO_INPUT, label="不等于")
    def not_equal_to(self, other_bool):
        return self.value != other_bool


@export_type
class SelectType(BaseType):
    name = "select"

    def _assert_valid_value_and_cast(self, value):
        if not hasattr(value, "__iter__"):
            raise AssertionError("{0} is not a valid select type".format(value))
        return value

    @staticmethod
    def _case_insensitive_equal_to(value_from_list, other_value):
        if isinstance(value_from_list, string_types) and isinstance(
            other_value, string_types
        ):
            return value_from_list.lower() == other_value.lower()
        else:
            return value_from_list == other_value

    @type_operator(FIELD_SELECT, assert_type_for_arguments=False)
    def contains(self, other_value):
        for val in self.value:
            if self._case_insensitive_equal_to(val, other_value):
                return True
        return False

    @type_operator(FIELD_SELECT, assert_type_for_arguments=False)
    def does_not_contain(self, other_value):
        for val in self.value:
            if self._case_insensitive_equal_to(val, other_value):
                return False
        return True


@export_type
class SelectMultipleType(BaseType):
    name = "select_multiple"

    def _assert_valid_value_and_cast(self, value):
        if not hasattr(value, "__iter__"):
            raise AssertionError(
                "{0} is not a valid select multiple type".format(value)
            )
        return value

    @type_operator(FIELD_SELECT_MULTIPLE, label="包含")
    def contains_all(self, other_value):
        select = SelectType(self.value)
        for other_val in other_value:
            if not select.contains(other_val):
                return False
        return True

    @type_operator(FIELD_SELECT_MULTIPLE, label="被设定值包含")
    def is_contained_by(self, other_value):
        other_select_multiple = SelectMultipleType(other_value)
        return other_select_multiple.contains_all(self.value)

    @type_operator(FIELD_SELECT_MULTIPLE, display=False)
    def shares_at_least_one_element_with(self, other_value):
        select = SelectType(self.value)
        for other_val in other_value:
            if select.contains(other_val):
                return True
        return False

    @type_operator(FIELD_SELECT_MULTIPLE, display=False)
    def shares_exactly_one_element_with(self, other_value):
        found_one = False
        select = SelectType(self.value)
        for other_val in other_value:
            if select.contains(other_val):
                if found_one:
                    return False
                found_one = True
        return found_one

    @type_operator(FIELD_SELECT_MULTIPLE, label="不包含")
    def shares_no_elements_with(self, other_value):
        return not self.shares_at_least_one_element_with(other_value)


@export_type
class DateTimeType(BaseType):
    name = "datetime"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"

    def _assert_valid_value_and_cast(self, value):
        """
        Parse string with formats '%Y-%m-%dT%H:%M:%S' or '%Y-%m-%d' into datetime.datetime instance.

        :param value:
        :return:
        """
        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)

        try:
            return datetime.strptime(value, self.DATETIME_FORMAT)
        except (ValueError, TypeError):
            pass

        try:
            return datetime.strptime(value, self.DATE_FORMAT)
        except (ValueError, TypeError):
            raise AssertionError("{0} is not a valid datetime type.".format(value))

    def _set_timezone_if_different(self, variable_datetime, condition_value_datetime):
        # type: (datetime, datetime) -> datetime
        if variable_datetime.tzinfo is None:
            if condition_value_datetime.tzinfo is None:
                return condition_value_datetime
            else:
                return condition_value_datetime.replace(tzinfo=None)

        return condition_value_datetime.replace(tzinfo=variable_datetime.tzinfo)

    @type_operator(FIELD_DATETIME, label="等于")
    def equal_to(self, other_datetime):
        # type: (datetime) -> bool
        other_datetime = self._set_timezone_if_different(self.value, other_datetime)

        return self.value == other_datetime

    @type_operator(FIELD_DATETIME, label="大于")
    def after_than(self, other_datetime):
        # type: (datetime) -> bool
        other_datetime = self._set_timezone_if_different(self.value, other_datetime)

        return self.value > other_datetime

    @type_operator(FIELD_DATETIME, label="大于或等于")
    def after_than_or_equal_to(self, other_datetime):
        return self.after_than(other_datetime) or self.equal_to(other_datetime)

    @type_operator(FIELD_DATETIME, label="小于")
    def before_than(self, other_datetime):
        # type: (datetime) -> bool
        other_datetime = self._set_timezone_if_different(self.value, other_datetime)

        return self.value < other_datetime

    @type_operator(FIELD_DATETIME, label="小于或等于")
    def before_than_or_equal_to(self, other_datetime):
        return self.before_than(other_datetime) or self.equal_to(other_datetime)


@export_type
class TimeType(BaseType):
    name = "time"
    TIME_FORMAT = "%H:%M:%S"
    TIME_FORMAT_NO_SECONDS = "%H:%M"

    def _assert_valid_value_and_cast(self, value):
        """
        Parse datetime, time or string with format %H:%M:%S into time instance.

        :param value: datetime, date or string with format %H:%M:%S
        :return: time
        """
        if isinstance(value, time):
            return value

        if isinstance(value, datetime):
            return value.time()

        try:
            dt = datetime.strptime(value, self.TIME_FORMAT)
            return time(dt.hour, dt.minute, dt.second)
        except (ValueError, TypeError):
            pass

        try:
            dt = datetime.strptime(value, self.TIME_FORMAT_NO_SECONDS)
            return time(dt.hour, dt.minute, dt.second)
        except (ValueError, TypeError):
            raise AssertionError("{0} is not a valid time type.".format(value))

    @type_operator(FIELD_TIME, label="等于")
    def equal_to(self, other_time):
        return self.value == other_time

    @type_operator(FIELD_TIME, label="大于")
    def after_than(self, other_time):
        return self.value > other_time

    @type_operator(FIELD_TIME, label="大于或等于")
    def after_than_or_equal_to(self, other_time):
        return self.after_than(other_time) or self.equal_to(other_time)

    @type_operator(FIELD_TIME, label="小于")
    def before_than(self, other_time):
        return self.value < other_time

    @type_operator(FIELD_TIME, label="小于或等于")
    def before_than_or_equal_to(self, other_time):
        return self.before_than(other_time) or self.equal_to(other_time)
