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

from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import EMPTY_STRING, LEN_SHORT, SHOW_BY_CONDITION
from itsm.component.utils.conversion import format_exp_value, show_conditions_validate
from itsm.component.utils.misc import get_choice_route, get_field_display_value, get_field_value, set_field_value
from itsm.workflow.models import BaseField

from . import managers


class TicketField(BaseField):
    """表单字段值表"""

    SOURCE = [('CUSTOM', '自定义添加'), ('TABLE', '基础模型添加')]

    ticket = models.ForeignKey('ticket.Ticket', help_text=_("关联工单"), related_name="fields", on_delete=models.CASCADE)
    state_id = models.CharField("对应的状态id", max_length=LEN_SHORT, default=EMPTY_STRING, null=True, blank=True)
    _value = models.TextField(_("表单值"), null=True, blank=True)
    source = models.CharField(_('添加方式'), max_length=LEN_SHORT, choices=SOURCE, default='CUSTOM')
    workflow_field_id = models.IntegerField(_('流程版本字段ID'), default=-1,)

    objects = managers.TicketFieldManager()

    class Meta:
        app_label = "ticket"
        verbose_name = _("表单字段值")
        verbose_name_plural = _("表单字段值")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type)

    @property
    def display_value(self):
        """根据_value是否有值对其进行转换"""
        return get_field_display_value(self)

    @property
    def value(self):
        """
        根据type转换_value并返回
        还有一个思路就是把所有类型都创建为表的一个字段（讨论）
        """
        return get_field_value(self)

    @value.setter
    def value(self, v):
        """
        保存时自动根据类型做转换
        """
        set_field_value(self, v)

    @property
    def _display_value(self):
        """用于获取日志接口的数据展示"""
        if not self._value:
            return ''

        if self.type in ['SELECT', 'RADIO']:
            return {str(choice['key']): choice['name'] for choice in self.choice}.get(self._value, self._value)

        if self.type in ['MULTISELECT', 'CHECKBOX', 'MEMBERS']:
            choice = {str(choice['key']): choice['name'] for choice in self.choice}
            return ','.join([choice.get(key, key) for key in self._value.split(',')])

        if self.type == 'TREESELECT':
            route = get_choice_route(self.choice, self._value)
            return '->'.join([item['name'] for item in route]) or self._value

        if self.type == 'TABLE':
            return {'header': self.choice, 'value': self.value}
        if self.type == 'CUSTOMTABLE':
            return {'header': self.meta, 'value': self.value}

        return self._value

    @property
    def can_edit(self):
        if self.is_readonly and self._value:
            return False
        return True

    def show_result(self, show_all_fields):

        if show_all_fields:
            return True

        if self.show_type == SHOW_BY_CONDITION:
            key_value = {
                'params_%s' % item['key']: format_exp_value(item['type'], item['_value'])
                for item in self.ticket.fields.values('key', '_value', 'type')
            }
            if show_conditions_validate(self.show_conditions, key_value):
                return False

        return True


class TaskField(BaseField):
    """任务表单字段"""

    SOURCE = [("CUSTOM", "自定义添加"), ("TABLE", "基础模型添加")]

    state_id = models.CharField("对应的状态id", max_length=LEN_SHORT, default=EMPTY_STRING, null=True, blank=True)
    _value = models.TextField(_("表单值"), null=True, blank=True)
    source = models.CharField(_("添加方式"), max_length=LEN_SHORT, choices=SOURCE, default="CUSTOM")
    workflow_field_id = models.IntegerField(_("流程版本字段ID"), default=-1,)
    task_id = models.IntegerField(_("任务ID"), default=-1)

    class Meta:
        app_label = "ticket"
        verbose_name = _("任务字段值")
        verbose_name_plural = _("任务字段值")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type)

    @property
    def display_value(self):
        """根据_value是否有值对其进行转换"""
        return get_field_display_value(self)

    @property
    def value(self):
        """
        根据type转换_value并返回
        """
        return get_field_value(self)

    @property
    def show_result(self):
        return True
