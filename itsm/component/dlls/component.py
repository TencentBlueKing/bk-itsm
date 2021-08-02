# -*- coding:utf-8 -*-
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

import importlib
from collections import OrderedDict

from django import forms

from itsm.component.exceptions import ComponentNotExist, ComponentValidateError


class BaseComponentMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(BaseComponentMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, BaseComponentMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class
        module_name = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module_name})
        module = importlib.import_module(module_name)

        for obj_name, obj in attrs.items():
            setattr(new_class, obj_name, obj)

        if not getattr(module, '__register_ignore__', False):
            ComponentLibrary.register_component(
                component_type=new_class.type, component_code=new_class.code, component_cls=new_class
            )
        return new_class


class ComponentLibrary(object):
    """组件库"""

    components = OrderedDict()

    @classmethod
    def register_component(cls, component_type, component_code, component_cls):
        """注册组件"""
        cls.components.setdefault(component_type, {})[component_code] = component_cls

    @classmethod
    def get_component_class(cls, component_type, component_code):
        """获取组件类"""
        component_cls = cls.components.get(component_type, {}).get(component_code)
        if component_cls is None:
            raise ComponentNotExist('component %s does not exist.' % component_code)
        return component_cls


def get_error_prompt(form):
    """
    Get error messages for form
    """
    content = []
    for k, v in form.errors.items():
        b_field = form._safe_get_field(k)
        # Get the default error messages
        messages = {}
        if b_field:
            for c in reversed(b_field.field.__class__.__mro__):
                messages.update(getattr(c, "default_error_messages", {}))

        if b_field and v[0] in messages.values():
            content.append("%s [%s] %s" % (b_field.label, b_field.name, v[0]))
        else:
            content.append("%s" % v[0])
    return ";".join(content)


class BaseComponentForm(forms.Form):
    get_error_prompt = get_error_prompt

    def _safe_get_field(self, field):
        return self[field] if field in self.fields else None

    def get_cleaned_data_or_error(self):
        """
        获取当前form的cleaned data，如果验证不通过，直接抛出RpcAPIError
        """
        if self.is_valid():
            return self.cleaned_data
        else:
            raise ComponentValidateError(self.get_error_prompt())
