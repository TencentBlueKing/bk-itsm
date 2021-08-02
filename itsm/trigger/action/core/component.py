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

import traceback
from django.utils.translation import ugettext as _
from django.forms.fields import CallableChoiceIterator
from django.forms.forms import DeclarativeFieldsMetaclass

from itsm.component.dlls.component import BaseComponentMeta
from itsm.trigger.tasks import async_execute_action
from itsm.trigger.signal import action_finish
from pipeline.core.data.base import DataObject


class BaseComponent(metaclass=BaseComponentMeta):  # noqa
    """
    Base class for component
    """

    name = 'UNKNOWN'  # display name
    code = 'unknown'  # 在trigger组件里唯一
    type = 'trigger'
    Form = None
    is_async = True
    need_refresh = True
    exclude_signal_type = []

    def __init__(self, context, params_schema, action_id=None, countdown=0):
        self.data = DataObject({})  # include input and output
        self.context = context  # context data
        self.params_schema = params_schema
        self.action_id = action_id
        self.countdown = countdown
        self.form = self.form_class(self.params_schema, self.context) if self.form_class else None
        self.validate_inputs()

    def invoke(self, inputs):
        """Invoke component"""
        self.validate_inputs()
        result = self.execute()
        return result

    def validate_inputs(self):
        """
        校验输入信息
        :return:
        """
        self.form.inputs.update(self.context)
        inputs = self.form.get_cleaned_data_or_error() if self.form else {}
        self.data.override_inputs(inputs)

    def to_representation_data(self, **kwargs):
        return self.form.to_representation_data(**kwargs)

    def validate_params(self):
        self.form.validate_params()

    def run(self):
        if self.countdown:
            return async_execute_action.apply_async(self, countdown=self.countdown * 60)
        if self.is_async:
            return async_execute_action.delay(self)
        return self.execute()

    def execute(self):
        error_message = ""
        try:
            result = self._execute()
        except BaseException:
            error_message = traceback.format_exc()
            print(error_message)
            result = False

        # 通过信息发送事件结束信息
        action_finish.send(
            self.__class__,
            action_id=self.action_id,
            result=result,
            error_message=error_message or self.data.get_one_of_outputs("message"),
            outputs=self.data.outputs,
        )
        return result

    def _execute(self):
        """
        All Component should override this class
        """
        raise NotImplementedError("All Component should override this class")

    @classmethod
    def get_inputs(cls):
        inputs = []
        # Whether define form data
        if isinstance(cls.Form, DeclarativeFieldsMetaclass):
            for field_name, field in cls.Form.declared_fields.items():
                choices = getattr(field, "choices") if hasattr(field, "choices") else None
                if isinstance(choices, CallableChoiceIterator):
                    choices = choices.choices_func()

                input_data = {
                    'name': _(field_name),
                    'label': _(field.label),
                    'initial': field.initial,
                    'required': field.required,
                    'choices': choices,
                }
                inputs.append(input_data)

        if hasattr(cls, "form_class"):
            inputs = cls.form_class.declared_fields_schema()
        return inputs

    def update_context(self):
        self.validate_inputs()
        return self.context
