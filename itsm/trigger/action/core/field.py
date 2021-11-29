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

# 不支持的 字段附件，表格， API字段

import copy
import datetime
import re
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from mako.template import Template

from common.log import logger
from itsm.role.models import UserRole
from itsm.postman.models import RemoteApi
from itsm.component.constants import DEFAULT_BK_BIZ_ID, EMPTY_DICT, PROCESSOR_CHOICES, PERSON
from itsm.component.utils.basic import list_by_separator, dotted_name, normal_name

VAR_STR_MATCH = re.compile(r"\$\{\s*[\w\|]+\s*\}")


class BaseField:
    """
    基础字段
    """

    enabled_field_types = []
    default_field_type = 'STRING'

    def __init__(
        self,
        name,
        field_type=None,
        required=True,
        use_variable=True,
        choice=None,
        display=True,
        default="",
        desc="",
        source_type="",
        source_uri="",
        is_tips=False,
        tips="",
    ):
        """ 
        {
            "type": "STRING|TEXT|SELECT|MULTISELECT|MEMBERS|",
            "choice": [],
            "name": "标题",
            "value": "rwetwrwrw",
            "display": true,
            "display_value": null
            "use_variable"：是否可以使用变量引用
        }
        """
        # 代码规范兼容
        if choice is None:
            choice = []
        
        self.type = self.default_field_type
        self.choice = choice
        self.name = name
        self.display = display
        self.default = default
        self.required = required
        self.desc = desc
        self.source_type = source_type
        self.source_uri = source_uri
        self.use_variable = use_variable
        self.set_field_type(field_type)
        self.is_tips = is_tips
        self.tips = tips

    def validate(self):
        """根据字段内容进行校验"""

        raise NotImplementedError

    def to_internal_data(self, value, context=None, **kwargs):
        raise NotImplementedError

    def to_representation_data(self, value, context=None, **kwargs):
        """
        用来做展示的内容
        """
        clean_data = self.to_internal_data(value, context, display=True)
        if isinstance(clean_data, list):
            clean_data = [str(item) for item in clean_data]
            clean_data = ",".join(clean_data)
        return clean_data

    def set_field_type(self, field_type):
        self.type = field_type if field_type in self.enabled_field_types else self.default_field_type

    def get_field_schema(self, key):
        return {
            "key": key,
            "type": self.type,
            "choice": self.choice() if callable(self.choice) else self.choice,
            "name": _(self.name),
            "display": self.display,
            "required": self.required,
            "default": self.default,
            "desc": self.desc,
            "source_type": self.source_type,
            "source_uri": self.source_uri,
            "use_variable": self.use_variable,
            "meta": self.meta if hasattr(self, "meta") else {},
            "tips": _(self.tips),
            "is_tips": self.is_tips,
        }


class ApiSourceField(BaseField):
    enabled_field_types = ["API"]
    default_field_type = 'API'

    def validate(self, value):
        """根据字段内容进行校验"""
        try:
            RemoteApi.objects.get(id=value)
        except RemoteApi.DoesNotExist:
            ValidationError(_("所选择的API配置对象不存在"))
        return value

    def to_internal_data(self, value, context=None, **kwargs):
        """
        :param value: 输入值
        :param context: 
        :return: 
        """
        parse_tool = ParamParseTool(context)
        return self.validate(parse_tool(param=value, **kwargs))


