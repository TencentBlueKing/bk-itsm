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

from django.test import TestCase

from itsm.trigger.action.core import StringField, NumberField, MemberField, SelectField, ApiInfoField
from itsm.trigger.action.components.modify_ticket_status import get_ticket_status_names


class TriggerFieldTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.inputs_field = StringField(name="hahahhahah", field_type="TEXT")
        self.number_field = NumberField(name="kkfdsjfkjdsf", field_type="TEXT")
        self.member_field = MemberField(name="人员")
        self.member_role_field = MemberField(name="角色", convert_to_users=False)
        self.select_field = SelectField(name="选择框", choice=get_ticket_status_names)
        self.context = {
            "sn": "NOqwew12312312312321321321321321321",
            "title": "haklajfkldsjfkladjsfkdshahhahfdshfds",
            "current_processors": "admin1,admin2,admin3",
            "creator": "admin4",
            "number": '123',
        }
        super(TriggerFieldTestCase, self).__init__(*args, **kwargs)

    def test_import_format(self):
        inputs = {"key": "inputs_field", "value": "【ITSM通知】您有待处理工单${sn}", "ref_type": "import"}
        value = self.inputs_field.to_internal_data(inputs, self.context)
        self.assertEquals(value, "【ITSM通知】您有待处理工单NOqwew12312312312321321321321321321")

    def test_custom_import_format(self):
        inputs = {"key": "inputs_field", "value": "【ITSM通知】您有待处理工单${sn}", "ref_type": "custom"}
        value = self.inputs_field.to_internal_data(inputs, self.context)
        self.assertEquals(value, "【ITSM通知】您有待处理工单NOqwew12312312312321321321321321321")

    def test_refrence_format(self):
        inputs = {"key": "inputs_field", "value": "title", "ref_type": "reference"}
        value = self.inputs_field.to_internal_data(inputs, self.context)
        self.assertEquals(value, "haklajfkldsjfkladjsfkdshahhahfdshfds")

    def test_number_format(self):
        inputs = {"key": "number_field", "value": "number", "ref_type": "reference"}
        value = self.number_field.to_internal_data(inputs, self.context)
        self.assertEquals(value, 123)

    def test_member_format(self):
        inputs = {
            "key": "member_field",
            "value": [
                {"ref_type": "reference", "value": {"members": "current_processors,creator", "member_type": "EMPTY"}}
            ],
        }
        value = self.member_field.to_internal_data(inputs, self.context)
        self.assertEquals(set(value), set("admin1,admin2,admin3,admin4".split(",")))

    def test_role_format(self):
        inputs = {
            "key": "member_field",
            "value": [
                {"ref_type": "custom", "value": {"members": "1,2,3", "member_type": "GENERAL"}},
                {"ref_type": "reference", "value": {"members": "current_processors,creator", "member_type": "EMPTY"}},
            ],
        }

        print(self.member_role_field.to_internal_data(inputs, self.context))

    def test_select_choice(self):
        field_schema = self.select_field.get_field_schema(key="field_schema")
        print(field_schema)
        self.assertTrue(isinstance(field_schema["choice"], list))
        self.assertTrue(len(field_schema["choice"]) > 0)

    def test_api_info_field_format(self):
        req_params_field = ApiInfoField(name="req_params")
        req_params = {
            "key": "member_field",
            "value": {
                "a": [
                    {
                        "b": {"value": "creator", "is_leaf": True, "ref_type": "reference"},
                        "c": {"value": "aaa", "is_leaf": True, "ref_type": "custom"},
                    },
                    {
                        "b": {"value": "aaa", "is_leaf": True, "ref_type": "custom"},
                        "c": {"value": "aaa", "is_leaf": True, "ref_type": "custom"},
                    },
                ],
                "d": {"value": "ddd", "is_leaf": True, "ref_type": "custom"},
            },
        }

        print(req_params_field.to_internal_data(req_params, self.context))
