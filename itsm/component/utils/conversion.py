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
import copy
import json
import re

from django.utils.translation import ugettext as _
from mako.template import Template

from itsm.component.exceptions import ParamError
from itsm.component.utils.bk_bunch import bunchify
from pipeline.utils.boolrule import BoolRule

VAR_STR_MATCH = re.compile(r"\$\{\s*[\w\|]+\s*\}")


def params_type_conversion(params, schema):
    """
    :param params:  输入的原始参数值
    :param schema: 请求参数内容
    :param required: 必要的字段
    :return:
    """

    if params is None:
        return
    if schema["type"] == "object":
        for k, v in list(schema["properties"].items()):
            result = params_type_conversion(params.get(k), v)
            if result is not None:
                params[k] = result
    if schema["type"] == "array":
        if not schema.get("items"):
            return None
        for i in range(len(params)):
            result = params_type_conversion(params[i], schema["items"])
            if result is not None:
                params[i] = result
    if schema["type"] == "number":
        return int(params) if params else schema["default"]
    if schema["type"] == "boolean":
        if params:
            return True
        else:
            return False
    if schema["type"] == "string":
        import ast

        try:
            value = ast.literal_eval(params)
            if not isinstance(value, (dict, list)):
                return params
            return json.dumps(value)
        except Exception:
            return params
    return None


def build_params_by_mako_template(api_config_query_params, params):
    """
    根据引用内容进行渲染
    :param api_config_query_params: 输入的对象
    :param params: 对应的参数
    :return:
    """
    try:
        if not isinstance(api_config_query_params, dict):
            # 待解析的数据必须是数据字典
            return False, "error query params %s" % api_config_query_params
        for key, value in api_config_query_params.items():
            if isinstance(value, str):
                # 如果是字符串且需要转换的
                api_config_query_params[key] = Template(value).render(**params)
            elif isinstance(value, dict):
                # 如果是字典，直接转换
                result, api_config_query_params[key] = build_params_by_mako_template(
                    value, params
                )
            elif isinstance(value, list):
                str_value = json.dumps(value)
                if not VAR_STR_MATCH.findall(json.dumps(str_value)):
                    # 如果是列表，先检测是否需哟进行替换
                    continue
                new_value = []
                for item_value in value:
                    # 对每一个元素进行转换
                    if isinstance(item_value, dict):
                        _, new_item = build_params_by_mako_template(item_value, params)
                        new_value.append(new_item)
                        continue
                    new_value.append(Template(item_value).render(**params))
                api_config_query_params[key] = new_value
        return True, api_config_query_params
    except Exception as e:
        return False, str(e)


def format_exp_value(field_type, exp_value, show_condition=False):
    """不同类型字段值的格式化"""
    if exp_value is None:
        return exp_value

    if field_type in ["INT"]:
        if str(exp_value).isdigit():
            return int(exp_value)
        return float(exp_value)

    if field_type in [
        "STRING",
        "TEXT",
        "DATE",
        "DATETIME",
        "BOOLEAN",
        "SELECT",
        "TREESELECT",
        "RADIO",
    ]:
        return exp_value

    if field_type in ["MULTISELECT", "CHECKBOX"] and exp_value is not None:
        exp_value = tuple([str(x) for x in exp_value.split(",")])
        # 单元素元组无法正常规则判定

        if show_condition:
            if len(exp_value) == 1:
                exp_value = "('{}')".format(exp_value[0])
        return exp_value

    if field_type in ["CUSTOMTABLE", "TABLE"]:
        return json.dumps(exp_value)
    # 其他的直接返回字段
    return exp_value


def get_exp_template(exp_type):
    """表达式模板"""
    # TODO 后面根据业务需求优化类型选择
    if exp_type in ["INT", "BOOLEAN"]:
        return "{key} {condition} {value}"

    if exp_type in [
        "STRING",
        "TEXT",
        "SELECT",
        "TREESELECT",
        "RADIO",
        "DATE",
        "DATETIME",
    ]:
        return "'{key}' {condition} '{value}'"

    if exp_type in ["MULTISELECT", "CHECKBOX"]:
        return "{key} {condition} {value}"

    return "'{key}' {condition} '{value}'"


# {"expressions": [{"key": "SHIFOUYINCANG", "choiceList": [{"isDisabled": false, "id": "SHI", "name": "\u662f"},
#                                                          {"isDisabled": false, "id": "FOU", "name": "\u5426"}],
#                   "type": "RADIO", "condition": "==", "value": "SHI"}], "type": "and"}


def field_conditions_conversion(condition):
    condition = bunchify(condition)
    inner_expressions = []

    for exp in condition.expressions:
        if exp.key == "G_INT_1":
            evaluation = "1==1"
        else:
            mapping = {"string": "STRING", "number": "INT", "boolean": "BOOLEAN"}
            e_type = mapping.get(exp.type, exp.type)

            template = get_exp_template(e_type)
            value = format_exp_value(e_type, exp.value, show_condition=True)

            evaluation = template.format(
                key="${params_%s}" % exp.key, condition=exp.condition, value=value
            )
        inner_expressions.append(evaluation)

    expression_type = " {} ".format(condition.type)
    return expression_type.join(inner_expressions)


def conditions_conversion(condition):
    """构造网关条件表达式"""

    condition = bunchify(condition)

    expressions = []

    for expression in condition.expressions:

        inner_expressions = []
        for exp in expression.expressions:

            if exp.key == "G_INT_1":
                evaluation = "1==1"
            else:
                mapping = {"string": "STRING", "number": "INT", "boolean": "BOOLEAN"}
                e_type = mapping.get(exp.type, exp.type)

                template = get_exp_template(e_type)
                value = format_exp_value(e_type, exp.value)

                evaluation = template.format(
                    key="${params_%s}" % exp.key, condition=exp.condition, value=value
                )
            inner_expressions.append(evaluation)

        expression_type = " {} ".format(expression.type)
        expressions.append(expression_type.join(inner_expressions))

    return condition.type.join([" ({}) ".format(e) for e in expressions])


def build_conditions_by_mako_template(condition, rsp):
    try:
        condition = Template(condition).render(**rsp)
        return True, condition
    except Exception as e:
        return False, str(e)


rsp = {
    "message": "success",
    "code": 0,
    "data": {
        "count": 8,
        "info": [
            {"bk_set_name": _("空闲机池")},
            {"bk_set_name": _("故障自愈")},
            {"bk_set_name": _("数据服务模块")},
            {"bk_set_name": _("公共组件")},
            {"bk_set_name": _("集成平台")},
            {"bk_set_name": _("作业平台")},
            {"bk_set_name": _("配置平台")},
            {"bk_set_name": _("管控平台")},
        ],
    },
    "result": "true",
    "request_id": "fe61c60c11b34ec4881182532c39edba",
    "msg": "success",
}


def rsp_conversion(rsp):
    for key, value in list(rsp.items()):
        if isinstance(value, dict):
            rsp_conversion(value)
        rsp["params_" + key] = rsp.pop(key)


def show_conditions_validate(show_conditions, key_value):
    conditions = field_conditions_conversion(show_conditions)
    key_value = copy.deepcopy(key_value)

    for key, value in key_value.items():
        if isinstance(value, tuple):
            if len(value) == 1:
                key_value[key] = "('{}')".format(value[0])

    b_result, b_conditions = build_conditions_by_mako_template(conditions, key_value)
    if not b_result:
        raise ParamError(_("参数转换失败，请联系管理员"))
    return BoolRule(b_conditions).test()
