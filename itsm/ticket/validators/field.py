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

import datetime
import re


from django.utils.translation import ugettext as _
from pipeline.utils.boolrule import BoolRule
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from itsm.component.constants import (
    BASE_MODEL,
    FIELD_BACK_MSG,
    FIELD_TERM_MSG,
    LEN_MIDDLE,
    REGEX_CHOICES,
    SHOW_BY_CONDITION,
    TABLE,
)
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.exceptions import ParamError
from itsm.component.utils.basic import Regex, walk
from itsm.component.utils.bk_bunch import Bunch, bunchify, unbunchify
from itsm.component.utils.conversion import format_exp_value, show_conditions_validate
from itsm.postman.constants import RPC_CODE
from itsm.postman.models import RemoteApiInstance
from itsm.postman.rpc.core.request import CompRequest
from itsm.service.models import SysDict
from itsm.ticket.models import TicketField, TicketGlobalVariable
from itsm.ticket.serializers import FieldSerializer


def field_validate(field, state_fields, key_value, **kwargs):
    """单个字段校验"""
    if field["key"] in [FIELD_BACK_MSG, FIELD_TERM_MSG]:
        return

    field_obj = state_fields.get(field["key"], None)

    if field_obj is None:
        raise serializers.ValidationError(_("【{}】字段不存在，请联系管理员").format(field["key"]))

    field_obj = bunchify(field_obj)

    required_validate(field, field_obj, key_value, skip_readonly=True)
    # field_required_validate 已经校验是否必填
    if not str(field["value"]):
        return

    if field_obj.key == "title" and len(key_value["params_title"]) > LEN_MIDDLE:
        raise serializers.ValidationError(_("标题不能超过120个字符"))

    choice_validate(field, field_obj, key_value, **kwargs)
    regex_validate(field, field_obj, kwargs.get("ticket", None))
    custom_regex_validate(field, field_obj)


def required_validate(field, field_obj, key_value, skip_readonly=False):
    validate_type = field_obj.validate_type

    # 字段非必填且无数据时
    if validate_type == "OPTION" and not field["value"]:
        return

    # 是否只读校验，当字段有值后，不能被更改, 建单不做校验
    if field_obj.is_readonly and not skip_readonly:
        if field_obj._value and field["value"] != field_obj._value:
            raise ParamError(_("【{}】只读字段不允许修改").format(field_obj.name))

    # 隐藏条件校验
    if field_obj.show_type == SHOW_BY_CONDITION:
        result = show_conditions_validate(field_obj.show_conditions, key_value)
        if result:
            # 隐藏条件成立且没数据，若有数据，则继续进行校验
            if not field["value"]:
                return
        else:
            if not field["value"]:
                raise ParamError(_("【{}】为必填项").format(field_obj.name))

    if field_obj.type in ["CUSTOMTABLE", "TABLE"]:
        if not field["value"]:
            raise serializers.ValidationError(_("【{}】为必填项").format(field_obj.name))
        # 表格类型字段的必填校验

        field_column_schema = (
            field_obj.choice
            if field_obj.type == "TABLE"
            else field_obj.meta.get("columns", [])
        )
        required_columns = {
            choice["key"]: choice["name"]
            for choice in field_column_schema
            if choice.get("required") is True
        }
        if not required_columns:
            return

        for index, row in enumerate(field["value"]):
            for column, value in row.items():
                if column in required_columns and not value:
                    raise serializers.ValidationError(
                        _("表格字段【{field_name}】的第【{index}】行【{column_name}】为必填项").format(
                            field_name=field_obj.name,
                            index=index + 1,
                            column_name=required_columns[column],
                        )
                    )

    if isinstance(field["value"], (int, str, bool)) and not str(field["value"]):
        raise serializers.ValidationError(_("【{}】为必填项").format(field_obj.name))


def choice_validate(field, field_obj, key_value, **kwargs):
    """
    选择类字段校验
    """
    if field_obj.type not in [
        "SELECT",
        "RADIO",
        "CHECKBOX",
        "MULTISELECT",
        "TREESELECT",
    ]:
        return

    if field_obj.source_type == "CUSTOM_API":
        return

    choice = get_choice(field_obj, key_value, **kwargs)

    if not choice:
        raise serializers.ValidationError(_("【%s】选项不存在，请联系管理员") % field_obj.key)

    # 更新choice
    field["choice"] = choice

    if field_obj.type == "TREESELECT":
        if not choice:
            raise serializers.ValidationError(_("数据字典不存在，请检查字典编码: %s") % field_obj.key)
        key_choice = [str(item["id"]) for _choice in choice for item in walk(_choice)]
    else:
        key_choice = [str(item["key"]) for item in choice]

    if field_obj.type in ["SELECT", "RADIO"]:
        if str(field["value"]) not in key_choice:
            raise serializers.ValidationError(
                _("【{}】选项不匹配，请重新选择").format(field_obj.name)
            )

    if field_obj.type in ["CHECKBOX", "MULTISELECT"]:
        if not set(field["value"].split(",")).issubset(key_choice):
            raise serializers.ValidationError(
                _("【{}】选项不匹配，请重新选择").format(field_obj.name)
            )

    if field_obj.type == "TREESELECT":
        if str(field["value"]) not in key_choice:
            raise serializers.ValidationError(
                _("【{}】选项不匹配，请重新选择").format(field_obj.name)
            )


