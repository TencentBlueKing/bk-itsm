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

ACTION_STATUS_CREATED = "CREATED"
ACTION_STATUS_RUNNING = "RUNNING"
ACTION_STATUS_SUCCEED = "SUCCEED"
ACTION_STATUS_FAILED = "FAILED"

ACTION_STATUS_CHOICE = [
    (ACTION_STATUS_CREATED, _("新建")),
    (ACTION_STATUS_RUNNING, _("执行中")),
    (ACTION_STATUS_SUCCEED, _("成功")),
    (ACTION_STATUS_FAILED, _("失败")),
]

MANUAL = "MANUAL"
BACKEND = "BACKEND"
OPT_TYPE_CHOICE = [(MANUAL, _("手动执行")), (BACKEND, _("后台执行"))]

SOURCE_BASIC = "basic"
SOURCE_WORKFLOW = "workflow"
SOURCE_TICKET = "ticket"
SOURCE_TASK = "task"

TRIGGER_SOURCE_TYPE = [
    (SOURCE_BASIC, _("公共")),
    (SOURCE_WORKFLOW, _("流程")),
    (SOURCE_TICKET, _("流程版本")),
    (SOURCE_TASK, _("任务")),
]

TRIGGER_ICON_CHOICE = [
    ("message", _("消息")),
    ("status", _("修改状态")),
    ("user", _("修改处理人")),
    ("api", _("API接口")),
]

# 触发信息定义

# Part1 单据相关
CREATE_TICKET = "CREATE_TICKET"
CLOSE_TICKET = "CLOSE_TICKET"
TERMINATE_TICKET = "TERMINATE_TICKET"
SUSPEND_TICKET = "SUSPEND_TICKET"
RECOVERY_TICKET = "RECOVERY_TICKET"
DELETE_TICKET = "DELETE_TICKET"
CREATE_RELATE_TICKET = "CREATE_RELATE_TICKET"
CREATE_PARENTChILD_TICKET = "CREATE_PARENTChILD_TICKET"
DISSOLVE_PARENTChILD_TICKET = "DISSOLVE_PARENTChILD_TICKET"

# Part2 节点和线条
ENTER_STATE = "ENTER_STATE"
LEAVE_STATE = "LEAVE_STATE"
GLOBAL_ENTER_STATE = "GLOBAL_ENTER_STATE"
GLOBAL_LEAVE_STATE = "GLOBAL_LEAVE_STATE"
DISTRIBUTE_STATE = "DISTRIBUTE_STATE"
CLAIM_STATE = "CLAIM_STATE"
DELIVER_STATE = "DELIVER_STATE"

FLOW_TRIGGER_SIGNAL = {
    CREATE_TICKET: _("创建单据"),
    CLOSE_TICKET: _("关闭单据"),
    TERMINATE_TICKET: _("终止单据"),
    SUSPEND_TICKET: _("挂起单据"),
    RECOVERY_TICKET: _("恢复单据"),
    DELETE_TICKET: _("撤销单据"),
    GLOBAL_ENTER_STATE: _("进入节点"),
    GLOBAL_LEAVE_STATE: _("离开节点")
    # CREATE_RELATE_TICKET: _("创建关联单"),
    # CREATE_PARENTChILD_TICKET: _("创建母子单"),
    # DISSOLVE_PARENTChILD_TICKET: _("解除母子单"),
}

STATE_TRIGGER_SIGNAL = {
    ENTER_STATE: _("进入节点"),
    LEAVE_STATE: _("离开节点"),
    DISTRIBUTE_STATE: _("分派单据"),
    CLAIM_STATE: _("认领单据"),
    DELIVER_STATE: _("转单"),
}

THROUGH_TRANSITION = "THROUGH_TRANSITION"
TRANSITION_TRIGGER_SIGNAL = {
    THROUGH_TRANSITION: _("进入分支"),
}

# Part 3 任务组的
CREATE_TASK = "CREATE_TASK"
DELETE_TASK = "DELETE_TASK"
BEFORE_START_TASK = "BEFORE_START_TASK"
AFTER_FINISH_TASK = "AFTER_FINISH_TASK"
AFTER_CONFIRM_TASK = "AFTER_CONFIRM_TASK"

TASK_TRIGGER_SIGNAL = {
    CREATE_TASK: _("创建任务之后"),
    DELETE_TASK: _("删除任务"),
    BEFORE_START_TASK: _("执行任务之前"),
    AFTER_FINISH_TASK: _("执行任务之后"),
    AFTER_CONFIRM_TASK: _("完成任务之后"),
}

# 所有的触发信息

FLOW_SIGNAL = "FLOW"
STATE_SIGNAL = "STATE"
TRANSITION_SIGNAL = "TRANSITION"
TASK_SIGNAL = "TASK"

TRIGGER_SIGNAL = {
    "FLOW": FLOW_TRIGGER_SIGNAL,
    "STATE": STATE_TRIGGER_SIGNAL,
    "TRANSITION": TRANSITION_TRIGGER_SIGNAL,
    "TASK": TASK_TRIGGER_SIGNAL,
}

TRIGGER_CATEGORIES = {
    "FLOW": _("单据信号"),
    "STATE": _("节点信号"),
    "TRANSITION": _("线条信号"),
    "TASK": _("任务信号"),
}

ONLY_BACKEND_SIGNALS = [
    AFTER_CONFIRM_TASK,
    LEAVE_STATE,
    THROUGH_TRANSITION,
    DELETE_TICKET,
    CLOSE_TICKET,
    TERMINATE_TICKET,
]

TRIGGER_SIGNAL_CHOICE = [
    (signal, name)
    for signal_group in TRIGGER_SIGNAL.values()
    for signal, name in signal_group.items()
]
