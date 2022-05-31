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

from itsm.component.utils import robot
from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import StringField
from itsm.trigger.action.core import BaseForm

__register_ignore__ = False


class RobotForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    web_hook_id = StringField(name="Webhook ID", required=True)
    chat_id = StringField(name="Chat ID", required=False, tips="群ID, 多个用,区分")
    content = StringField(name=_("文本内容"), field_type="TEXT", required=True)
    mentioned_list = StringField(
        name="需要提及的人的列表", tips="英文半角逗号分割的英文名列表，不填则默认@所有成员，None不@任何人", required=False
    )


class AutomaticAnnouncementComponent(BaseComponent):
    name = _("企业微信机器人通知")
    code = "automatic_announcement"
    is_async = False
    form_class = RobotForms

    def _execute(self):
        """
        机器人自动通知
        """
        web_hook_ids = self.data.get_one_of_inputs("web_hook_id")
        content = self.data.get_one_of_inputs("content")
        mentioned_list = self.data.get_one_of_inputs("mentioned_list")
        chat_id = self.data.get_one_of_inputs("chat_id", "")

        chat_ids = None
        if len(chat_id) != 0:
            if len(web_hook_ids.split(",")) > 1:
                self.data.set_outputs("message", "当指定群时,Webhook ID只能选一个")
                return False
            chat_ids = "|".join(chat_id.split(","))

        if mentioned_list is None or len(mentioned_list) == 0:
            mentioned_list = ["@all"]
        elif mentioned_list == "None":
            mentioned_list = []
        else:
            mentioned_list = mentioned_list.split(",")
        if not web_hook_ids:
            self.data.set_outputs("message", "企业微信机器人未添加")
            return False

        if not content:
            self.data.set_outputs("message", "自动通知内容未添加")
            return False

        threads = []
        for web_hook_id in web_hook_ids.split(","):
            announcement = robot.Announcement(
                web_hook_id, content, mentioned_list, chat_ids
            )
            threads.append(announcement)

        for thread in threads:
            thread.start()

        output = []
        for thread in threads:
            thread.join()
            if not thread.is_success():
                output.append(
                    "发送消息到{}机器人失败，原因是{}".format(
                        thread.web_hook_id, thread.get_error_msg()
                    )
                )

        if output:
            self.data.set_outputs("message", ";".join(output))
            return False

        return True