def get_choice(field_obj, key_value, **kwargs):
    if field_obj.source_type == "CUSTOM":
        return field_obj.choice

    if field_obj.source_type == "DATADICT":
        view_type = "tree" if field_obj.type == "TREESELECT" else "list"
        return SysDict.get_data_by_key(field_obj.source_uri, view_type)

    if field_obj.source_type == "API":
        return RemoteApiInstance.get_api_choice_by_instance_id(
            field_obj.api_instance_id, field_obj.kv_relation, key_value
        )["data"]

    if field_obj.source_type == "RPC":
        if isinstance(field_obj, Bunch):
            field_data = unbunchify(field_obj)
        else:
            field_data = FieldSerializer(field_obj).data
        result, params = CompRequest.parse_params(field_data)

        # 参数解析失败
        if not result:
            return []
        if kwargs.get("request", None):
            request = kwargs.get("request", None)
            request.data.update(**field_data)
        else:
            request = CompRequest(field_data)
        request.data.update(**params)
        component_cls = ComponentLibrary.get_component_class(
            "rpc", request.data[RPC_CODE]
        )
        component_obj = component_cls(request)
        return component_obj.invoke()


def custom_regex_validate(field, field_obj):
    custom_regex = field_obj.custom_regex
    if not custom_regex:
        return
    try:
        if not re.match(r"{}".format(custom_regex), str(field["value"])):
            raise serializers.ValidationError(_("用户输入的值不符合自定义正则规则"))
    except Exception as e:
        raise serializers.ValidationError(_("自定义正则出现异常， error = {}".format(e)))


def validate_expression(field, expression, ticket):
    VALIDATE_TYPE_MAP = {
        "DATE": validate_date_expression,
        "INT": validate_int_expression,
        "DATETIME": validate_datetime_expression,
    }
    try:
        return VALIDATE_TYPE_MAP[expression.type](field, expression, ticket)
    except Exception:
        return False


def validate_int_expression(field, expression, ticket):
    source = field["value"]
    if expression.source == "field":
        target_value = ticket.fields.get(key=expression.key).value
    else:
        target_value = expression.value

    exp = "{}{}{}".format(source, expression.condition, target_value)
    return BoolRule(exp).test()


def validate_datetime_expression(field, expression, ticket):
    source_timestamp = datetime.datetime.timestamp(
        datetime.datetime.strptime(field["value"], "%Y-%m-%d %H:%M:%S")
    )
    if expression.source == "field":
        if expression.key == "ticket_create_at":
            target_value = ticket.create_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            target_value = ticket.fields.get(key=expression.key).value
    elif expression.source == "system":
        if expression.key == "system_time":
            target_value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            target_value = ""
    else:
        target_value = expression.value

    target_timestamp = datetime.datetime.timestamp(
        datetime.datetime.strptime(target_value, "%Y-%m-%d %H:%M:%S")
    )
    exp = "{}{}{}".format(source_timestamp, expression.condition, target_timestamp)
    return BoolRule(exp).test()


def validate_date_expression(field, expression, ticket):
    source_timestamp = datetime.datetime.timestamp(
        datetime.datetime.strptime(field["value"], "%Y-%m-%d")
    )
    if expression.source == "field":
        if expression.key == "ticket_create_at":
            target_value = ticket.create_at
        else:
            target_value = ticket.fields.get(key=expression.key).value
    elif expression.source == "system":
        if expression.key == "system_time":
            target_value = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            target_value = ""
    else:
        target_value = expression.value
    target_timestamp = datetime.datetime.timestamp(
        datetime.datetime.strptime(target_value, "%Y-%m-%d")
    )
    exp = "{}{}{}".format(source_timestamp, expression.condition, target_timestamp)
    return BoolRule(exp).test()


