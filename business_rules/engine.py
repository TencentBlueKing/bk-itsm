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

import contextlib
import logging
import threading

from config.default import DEFAULT_VARIABLE_NAME
from . import utils
from .fields import FIELD_NO_INPUT
from .models import ConditionResult
from .util import method_type
from .util.compat import getfullargspec

from .operators import (
    BaseType,
    BooleanType,
    DateTimeType,
    NumericType,
    SelectMultipleType,
    StringType,
    TimeType,
)

logger = logging.getLogger("app")


def run_all(rule_list, defined_variables, defined_actions, stop_on_first_trigger=False):
    # type: (...) -> list[bool]
    results = [False] * len(rule_list)
    for i, rule in enumerate(rule_list):
        result = run(rule, defined_variables, defined_actions, if_batch_run=False)
        if result:
            results[i] = True
            if stop_on_first_trigger:
                break
    return results


def run(rule, defined_variables, defined_actions, if_batch_run=True):
    conditions, actions = rule.get("conditions"), rule["actions"]

    if conditions is not None:
        rule_triggered, checked_conditions_results = check_conditions_recursively(conditions, defined_variables, rule)
    else:
        # If there are no conditions then trigger actions
        rule_triggered = True
        checked_conditions_results = []

    if rule_triggered:
        do_actions(actions, defined_actions, checked_conditions_results, rule, if_batch_run)
        return True

    return False


def check_conditions_recursively(conditions, defined_variables, rule):
    """
    Check if the conditions are true given a set of variables.
    This method checks all conditions including embedded ones.

    :param conditions:  Conditions to be checked
    :param defined_variables: BaseVariables instance to get variables values to check Conditions
    :param rule: Original rule where Conditions and Actions are defined
    :return: tuple with result of condition check and list of checked conditions with each individual result.

            (condition_result, [(condition1_result), (condition2_result)]

            condition1_result = (condition_result, variable name, condition operator, condition value, condition params)
    """
    keys = list(conditions.keys())
    if keys == ["all"]:
        assert len(conditions["all"]) >= 1
        matches = []
        for condition in conditions["all"]:
            check_condition_result, matches_results = check_conditions_recursively(condition, defined_variables, rule)
            matches.extend(matches_results)
            if not check_condition_result:
                return False, []
        return True, matches

    elif keys == ["any"]:
        assert len(conditions["any"]) >= 1
        for condition in conditions["any"]:
            check_condition_result, matches_results = check_conditions_recursively(condition, defined_variables, rule)
            if check_condition_result:
                return True, matches_results
        return False, []

    else:
        # help prevent errors - any and all can only be in the condition dict
        # if they're the only item
        assert not ("any" in keys or "all" in keys)
        result = check_condition(conditions, defined_variables, rule)
        return result[0], [result]


def check_condition(condition, defined_variables, rule):
    """
    Checks a single rule condition - the condition will be made up of
    variables, values, and the comparison operator. The defined_variables
    object must have a variable defined for any variables in this condition.

    :param condition:
    :param defined_variables:
    :param rule:
    :return: business_rules.models.ConditionResult

        .. code-block::
        (
            result of condition: bool,
            condition name: str,
            condition operator: str,
            condition value: ?,
            condition params: {}
        )
    """

    name, op, value, field_type, key = (
        condition.get("name") or condition.get("key", ""),
        condition["operator"],
        _get_reference_variable_value(condition, defined_variables),
        condition.get("field_type", "").lower(),
        condition.get("key"),
    )
    params = condition.get("params", {})
    operator_type = _get_variable_value(defined_variables, name, params, rule, key, field_type)
    return ConditionResult(
        result=_do_operator_comparison(operator_type, op, value), name=name, operator=op, value=value, parameters=params
    )


def _get_reference_variable_value(condition, defined_variables):
    if condition.get("type") == "reference":
        return defined_variables.reference_variable_by_name(ref_Key=condition["ref_key"])

    field_type = condition.get("field_type", "").lower()
    value = condition['value']

    if field_type == "bool":
        return value is True
    if field_type == 'int':
        return int(value)
    if field_type == 'numeric':
        return float(value)
    if field_type in ["string", 'select', 'text', 'radio']:
        return str(value)
    if field_type in ["multiselect", 'checkbox'] and isinstance(value, str):
        return set(value.split(","))
    return value


def _get_variable_value(defined_variables, name, params, rule, key=None, field_type=None):
    """
    Call the function provided on the defined_variables object with the
    given name (raise exception if that doesn't exist) and casts it to the
    specified type.

    Returns an instance of operators.BaseType
    :param defined_variables:
    :param name:
    :param params:
    :return: Instance of operators.BaseType
    """

    method = getattr(defined_variables, name, None) or getattr(defined_variables, DEFAULT_VARIABLE_NAME, None)

    if method is None:
        raise AssertionError(
            "Variable {0} is not defined in class {1}".format(name, defined_variables.__class__.__name__)
        )

    utils.check_params_valid_for_method(method, params, method_type.METHOD_TYPE_VARIABLE)

    method_params = _build_variable_parameters(method, params, rule)
    if key:
        method_params.update({"key": key})
    variable_value = method(**method_params)
    if method.field_type is not BaseType:
        return method.field_type(variable_value)
    return _get_real_variable_value(variable_value, field_type)