class ApiInfoField(BaseField):
    enabled_field_types = ["API_INFO"]
    default_field_type = 'API_INFO'

    def validate(self, value):
        """根据字段内容进行校验"""

        return value

    def to_internal_data(self, value, context=None, **kwargs):
        """
        根据输入格式来对数据做渲染
        :param value: 
        :param context: 
        :return: 
        """
        parse_tool = ParamParseTool(context)

        def _dict_clean(dict_value):

            if dict_value.get("is_leaf"):
                return _leaf_clean(dict_value)

            clean_data = {}
            for key, _value in dict_value.items():
                if key in ["is_leaf", "ref_type", "value"]:
                    continue

                if not isinstance(_value, (dict, list)):
                    _clean_value = _leaf_clean(_value)

                if isinstance(_value, list):
                    _clean_value = _list_clean(_value)

                if isinstance(_value, dict):
                    _clean_value = _dict_clean(_value)

                clean_data[key] = _clean_value

            return clean_data

        def _list_clean(list_value):
            clean_data = []
            for _value in list_value:
                if not isinstance(_value, (dict, list)):
                    _clean_value = _leaf_clean(_value)

                if isinstance(_value, list):
                    _clean_value = _list_clean(_value)

                if isinstance(_value, dict):
                    _clean_value = _dict_clean(_value)

                clean_data.append(_clean_value)
            return clean_data

        def _datetime_clean(_value):
            return _value.strftime('%Y-%m-%d %H:%M:%S')

        def _date_clean(_value):
            return _value.strftime('%Y-%m-%d')
        
        def _leaf_clean(_value):
            result = self.validate(parse_tool(param=_value, **kwargs))
            if isinstance(result, datetime.datetime):
                return _datetime_clean(result)
            if isinstance(result, datetime.date):
                return _date_clean(result)
            return result

        value = value.get("value")
        if not isinstance(value, (dict, list)):
            return _leaf_clean(value)

        if isinstance(value, list):
            return _list_clean(value)

        if isinstance(value, dict):
            return _dict_clean(value)


class MemberField(BaseField):
    """
    多功能的人员选择器
    """

    enabled_field_types = ["MEMBERS", "MULTI_MEMBERS"]
    default_field_type = 'MEMBERS'

    def __init__(self, name, **kwargs):
        self.convert_to_users = kwargs.pop("convert_to_users", True)
        super(MemberField, self).__init__(name, **kwargs)

    def validate(self):
        # TODO 校验还没做
        return True

    def to_internal_data(self, value, context=None, **kwargs):

        if self.convert_to_users:
            return self._convert_to_users(value['value'], context, **kwargs)
        else:
            members = self._direct_convert(value['value'], context, **kwargs)

        if kwargs.get("display"):
            return self.display_convert(members)

        return members

    @staticmethod
    def _convert_to_users(member_value, context, **kwargs):
        members = []
        parse_tool = ParamParseTool(context)
        bk_biz_id = context.get("bk_biz_id", DEFAULT_BK_BIZ_ID)
        for member in copy.deepcopy(member_value):
            member["value"] = UserRole.get_users_by_type(
                bk_biz_id, member['value']['member_type'], member['value']['members']
            )
            parse_people = parse_tool(param=member)
            members.extend(parse_people if isinstance(parse_people, list) else list_by_separator(parse_people))
        return members

    def _direct_convert(self, member_value, context, **kwargs):
        # 直接转换
        members = []
        parse_tool = ParamParseTool(context)
        for member in member_value:
            parse_value = {"ref_type": member['ref_type'], "value": member['value']['members']}
            member['value']['members'] = dotted_name(parse_tool(param=parse_value))
            if member['value']['member_type'] in ['VARIABLE', "EMPTY"]:
                member['value']['member_type'] = 'PERSON'
            if self.type == 'MEMBERS':
                members = member['value']
                break
            members.append(member['value'])
        return members

    def display_convert(self, members):

        if isinstance(members, dict):
            return self.get_members_display(members)
        members_display = []
        for member in members:
            members_display.append(self.get_members_display(member))

    @staticmethod
    def get_members_display(member):
        members_type = dict(PROCESSOR_CHOICES)

        if member['member_type'] == PERSON:
            display_value = normal_name(member['members'])
        else:
            display_value = ",".join(
                UserRole.objects.filter(id__in=list_by_separator(member['members'])).values_list("name", flat=True)
            )
        return ("{}:{}").format(members_type.get(member['member_type']), display_value)


class SelectField(BaseField):
    """
    单项选择字段
    """

    enabled_field_types = ["SELECT", "RADIO"]
    default_field_type = 'SELECT'

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        try:
            return parse_tool(param=value)
        except TypeError:
            raise


class MultiSelectField(BaseField):
    """多项选择字段"""

    enabled_field_types = ["MULTISELECT", "CHECKBOX"]
    default_field_type = 'MULTISELECT'

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        try:
            return parse_tool(param=value, **kwargs)
        except TypeError:
            raise


