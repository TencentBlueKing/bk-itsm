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

from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import GENERAL_NOTICE
from itsm.component.esb.esbclient import client_backend
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.basic import merge_dict_list
from weixin.core.settings import WEIXIN_APP_EXTERNAL_HOST


class BaseNotifier(object):
    def __init__(self, title, receivers, message, notify_type=GENERAL_NOTICE):
        self.title = title
        self.receivers = receivers
        self.message = message
        self.notify_type = notify_type

    def get_notify_class(self, notify_type, **kwargs):
        """获取通知类"""

        if notify_type == "weixin":
            return WeixinNotifier(
                self.title,
                self.receivers,
                self.message,
                ticket_id=kwargs.get("ticket_id"),
            )

        if notify_type == "email":
            return EmailNotifier(self.title, self.receivers, self.message)

        if notify_type == "sms":
            return SmsNotifier(
                self.title,
                self.receivers,
                self.message,
                receiver_nums=kwargs.get("receiver_nums"),
            )

        return BaseNotifier(self.title, self.receivers, self.message, notify_type)

    def send(self, **kwargs):
        """
        发送通知
        """
        # 1.获取消息通知类型
        try:
            result = client_backend.cmsi.get_msg_type()
            notify_type_list = [ins["type"] for ins in result if ins["is_active"]]
        except ComponentCallError as e:
            logger.error("查询消息通知类型失败，error:{}".format(e))
            raise e
        # 2.判断当前通知类型是否可用""
        #   考虑到流程中配置某通知途径，后续可能下线的情况，因而做校验
        if self.notify_type.lower() not in notify_type_list:
            logger.info("不支持当前通知类型，notify_type:{}".format(self.notify_type))
            return
        # 3.构建通用消息发送接口参数
        params = merge_dict_list(
            [self.params, kwargs, {"msg_type": self.notify_type.lower()}]
        )
        # 4.通用消息发送
        try:
            return client_backend.cmsi.send_msg(params)
        except ComponentCallError as e:
            if e.esb_message.startswith("Some users failed"):
                return
            logger.error("通知发送失败，error:{}，params:{}".format(e, params))
            raise e

    @property
    def params(self):
        """
        获取参数
        """
        return {
            "receiver__username": self.receivers,
            "title": self.title,
            "content": self.message,
        }


class WeixinNotifier(BaseNotifier):
    """发送微信"""

    def __init__(
        self,
        title,
        receivers,
        message,
        wx_qy_agentid=settings.WX_QY_AGENTID,
        wx_qy_corpsecret=settings.WX_QY_CORPSECRET,
        ticket_id="",
    ):
        """支持指定通道发送企业微信消息"""

        self.wx_qy_agentid = wx_qy_agentid
        self.wx_qy_corpsecret = wx_qy_corpsecret
        self.ticket_id = ticket_id

        super(WeixinNotifier, self).__init__(title, receivers, message)

    def send(self, **kwargs):
        params = merge_dict_list(
            [self.params, kwargs, {"msg_type": settings.QY_WEIXIN}]
        )
        try:
            client_backend.cmsi.send_msg(params)
        except ComponentCallError as e:
            if e.esb_message.startswith("Some users failed"):
                return
            raise e

    @property
    def params(self):
        return {
            "receiver__username": self.receivers,
            "title": self.title,
            "content": self.message,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "remark": _(
                '<a href="{site_url}weixin/#/detail/{ticket_id}/">点击查看详情</a>'
            ).format(site_url=WEIXIN_APP_EXTERNAL_HOST, ticket_id=self.ticket_id),
            "wx_qy_agentid": self.wx_qy_agentid,
            "wx_qy_corpsecret": self.wx_qy_corpsecret,
        }


class EmailNotifier(BaseNotifier):
    """发送邮件"""

    def send(self, **kwargs):
        """
        发送通知
        """
        params = merge_dict_list([self.params, kwargs, {"msg_type": "mail"}])
        try:
            return client_backend.cmsi.send_msg(params)
        except ComponentCallError as e:
            if e.esb_message.startswith("Some users failed"):
                return
            raise e


class SmsNotifier(BaseNotifier):
    """发送短信"""

    def __init__(self, title, receivers, message, receiver_nums=""):
        """receiver_nums: 逗号隔开的多个手机号"""
        self.receiver_nums = receiver_nums
        super(SmsNotifier, self).__init__(title, receivers, message)

    def send(self, **kwargs):
        try:
            params = merge_dict_list([self.params, kwargs, kwargs, {"msg_type": "sms"}])
            return client_backend.cmsi.send_sms(params)
        except ComponentCallError as e:
            if e.esb_message.startswith("Some users failed"):
                return
            raise e

    @property
    def params(self):
        self.message = self.title + self.message
        if self.receiver_nums:
            return {"receiver": self.receiver_nums, "content": self.message}
        return {"receiver__username": self.receivers, "content": self.message}
