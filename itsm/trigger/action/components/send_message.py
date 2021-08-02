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

from django.utils.translation import ugettext as _

from itsm.component.notify import EmailNotifier, WeixinNotifier, SmsNotifier
from itsm.trigger.action.core.component import BaseComponent
from itsm.component.exceptions import ComponentCallError
from itsm.trigger.action.core import BaseForm, EmailMessageForms, MessageForms, WechatMessageForms, SubComponentField

from itsm.ticket.models import Ticket
from itsm.task.models import Task

__register_ignore__ = False


class SendEmailComponent(BaseComponent):
    name = _("邮件")
    code = "send_email_message"
    is_async = False
    form_class = EmailMessageForms
    is_sub_class = True
    need_refresh = False

    def _execute(self):
        inputs = self.data.inputs
        receivers = ",".join(inputs['receivers'])
        notifier = EmailNotifier(title=inputs['title'], receivers=receivers, message=inputs['content'])
        try:
            notifier.send()
        except ComponentCallError:
            raise
        return True


class SendSMSComponent(BaseComponent):
    name = _("短信")
    code = "send_sms_message"
    is_async = False
    form_class = MessageForms
    is_sub_class = True
    need_refresh = False

    def _execute(self):
        receivers = ",".join(self.data.inputs['receivers'])
        notifier = SmsNotifier(title="sms-title needless", receivers=receivers, message=self.data.inputs['content'])
        try:
            notifier.send()
        except ComponentCallError:
            raise
        return True


class SendWechatComponent(BaseComponent):
    name = _("微信")
    code = "send_wechat_message"
    is_async = False
    form_class = WechatMessageForms
    is_sub_class = True
    need_refresh = False

    def _execute(self):
        receivers = ",".join(self.data.inputs['receivers'])
        notifier = WeixinNotifier(
            title=self.data.inputs['title'], receivers=receivers, message=self.data.inputs['content']
        )
        try:
            notifier.send()
        except ComponentCallError:
            raise
        return True


class MultiMessageForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    sub_message_component = SubComponentField(
        sub_components=[SendEmailComponent, SendSMSComponent, SendWechatComponent], name="对应的所有消息配置信息"
    )

    def get_cleaned_data_or_error(self):
        # TODO 包含子组件的有特殊逻辑
        return self.inputs


class SendMessage(BaseComponent):
    """
    发送通知组合条件
    :param : 
    :return: 
    """

    name = _("发送通知给用户")
    code = "send_message"
    is_async = False
    need_refresh = False
    form_class = MultiMessageForms
    sub_action_classes = [SendEmailComponent, SendWechatComponent, SendSMSComponent]

    def __init__(self, context, params_schema, action_id=None, countdown=0):
        #  根据输入参数进行解析子动作的初始化， 根据参数类型

        """
        :param context: 
        :param params_schema: 
        :param action_id: 
        """
        super(SendMessage, self).__init__(context, params_schema, action_id, countdown)

        # 初始化子组件
        self.sub_actions = []
        for item in self.params_schema:
            sub_components = item.get("sub_components", [])
            for sub_component in sub_components:
                sub_action = self.get_sub_action(sub_component)
                if sub_action:
                    self.sub_actions.append(sub_action)

    def get_sub_action(self, sub_component):
        """
        获取对应的子类对象
        :param sub_component: 
        :return: 
        """

        for action_class in self.sub_action_classes:
            if sub_component['key'] == action_class.code:
                return action_class(self.context, sub_component['params'])

    def _execute(self):
        for sub_action in self.sub_actions:
            sub_action.execute()
        return True

    def to_representation_data(self, flat=False):
        """
        获取字段的展示值
        :return: 
        """
        return self.form.to_representation_data(sub_actions=self.sub_actions, flat=flat)

    def update_context(self):
        """
        手动操作的时候更新context
        """
        try:
            ticket = Ticket.objects.get(sn=self.context.get("ticket_sn"))
            self.context.update(ticket.get_output_fields(return_format='dict'))
        except Ticket.DoesNotExist:
            pass

        try:
            task = Task.objects.get(id=self.context.get("task_id"))
            self.context.update(task.get_output_context())

        except Task.DoesNotExist:
            pass

        for sub_action in self.sub_actions:
            sub_action.context.update(self.context)
            sub_action.validate_inputs()
        return self.context