def regex_validate(field, field_obj, ticket=None):
    regex = field_obj.regex

    regex_list = []
    for choice in list(REGEX_CHOICES.values()):
        regex_list.extend(choice)

    if regex and regex not in [reg[0] for reg in list(set(regex_list))]:
        raise serializers.ValidationError(_("该正则规则不在可选范围内"))

    if regex in ["AFTER_DATE", "BEFORE_DATE", "AFTER_TIME", "BEFORE_TIME"]:
        RegexValidator(field_obj.name, regex).validate(field["value"])

    if regex == "ASSOCIATED_FIELD_VALIDATION" and ticket:
        # 联合字段校验
        rule = field_obj.regex_config.rule
        if rule.expressions:
            results = []
            for expression in rule.expressions:
                results.append(validate_expression(field, expression, ticket))

            expression_type = {"and": all, "or": any}
            if not expression_type.get(rule.type, any)(results):
                raise serializers.ValidationError(
                    _("字段[{}]关联规则不满足条件，请检查".format(field_obj.name))
                )

    elif regex and regex != "EMPTY":
        if field_obj.type in ["INT", "STRING"]:
            RegexValidator(field_obj.name, regex).validate(str(field["value"]))

        elif field_obj.type == "TEXT":
            if not isinstance(field["value"], list):
                # 这里不能全部采用转为list的方式，需要根据field的类型
                field_value = (
                    field["value"]
                    .strip()
                    .replace("\n", ",")
                    .replace(";", ",")
                    .split(",")
                )
            else:
                field_value = [field["value"]]

            for value in field_value:
                RegexValidator(field_obj.name, regex).validate(value)


class RegexValidator(Regex):
    def __init__(self, field_name, regex):
        super(RegexValidator, self).__init__(validate_type=regex.lower())
        self.field_name = field_name
        self.validate_type_action = {
            "after_date": "date",
            "before_date": "date",
            "after_time": "time",
            "before_time": "time",
        }

    def validate(self, value):
        action = self.validate_type_action.get(self.validate_type)
        if action and hasattr(self, "%s_validate" % action):
            getattr(self, "%s_validate" % action)(value)
        else:
            try:
                super(RegexValidator, self).validate(value)
            except ValidationError as e:
                raise serializers.ValidationError(
                    "【{}】{}".format(self.field_name, str(",".join(e.detail)))
                )

    def date_validate(self, value):
        """日期的校验"""
        # ("AFTER_DATE", u"当前日期之后"),
        # ("BEFORE_DATE", u"当前日期之前"),
        if not value:
            return

        try:
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise serializers.ValidationError(
                _("【{}】{} 不匹配日期格式{}").format(self.field_name, value, "%Y-%m-%d")
            )

        if self.validate_type == "after_date" and value < datetime.datetime.now():
            raise serializers.ValidationError(
                _("【{}】{} 不在当前日期之后").format(self.field_name, value.date())
            )

        if self.validate_type == "before_date" and value > datetime.datetime.now():
            raise serializers.ValidationError(
                _("【{}】{} 不在当前日期之前").format(self.field_name, value.date())
            )

    def time_validate(self, value):
        """时间的校验"""
        # ("AFTER_TIME", u"当前时间之后"),
        # ("BEFORE_TIME", u"当前时间之前")
        if not value:
            return

        try:
            value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise serializers.ValidationError(
                _("【{}】{} 不匹配时间格式{}").format(
                    self.field_name, value, "%Y-%m-%d %H:%M:%S"
                )
            )

        if self.validate_type == "after_time" and value < datetime.datetime.now():
            raise serializers.ValidationError(
                _("【{}】{} 不在当前时间之后").format(self.field_name, value)
            )

        if self.validate_type == "before_time" and value > datetime.datetime.now():
            raise serializers.ValidationError(
                _("【{}】{} 不在当前时间之前").format(self.field_name, value)
            )


def edit_field_validate(field, **kwargs):
    """修改单个字段校验"""

    try:
        field_obj = TicketField.objects.get(id=field["id"])
    except TicketField.DoesNotExist:
        raise ParamError(_("【{}】字段不存在，请联系管理员").format(field["key"]))

    if field_obj.source not in [TABLE, BASE_MODEL]:
        raise ParamError(_("非公共字段不允许修改"))

    key_value = {
        "params_%s" % field["key"]: format_exp_value(field["type"], field["_value"])
        for field in field_obj.ticket.fields.filter(_value__isnull=False).values(
            "key", "type", "_value"
        )
    }

    key_value.update(
        {
            "params_%s" % item["key"]: item["value"]
            for item in TicketGlobalVariable.objects.filter(
                ticket_id=field_obj.ticket_id
            ).values("key", "value")
        }
    )

    key_value.update(
        {"params_" + field["key"]: format_exp_value(field["type"], field["value"])}
    )

    required_validate(field, field_obj, key_value, skip_readonly=True)
    if field_obj.key == "title" and len(key_value["params_title"]) > LEN_MIDDLE:
        raise serializers.ValidationError(_("标题不能超过120个字符"))

    # 是否必填已经校验
    if not str(field["value"]):
        return field, field_obj

    choice_validate(field, field_obj, key_value, **kwargs)
    regex_validate(field, field_obj)
    custom_regex_validate(field, field_obj)
    return field, field_obj
