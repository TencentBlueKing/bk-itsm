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
from decimal import Context, Decimal, Inexact

from .util import method_type


def fn_name_to_pretty_label(name):
    return ' '.join([w.title() for w in name.split('_')])


def export_rule_data(variables, actions):
    """
    Export_rule_data is used to export all information about the
    variables, actions, and operators to the client. This will return a
    dictionary with three keys:
    - variables: a list of all available variables along with their label, type, options and params
    - actions: a list of all actions along with their label and params
    - variable_type_operators: a dictionary of all field_types -> list of available operators
    :param variables:
    :param actions:
    :return:
    """
    from . import operators

    actions_data = actions.get_all_actions()
    variables_data = variables.get_all_variables()

    variable_type_operators = {}
    for variable_class in inspect.getmembers(operators, lambda x: getattr(x, 'export_in_rule_data', False)):
        variable_type = variable_class[1]  # getmembers returns (name, value)
        variable_type_operators[variable_type.name] = variable_type.get_all_operators()

    return {
        "variables": variables_data,
        "actions": actions_data,
        "variable_type_operators": variable_type_operators
    }


def float_to_decimal(f):
    """
    Convert a floating point number to a Decimal with
    no loss of information. Intended for Python 2.6 where
    casting float to Decimal does not work.
    """
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result


def get_valid_fields():
    from . import fields

    valid_fields = [getattr(fields, f) for f in dir(fields) if f.startswith("FIELD_")]
    return valid_fields


def params_dict_to_list(params):
    """
    Transform parameters in dict format to list of dictionaries with a standard format.
    If 'params' is not a dictionary, then the result will be 'params'
    :param params: Dictionary of parameters with the following format:
    {
        'param_name': param_type
    }
    :return:
    [
        {
            'label': 'param_name'
            'name': 'param_name'
            'field_type': param_type
        }
    ]
    """
    if params is None:
        return []

    if not isinstance(params, dict):
        return params

    return [
        {
            'label': fn_name_to_pretty_label(name),
            'name': name,
            'field_type': param_field_type
        } for name, param_field_type in params.items()
    ]


def check_params_valid_for_method(method, given_params, method_type_name):
    """
    Verifies that the given parameters (defined in the Rule) match the names of those defined in
    the variable or action decorator. Raise an error if one of the sets contains a parameter that
    the other does not.

    :param method:
    :param given_params: Parameters defined within the Rule (Action or Condition)
    :param method_type_name: A method type defined in util.method_type module
    :return: Set of default values for params which are missing but have a default value. Raise exception if parameters
    don't
    match (defined in method and
    Rule)
    """
    method_params = params_dict_to_list(method.params)
    defined_params = [param.get('name') for param in method_params]
    missing_params = set(defined_params).difference(given_params)

    # check for default value in action parameters, if it is present, exclude param from missing params
    params_with_default_value = set()
    if method_type_name == method_type.METHOD_TYPE_ACTION and missing_params:
        params_with_default_value = check_for_default_value_for_missing_params(missing_params, method_params)
        missing_params -= params_with_default_value

    if missing_params:
        raise AssertionError("Missing parameters {0} for {1} {2}".format(
            ', '.join(missing_params), method_type_name, method.__name__))

    invalid_params = set(given_params).difference(defined_params)

    if invalid_params:
        raise AssertionError("Invalid parameters {0} for {1} {2}".format(
            ', '.join(invalid_params), method_type_name, method.__name__))

    return params_with_default_value


def check_for_default_value_for_missing_params(missing_params, method_params):
    """
    :param missing_params: Params missing from Rule
    :param method_params: Params defined on method, which could have default value for missing param
    [{
     'label': 'action_label',
     'name': 'action_parameter',
     'fieldType': 'numeric',
     'defaultValue': 123
    },
    ...
    ]
    :return Params that are missing from rule but have default params: {'action_parameter'}
    """
    missing_params_with_default_value = set()
    if method_params:
        for param in method_params:
            if param['name'] in missing_params and param.get('defaultValue', None) is not None:
                missing_params_with_default_value.add(param['name'])

    return missing_params_with_default_value


def validate_rule_data(variables, actions, rule):
    """
    validate_rule_data is used to check a generated rule against a set of variables and actions
    :param variables:
    :param actions:
    :param rule:
    :return: bool
    :raises AssertionError:
    """
    def validate_root_keys(rule):
        """
        Check the root object contains both 'actions' & 'conditions'
        """
        root_keys = list(rule.keys())
        if 'actions' not in root_keys:
            raise AssertionError('Missing "{}" key'.format('actions'))

    def validate_condition_operator(condition, rule_schema):
        """
        Check provided condition contains a valid operator
        """
        if "operator" not in condition:
            raise AssertionError('Missing "operator" key for condition {}'.format(condition.get('name')))
        for item in rule_schema.get('variables'):
            if item.get('name') == condition.get('name'):
                condition_field_type = item.get('field_type')
                variable_operators = rule_schema.get('variable_type_operators', {}).get(condition_field_type, [])
                for operators in variable_operators:
                    if operators['name'] == condition['operator']:
                        return True
                raise AssertionError('Unknown operator "{}"'.format(condition['operator']))
        raise AssertionError('Name "{}" not supported'.format(condition.get('name')))

    def validate_condition_name(condition, variables):
        """
        Check provided condition contains a 'name' key and the value is valid
        """
        condition_name = condition.get('name')
        if not condition_name:
            raise AssertionError('Missing condition "name" key in {}'.format(condition))
        if not hasattr(variables, condition_name):
            raise AssertionError('Unknown condition "{}"'.format(condition_name))

    def validate_condition(condition, variables, rule_schema):
        validate_condition_name(condition, variables)
        validate_condition_operator(condition, rule_schema)
        method = getattr(variables, condition.get('name'))
        params = condition.get('params', {})
        check_params_valid_for_method(method, params, method_type.METHOD_TYPE_VARIABLE)

    def validate_conditions(input_conditions, rule_schema):
        """
        Recursively check all levels of input conditions
        """
        import six

        if isinstance(input_conditions, list):
            for condition in input_conditions:
                validate_conditions(condition, rule_schema)
        if isinstance(input_conditions, dict):
            keys = list(input_conditions.keys())
            if 'any' in keys or 'all' in keys:
                if len(keys) > 1:
                    raise AssertionError('Expected ONE of "any" or "all" but found {}'.format(keys))
                else:
                    for _, v in six.iteritems(input_conditions):
                        validate_conditions(v, rule_schema)
            else:
                validate_condition(input_conditions, variables, rule_schema)

    def validate_actions(input_actions):
        """
        Check all input actions contain valid names and parameters for defined actions
        """
        if type(input_actions) is not list:
            raise AssertionError('"actions" key must be a list')
        for action in input_actions:
            method = getattr(actions, action.get('name'), None)
            params = action.get('params', {})
            check_params_valid_for_method(method, params, method_type.METHOD_TYPE_ACTION)

    rule_schema = export_rule_data(variables, actions)
    validate_root_keys(rule)
    conditions = rule.get('conditions', None)
    if conditions is not None and type(conditions) is not dict:
        raise AssertionError('"conditions" must be a dictionary')
    validate_conditions(conditions, rule_schema)
    validate_actions(rule.get('actions'))
    return True
