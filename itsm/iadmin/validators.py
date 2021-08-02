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

import os
import time
from functools import reduce

from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.esb.esbclient import client_backend
from itsm.component.exceptions import (
    AnnexStoreValidateError,
    ComponentCallError,
    OrganizationStructureFunctionSwitchValidateError,
    ChildTicketSwitchValidateError,
    TaskSwitchValidateError,
    TriggerSwitchValidateError,
)
from itsm.component.constants import (
    MASTER_SLAVE,
    PROCESS_RUNNING,
    ACTIVE_TASK_STATUS,
    SOURCE_WORKFLOW,
    SOURCE_TICKET,
    SOURCE_TASK
)
from itsm.iadmin.contants import (
    SWITCH_OFF,
    SWITCH_ON,
)
from itsm.service.models import Service
from itsm.workflow.models import State
from itsm.task.models import Task
from itsm.ticket.models import TicketToTicket, Ticket
from itsm.trigger.models import Trigger


class PathTypeValidators(object):
    """路径类型校验"""

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        if self.instance:
            # 组织架构开关额外检查
            validate_func = getattr(self, "validate_{}".format(self.instance.key.lower()), 
                                    self.validate_other)
            validate_func(value)

    @staticmethod
    def validate_sys_file_path(value):
        path = value.get("value")
        if not path:
            raise AnnexStoreValidateError(_("路径不能为空！"))
        if not os.path.exists(path):
            raise AnnexStoreValidateError(_("路径不存在，请检查！"))
        file_path = os.path.join(path, "%s/" % int(time.time()))

        try:
            os.makedirs(file_path)
            try:
                if os.path.exists(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                logger.error("测试路径移除异常：%s" % e)
        except Exception as e:
            logger.error("PathTypeValidators：路径无法写入， %s" % e)
            raise AnnexStoreValidateError(_("路径无法写入，请联系管理员！"))

    @staticmethod
    def validate_is_organization(value):
        if value.get("value") == SWITCH_ON:
            try:
                client_backend.usermanage.list_departments({"fields": "id", "__raw": True})
            except ComponentCallError:
                raise OrganizationStructureFunctionSwitchValidateError(_("组织架构接口调用失败，无法启用，请联系管理员"))

        if value.get("value") == SWITCH_OFF:
            state_values = State.objects.filter(
                workflow__is_deleted=False, processors_type="ORGANIZATION"
            ).values_list("workflow__name", "name")
            if state_values.exists():
                raise OrganizationStructureFunctionSwitchValidateError(
                    _("以下流程节点正在使用组织架构功能，请更改再关闭：{}").format(",".join(["->".join(v) for v in state_values]))
                )
            service_values = Service.objects.filter(display_type="ORGANIZATION").values_list("name", flat=True)
            if service_values.exists():
                raise OrganizationStructureFunctionSwitchValidateError(
                    _("以下服务正在使用组织架构功能，请更改再关闭：{}").format(",".join(service_values))
                )

    @staticmethod
    def validate_child_ticket_switch(value):
        if value.get("value") == SWITCH_OFF:
            master_slaves = TicketToTicket.objects.filter(related_type=MASTER_SLAVE).values_list('from_ticket',
                                                                                                 'to_ticket')
            all_ticket_ids = reduce(lambda x, y: x.union(y), [set(), ] + list(master_slaves))
            active_ticket = Ticket.objects.filter(id__in=all_ticket_ids, current_status=PROCESS_RUNNING).exists()
            if active_ticket:
                raise ChildTicketSwitchValidateError(_("存在未完成的含有母子单的单据，请处理后再关闭"))

    @staticmethod
    def validate_task_switch(value):
        if value.get("value") == SWITCH_OFF:
            active_task = Task.objects.filter(status__in=ACTIVE_TASK_STATUS).exists()
            if active_task:
                raise TaskSwitchValidateError(_("存在含有未完成任务的单据，请处理后再关闭"))

    @staticmethod
    def validate_trigger_switch(value):
        if value.get("value") == SWITCH_OFF:
            quoted_status = [SOURCE_WORKFLOW, SOURCE_TICKET, SOURCE_TASK]
            active_trigger = Trigger.objects.filter(source_type__in=quoted_status).exists()
            if active_trigger:
                raise TriggerSwitchValidateError(_("存在被引用的触发器，请处理后再关闭"))

    @staticmethod
    def validate_other(value):
        pass