class StringField(BaseField):
    """
    输入框和文本
    """

    enabled_field_types = ["STRING", "TEXT"]
    default_field_type = 'STRING'

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        """
        { 
        "key": "content",
        "value": "工单编号:${sn} 标题：${title}",
        "ref_type": "import"
        }
        """
        parse_tool = ParamParseTool(context)
        return parse_tool(param=value, **kwargs)


class NumberField(BaseField):
    """
    输入框和文本
    """

    enabled_field_types = ["NUMBER"]
    default_field_type = "NUMBER"

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        try:
            return int(parse_tool(param=value, **kwargs))
        except TypeError:
            raise


class JSONField(BaseField):
    enabled_field_types = ["JSON"]
    default_field_type = "JSON"

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        return parse_tool(param=value, **kwargs)


class DatetimeField(BaseField):
    """
    时间格式
    """

    enabled_field_types = ["DATETIME", "DATE"]
    default_field_type = "DATETIME"

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        return parse_tool(param=value, **kwargs)


class SubComponentField(BaseField):
    """
        时间格式
        """

    enabled_field_types = ["SUBCOMPONENT"]
    default_field_type = "SUBCOMPONENT"
    sub_components = []

    def __init__(self, sub_components, name, **kwargs):
        self.sub_components = sub_components
        super(SubComponentField, self).__init__(name, **kwargs)

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        return value

    def to_representation_data(self, value, context=None, sub_actions=None, flat=False):
        """
        组装展示的时候数据组装
        """
        sub_component_data = []
        if sub_actions is None:
            return sub_component_data
        for sub_action in sub_actions:
            clean_data = sub_action.to_representation_data()
            if flat:
                sub_component_data.extend(clean_data)
            sub_component_data.append({"code": sub_action.code, "name": sub_action.name, "fields": clean_data})

        return sub_component_data

    def get_field_schema(self, key):
        """
            子响应函数组的格式返回
            :param key: 
            :return: 
            """
        schema = super(SubComponentField, self).get_field_schema(key)
        schema['sub_components'] = []
        for _component in self.sub_components:
            sub_component_field_schema = _component.get_inputs()
            schema['sub_components'].append(
                dict(key=_component.code, name=_component.name, field_schema=sub_component_field_schema)
            )
        return schema


class CascadeField(BaseField):
    enabled_field_types = ["CASCADE"]
    default_field_type = "CASCADE"

    def validate(self):
        return True

    def to_internal_data(self, value, context=None, **kwargs):
        parse_tool = ParamParseTool(context)
        return parse_tool(param=value, **kwargs)


class ParamParseTool:
    """
    {
        "key": "receivers",
        "value": "["current_processors","history_processors"]
        "ref_type":"reference|import|direct"
    }
    TODO 需要丰富 引用多个变量的时候，数据格式如何定义
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, *args, **kwargs):
        param = kwargs.get("param", EMPTY_DICT)
        parse_method = getattr(self, "{}_parse".format(param.get('ref_type', 'direct')), self.direct_parse)
        if parse_method is None:
            return param['value']
        kwargs.update(param_key=param.get("key"))
        return parse_method(param['value'], **kwargs)

    def import_parse(self, value, **kwargs):
        try:
            return Template(value).render(**self.context)
        except BaseException:
            # 可能存在参数不存在的问题，所以需要进行处理
            logger.exception("error params value %s context %s" % (value, self.context))
            return value

    def reference_parse(self, value, **kwargs):
        # 引用变量的时候是否需要区分多选和单选
        reference_keys = value.split(",") if isinstance(value, str) else value
        display = kwargs.get("display", False)
        if len(reference_keys) == 1:
            # 只引用了一个参数的使用
            key = "{}__display".format(reference_keys[0]) if display else reference_keys[0]
            return self.context.get(key) or self.context.get(reference_keys[0])
        if display:
            return ",".join(
                [
                    self.context.get("{}__display".format(key), self.context[key])
                    for key in reference_keys
                    if key in self.context
                ]
            )
        return ",".join([self.context.get(key) for key in reference_keys if key in self.context])

    def direct_parse(self, value, **kwargs):
        if isinstance(value, str) and VAR_STR_MATCH.findall(value):
            return self.import_parse(value, **kwargs)

        display = kwargs.get("display", False)
        if display:
            return self.context.get("{}__display".format(kwargs.get("param_key"))) or value
        return value
