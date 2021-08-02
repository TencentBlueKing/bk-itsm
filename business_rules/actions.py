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

from .utils import fn_name_to_pretty_label, get_valid_fields


class BaseActions(object):
    """ Classes that hold a collection of actions to use with the rules
    engine should inherit from this.
    """

    @classmethod
    def get_all_actions(cls):
        methods = inspect.getmembers(cls)
        return [{
            'name': m[0],
            'label': m[1].label,
            'params': m[1].params
        } for m in methods if getattr(m[1], 'is_rule_action', False)]

    def failure_handler(self, error, action, successful_conditions):
        """Action执行失败后的处理行为
        :param error: 错误对象
        :param action: action的上下文
        :param successful_conditions: action匹配的规则
        """
        method_failure_handler = getattr(self, "failure_handler_%s" % action["name"], None)
        # 是否为实例方法
        if inspect.ismethod(method_failure_handler):
            method_failure_handler(error, successful_conditions)

    def finish_handler(self, result, action, successful_conditions):
        """Action执行完成后的处理行为
        :param result: action执行完成后的返回结果
        :param action: action的上下文
        :param successful_conditions: action匹配的规则
        """
        pass


def _validate_action_parameters(func, params):
    """
    Verifies that the parameters specified are actual parameters for the
    function `func`, and that the field types are FIELD_* types in fields.
    :param func:
    :param params:
                {
                 'label': 'action_label',
                 'name': 'action_parameter',
                 'fieldType': 'numeric',
                 'defaultValue': 123
                }
    :return:
    """
    if params is not None:
        # Verify field name is valid
        valid_fields = get_valid_fields()

        for param in params:
            param_name, field_type = param['name'], param['fieldType']
            if param_name not in func.__code__.co_varnames:
                raise AssertionError("Unknown parameter name {0} specified for action {1}".format(
                    param_name, func.__name__))

            if field_type not in valid_fields:
                raise AssertionError("Unknown field type {0} specified for action {1} param {2}".format(
                    field_type, func.__name__, param_name))


def rule_action(label=None, params=None, terminate_process=False):
    """
    Decorator to make a function into a rule action.
    `params` parameter could be one of the following:
    1. Dictionary with params names as keys and types as values
    Example:
    params={
        'param_name': fields.FIELD_NUMERIC,
    }

    2. If a param has a default value, ActionParam can be used. Example:
    params={
        'action_parameter': ActionParam(field_type=fields.FIELD_NUMERIC, default_value=123)
    }

    :param terminate_process: If terminate rule process
    :param label: Label for Action
    :param params: Parameters expected by the Action function
    :return: Decorator function wrapper
    """

    def wrapper(func):
        params_ = params
        if isinstance(params, dict):
            params_ = [
                dict(
                    label=fn_name_to_pretty_label(key),
                    name=key,
                    fieldType=getattr(value, "field_type", value),
                    defaultValue=getattr(value, "default_value", None)
                ) for key, value in params.items()
            ]

        _validate_action_parameters(func, params_)

        func.is_rule_action = True
        func.label = label or fn_name_to_pretty_label(func.__name__)
        func.params = params_
        func.terminate_process = terminate_process

        return func

    return wrapper


class ActionParam:
    def __init__(self, field_type, default_value=None):
        self.field_type = field_type
        self.default_value = default_value
