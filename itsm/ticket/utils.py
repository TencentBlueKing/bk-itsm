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
from mako.template import Template

from common.log import logger
from itsm.component.constants import GENERAL_NOTICE
from itsm.component.utils.misc import transform_single_username
from itsm.iadmin.contants import ACTION_CHOICES_DICT
from itsm.iadmin.models import CustomNotice
from itsm.task.models import Task as TicketTask


def translate(message, cxt, related_operators=None):
    try:
        return _(message).format(
            operator=transform_single_username(cxt["operator"], related_operators),
            name=cxt["from_state_name"],
            detail_message=cxt["detail_message"],
            action=_(cxt["action"]).lower(),
        )

    except BaseException:
        return _(message)


def translate_constant_2(constant):
    temp_constant = []
    for item in constant:
        # py2->py3: 'str' object has no attribute 'decode'
        temp_constant.append((item[0], _(item[1])))
    constant = temp_constant
    return constant


def translate_constant_export_fields_dict(value):
    for index, item in enumerate(value):
        value[index]["name"] = _(item["name"])
    return value


def compute_list_difference(current, new):
    """
    计算A列表相较于B列表多出来的部分
    """
    return list(set(new).difference(set(current)))


def get_custom_notify(ticket, action, notify_type, used_by=None):
    if not notify_type:
        notify_type = GENERAL_NOTICE
    query_params = {
        "action": action,
        "notify_type": notify_type,
    }
    if used_by:
        query_params["used_by"] = used_by
    try:
        custom_notify = CustomNotice.objects.get(
            project_key=ticket.project_key, **query_params
        )
    except CustomNotice.DoesNotExist:
        custom_notify = CustomNotice.objects.get(**query_params, project_key="public")

    return custom_notify


def build_message(_notify, task_id, ticket, message, action, **kwargs):
    if task_id:
        custom_notify = get_custom_notify(ticket, action, _notify.type, used_by="TASK")
    else:
        custom_notify = get_custom_notify(ticket, action, _notify.type)

    # 获取单据上下文
    context = ticket.get_notify_context()
    context.update(
        message=message, action=_(ACTION_CHOICES_DICT.get(action, "待处理")), **kwargs
    )

    # 获取任务上下文
    if task_id:
        try:
            task = TicketTask.objects.get(id=task_id)
            context.update(
                {item["key"]: item["value"] for item in task.get_output_context()}
            )
        except TicketTask.DoesNotExist:
            logger.error("Failed to get task context: task_id={}".format(task_id))
            return None

    try:
        content = Template(custom_notify.content_template).render(**context)
        title = Template(custom_notify.title_template).render(**context)
        return content, title
    except NameError as error:
        logger.error(
            "context render failed, error: {}, title: {}->{}, content: {}->{}".format(
                error,
                context,
                custom_notify.title_template,
                context,
                custom_notify.content_template,
            )
        )
        return None
