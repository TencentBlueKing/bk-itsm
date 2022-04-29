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
from itsm.component.exceptions import FieldRequiredError
from .field import BaseField, MemberField, StringField


class BaseForm:
    """
    基础表单
    """

    @classmethod
    def declared_fields_schema(cls):
        """
        获取声明的字段结构
        :return: 
        """
        return [
            _object.get_field_schema(_attr)
            for _attr, _object in cls.__dict__.items()
            if isinstance(_object, BaseField) and _object.display
        ]

    @classmethod
    def declared_fields(cls):
        """
        声明的字段对象
        :return: 
        """
        return {_attr: _object for _attr, _object in cls.__dict__.items() if isinstance(_object, BaseField)}

    def __init__(self, params_schema, inputs=None):
        if inputs is None:
            inputs = {}
        self.params_schema = params_schema
        self.inputs = inputs

    def get_cleaned_data_or_error(self):
        """
        获取表单值
        :return: 
        """
        clean_data = {}
        related_fields = self.declared_fields()
        for _input in copy.deepcopy(self.params_schema):
            _clean_data = related_fields.get(_input['key']).to_internal_data(_input, self.inputs)
            clean_data.update({_input['key']: _clean_data})
        return clean_data

    def to_representation_data(self, **kwargs):
        """
        获取字段的展示值
        :return: 
        """
        data = []
        related_fields = self.declared_fields()
        params = {param['key']: param for param in self.params_schema}
        for key, related_field in related_fields.items():
            param = params.get(key) or copy.deepcopy(related_field.default)
            param.update({"key": key})
            clean_data = related_field.to_representation_data(param, self.inputs, **kwargs)
            if kwargs.get("flat") and isinstance(clean_data, list):
                data.extend(clean_data)
                continue
            field_schema = related_field.get_field_schema(key)
            field_schema.update({"value": clean_data, "show_result": True})
            data.append(field_schema)
        return data

    def validate_params(self):
        """输入参数配置校验"""
        related_fields = self.declared_fields()
        for field_key, field in related_fields:
            if not field.is_required:
                continue
            if field_key not in self.params_schema:
                raise FieldRequiredError("字段【{}】缺失".format(field['name']))
                # 每一个字段需要有自身的参数校验填写
            if not field.to_internal_data(self.params_schema['field_key'], self.inputs):
                raise FieldRequiredError("字段【{}】缺失".format(field['name']))


class SMSMessageForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    receivers = MemberField(name="收件人", field_type="MULTI_MEMBERS")
    content = StringField(name="内容", field_type="TEXT")


class WechatMessageForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    title = StringField(name="微信主题")
    receivers = MemberField(name="收件人", field_type="MULTI_MEMBERS")
    content = StringField(name="内容", field_type="TEXT", is_tips=True, tips="文本格式支持html，如果需要换行，请在行尾加&lt;br/&gt;")


class EmailMessageForms(BaseForm):
    """
    发送邮件通知的输入数据格式
    """

    title = StringField(name="邮件标题")
    receivers = MemberField(name="收件人", field_type="MULTI_MEMBERS")
    content = StringField(name="内容", field_type="TEXT", is_tips=True, tips="文本格式支持html，如果需要换行，请在行尾加 &lt;br/&gt;")


class BaseMessageForms(BaseForm):
    """
    发送通用通知的输入数据格式
    """

    title = StringField(name="标题")
    receivers = MemberField(name="收件人", field_type="MULTI_MEMBERS")
    content = StringField(name="内容", field_type="TEXT")