def _get_real_variable_value(variable_value, field_type):
    """条件配置了具体的操作类型，返回对应的类型即可"""
    if field_type == "bool":
        return BooleanType(variable_value)
    if field_type in ["numeric", "int"]:
        return NumericType(variable_value)
    if field_type in ["select_multiple", "member", "multiselect", 'checkbox']:
        if isinstance(variable_value, str):
            variable_value = variable_value.split(",")
        return SelectMultipleType(variable_value)
    if field_type == "datetime":
        return DateTimeType(variable_value)
    if field_type == "time":
        return TimeType(variable_value)
    if field_type in ["string", 'select', 'text', 'radio']:
        return StringType(variable_value)


def _do_operator_comparison(operator_type, operator_name, comparison_value):
    """
    Finds the method on the given operator_type and compares it to the
    given comparison_value.

    operator_type should be an instance of operators.BaseType
    comparison_value is whatever python type to compare to
    returns a bool
    :param operator_type:
    :param operator_name:
    :param comparison_value:
    :return:
    """

    def fallback(*args, **kwargs):
        raise AssertionError(
            "Operator {0} does not exist for type {1}".format(operator_name, operator_type.__class__.__name__)
        )

    method = getattr(operator_type, operator_name, fallback)
    if getattr(method, "input_type", "") == FIELD_NO_INPUT:
        return method()
    return method(comparison_value)


@contextlib.contextmanager
def action_exception_handler(defined_actions, method, action, successful_conditions):
    """
    :param defined_actions: 自定义action的类实例
    :param method: rule_method实现方法
    :param action: method的上下文
    :param successful_conditions: action匹配的规则
    :return:
    """
    # terminate_process的优先级: action > method
    terminate_process_list = [method.terminate_process]
    if "terminate_process" in action:
        terminate_process_list.append(action["terminate_process"])

    if terminate_process_list.pop():
        yield
    else:
        try:
            yield
        except Exception as error:
            logger.exception(error)
            defined_actions.failure_handler(error, action, successful_conditions)


def do_actions(actions, defined_actions, checked_conditions_results, rule, if_batch_run=True):
    """

    :param actions:             List of actions objects to be executed (defined in library)
                                Example:

                                .. code-block:: json

                                    {
                                        "name": "action name",
                                        "params": {
                                            "param1": value
                                        },
                                        "ignore_error": False
                                    }
    :param defined_actions:     Class with function that implement the logic for each possible action defined in
                                'actions' parameter
    :param checked_conditions_results:
    :param rule:                Rule that is being executed
    :param if_batch_run: batch run actions
    :return: None
    """

    # Get only conditions when result was TRUE
    successful_conditions = [x for x in checked_conditions_results if x[0]]

    def do_action(action):
        method_name = action["name"]
        action_params = action.get("params", {})

        method = getattr(defined_actions, method_name, None)

        if not method:
            raise AssertionError(
                "Action {0} is not defined in class {1}".format(method_name, defined_actions.__class__.__name__)
            )

        with action_exception_handler(defined_actions, method, action, successful_conditions):
            missing_params_with_default_value = utils.check_params_valid_for_method(
                method, action_params, method_type.METHOD_TYPE_ACTION
            )

            if missing_params_with_default_value:
                action_params = _set_default_values_for_missing_action_params(
                    method, missing_params_with_default_value, action_params
                )

            method_params = _build_action_parameters(method, action_params, rule, successful_conditions)
            result = method(**method_params)
            defined_actions.finish_handler(result, action, successful_conditions)

    if not if_batch_run:
        # 按顺序执行
        for action in actions:
            do_action(action)
        return

    action_threads = []
    for action in actions:
        action_threads.append(threading.Thread(target=do_action, args=[action]))

    for action_thread in action_threads:
        action_thread.start()

    for action_thread in action_threads:
        action_thread.join()


def _set_default_values_for_missing_action_params(method, missing_parameters_with_default_value, action_params):
    """
    Adds default parameter from method params to Action parameters.
    :param method: Action object.
    :param parameters_with_default_value: set of parameters which have a default value for Action parameters.
    :param action_params: Action parameters dict.
    :return: Modified action_params.
    """
    modified_action_params = {}
    if getattr(method, "params", None):
        for param in method.params:
            param_name = param["name"]
            if param_name in missing_parameters_with_default_value:
                default_value = param.get("defaultValue", None)
                if default_value is not None:
                    modified_action_params[param_name] = default_value
                    continue
            modified_action_params[param_name] = action_params[param_name]
    return modified_action_params


def _build_action_parameters(method, parameters, rule, conditions):
    """
    Adds extra parameters to the parameters defined for the method
    :param method:
    :param parameters:
    :param rule:
    :param conditions:
    :return:
    """
    extra_parameters = {"rule": rule, "conditions": conditions}

    return _build_parameters(method, parameters, extra_parameters)


def _build_variable_parameters(method, parameters, rule):
    """
    Adds extra parameters to the Variable's method parameters
    :param method:
    :param parameters:
    :param rule:
    :return:
    """
    extra_parameters = {
        "rule": rule,
    }

    return _build_parameters(method, parameters, extra_parameters)


def _build_parameters(method, parameters, extra_parameters):
    if getfullargspec(method).varkw is not None:
        method_params = extra_parameters
    else:
        method_params = {}

    method_params.update(parameters)

    return method_params
