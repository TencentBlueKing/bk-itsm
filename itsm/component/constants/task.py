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
from common.enum import enum

NEW = "NEW"
QUEUE = "QUEUE"
WAITING_FOR_OPERATE = "WAITING_FOR_OPERATE"
WAITING_FOR_CONFIRM = "WAITING_FOR_CONFIRM"
WAITING_FOR_BACKEND = "WAITING_FOR_BACKEND"
SKIPPED = "SKIPPED"
FAILED = "FAILED"
FINISHED = "FINISHED"
RUNNING = "RUNNING"
REVOKED = 'REVOKED'
SUSPENDED = 'SUSPENDED'
DELETED = "DELETED"
SUCCEED = "SUCCEED"
CANCELED = "CANCELED"
TERMINATE = "TERMINATE"

ACTIVE_TASK_STATUS = [QUEUE, WAITING_FOR_OPERATE, WAITING_FOR_CONFIRM, WAITING_FOR_BACKEND, RUNNING]
NEED_UPDATE_TASK_STATUS = [REVOKED, FAILED, SUSPENDED, DELETED, RUNNING]
END_TASK_STATUS = [REVOKED, FINISHED, DELETED]
NEED_SYNC_STATUS = [NEW, QUEUE, FAILED, SUSPENDED, RUNNING, WAITING_FOR_OPERATE]

NOT_CREATED = 'NOT_CREATED'
CREATE_FAILED = 'CREATE_FAILED'
CREATED = 'CREATED'
START_FAILED = 'START_FAILED'

SOPS_TASK_STATE_CHOICE = [
    (NOT_CREATED, '未创建'),
    (CREATE_FAILED, '创建失败'),
    (CREATED, '创建成功'),
    (START_FAILED, '启动失败'),
    (RUNNING, '执行中'),
    (FAILED, '执行失败'),
    (FINISHED, '执行结束'),
    (REVOKED, '被撤销'),
    (SUSPENDED, '被挂起'),
    (DELETED, '被删除'),
]

SOPS_TASK_STARTED_STATUS = [START_FAILED, RUNNING, REVOKED, FINISHED, FAILED, SUSPENDED]

CREATE = "CREATE"
OPERATE = "OPERATE"
CONFIRM = "CONFIRM"
ACTION_CONFIRM = "confirm"
ACTION_OPERATE = "operate"
ACTION_SKIP = "skip"

FLOW = "FLOW"
VERSION = "VERSION"

TASK_TYPE = [
    (FLOW, _("流程")),
    (VERSION, _("流程版本")),
]

TASK_STAGE_CHOICE = [
    (CREATE, _("新建")),
    (OPERATE, _("处理")),
    (CONFIRM, _("确认")),
]

TASK_STAGE_LIST = ["CREATE", "OPERATE", "CONFIRM"]

SOPS_TASK = "SOPS"
NORMAL_TASK = "NORMAL"
DEVOPS_TASK = "DEVOPS"
TASK_COMPONENT_CHOICE = [(NORMAL_TASK, _("常规")), (SOPS_TASK, _("标准运维")), (DEVOPS_TASK, _("蓝盾"))]
TASK_NAME_KEY = "task_name"  # 字段`任务名称`的key
TASK_PROCESSOR_KEY = "processors"  # 字段`处理人`的key
SOPS_TEMPLATE_KEY = "sops_templates"  # 字段`流程模板`的key
TASK_PI_PREFIX = "task"  # 任务pipeline_id的前缀
SUB_TASK_PARAMS_KEY = "sub_task_params"  # 字段`流程模板`的key

# 内置任务模块字段
TASK_FIELDS_SCHEMA = [
    {
        "stage": CREATE,
        "key": TASK_NAME_KEY,
        "name": "任务名称",
        "sequence": 0,
        "is_builtin": True,
        "display": True,
        "type": "STRING",
        "layout": "COL_12",
        "regex": "EMPTY",
    },
    {
        "stage": CREATE,
        "key": TASK_PROCESSOR_KEY,
        "name": "处理人",
        "sequence": 1,
        "is_builtin": True,
        "display": True,
        "type": "COMPLEX-MEMBERS",
        "layout": "COL_12",
        "regex": "EMPTY",
    },
]

# 内置任务模块字段
SOPS_TASK_FIELDS_SCHEMA = TASK_FIELDS_SCHEMA + [
    {
        "stage": CREATE,
        "key": SOPS_TEMPLATE_KEY,
        "name": "标准运维参数",
        "sequence": 2,
        "is_builtin": True,
        "display": True,
        "type": "SOPS_TEMPLATE",
        "layout": "COL_12",
        "regex": "EMPTY",
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'executeTime',
        'name': '执行时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'NON_NEGATIVE',
        'desc': '运维执行时长 (浮点数,单位是分钟)',
        'tips': '运维执行时长 (浮点数,单位是分钟)',
        'is_tips': True,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 1,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'reviewNumerator',
        'name': '停机比例',
        'layout': 'COL_12',
        'validate_type': 'OPTION',
        'regex': 'NON_NEGATIVE',
        'desc': '停机比例(整型 0-100)',
        'tips': '停机比例(整型 0-100)',
        'is_tips': True,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 2,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'RADIO',
        'key': 'reviewIsShutdown',
        'name': '是否停机发布',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'EMPTY',
        'desc': '是否停机发布 (整型：0, 1)',
        'tips': '是否停机发布 (整型：0, 1)',
        'is_tips': True,
        'default': '0',
        'choice': [{'key': '1', 'name': '是'}, {'key': '0', 'name': '否'}],
        'stage': CONFIRM,
        'sequence': 3,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'reviewShutdownTime',
        'name': '停机耗费时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'OPTION',
        'regex': 'NON_NEGATIVE',
        'desc': '停机耗费时长 (浮点数)',
        'tips': '停机耗费时长 (浮点数)',
        'is_tips': True,
        'default': '0',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 4,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'prepareTime',
        'name': '任务准备时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'NON_NEGATIVE',
        'desc': '任务准备时长 (浮点数,单位是分钟)',
        'tips': '任务准备时长 (浮点数,单位是分钟)',
        'is_tips': True,
        'default': '0',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 5,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'testTime',
        'name': '现网测试时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'NON_NEGATIVE',
        'desc': '现网测试时长 (浮点数,单位是分钟)',
        'tips': '现网测试时长 (浮点数,单位是分钟)',
        'is_tips': True,
        'default': '0',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 6,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'SELECT',
        'key': 'isSuccess',
        'name': '发布实施结论',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'EMPTY',
        'desc': '发布实施结论',
        'tips': '发布实施结论',
        'is_tips': True,
        'default': '1',
        'choice': [{'key': '1', 'name': '完全成功'}, {'key': '2', 'name': '成功但有问题'}, {'key': '3', 'name': '发布失败'}],
        'stage': CONFIRM,
        'sequence': 7,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'DATETIME',
        'key': 'actualEndTime',
        'name': '实际结束时间',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'EMPTY',
        'desc': "实际结束时间，日期格式 'yyyy-MM-dd hh:mm:ss'",
        'tips': "实际结束时间，日期格式 'yyyy-MM-dd hh:mm:ss'",
        'is_tips': True,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 8,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'DATETIME',
        'key': 'actualBeginTime',
        'name': '实际开始时间',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'EMPTY',
        'desc': "实际开始时间，日期格式 'yyyy-MM-dd hh:mm:ss'",
        'tips': "实际开始时间，日期格式 'yyyy-MM-dd hh:mm:ss'",
        'is_tips': True,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 9,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'RADIO',
        'key': 'reviewIsDbChange',
        'name': '是否DB发布',
        'layout': 'COL_12',
        'validate_type': 'REQUIRE',
        'regex': 'EMPTY',
        'desc': '是否DB发布',
        'tips': '是否DB发布',
        'is_tips': True,
        'default': '0',
        'choice': [{'key': '1', 'name': '是'}, {'key': '0', 'name': '否'}],
        'stage': CONFIRM,
        'sequence': 10,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'reviewDbChangeTime',
        'name': 'DB耗费时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'OPTION',
        'regex': 'NON_NEGATIVE',
        'desc': 'DB耗费时长 (浮点数)',
        'tips': 'DB耗费时长 (浮点数)',
        'is_tips': True,
        'default': '0',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 11,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'TEXT',
        'key': 'conclusion',
        'name': '发布经验总结',
        'layout': 'COL_12',
        'validate_type': 'OPTION',
        'regex': 'EMPTY',
        'desc': '发布经验总结',
        'tips': '',
        'is_tips': False,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 12,
    },
    {
        'is_builtin': True,
        'display': True,
        'type': 'STRING',
        'key': 'dbBackupTime',
        'name': 'DB备份时长（分钟）',
        'layout': 'COL_12',
        'validate_type': 'OPTION',
        'regex': 'NON_NEGATIVE',
        'desc': '',
        'tips': '',
        'is_tips': False,
        'default': '',
        'choice': [],
        'stage': CONFIRM,
        'sequence': 13,
    },
]

DEVOPS_TASK_FIELDS_SCHEMA = TASK_FIELDS_SCHEMA + [
    {
        "stage": CREATE,
        "key": SUB_TASK_PARAMS_KEY,
        "name": "子任务流水线参数",
        "sequence": 2,
        "is_builtin": True,
        "display": True,
        "type": "DEVOPS_TEMPLATE",
        "layout": "COL_12",
        "regex": "EMPTY",
    },
]

DEVOPS_STATUS = enum(
    SUCCEED="SUCCEED",
    FAILED="FAILED",
    CANCELED="CANCELED",
    RUNNING="RUNNING",
    TERMINATE="TERMINATE",
    REVIEWING="REVIEWING",
    REVIEW_ABORT="REVIEW_ABORT",
    REVIEW_PROCESSED="REVIEW_PROCESSED",
    HEARTBEAT_TIMEOUT="HEARTBEAT_TIMEOUT",
    PREPARE_ENV="PREPARE_ENV",
    SKIP="SKIP",
    QUALITY_CHECK_FAIL="QUALITY_CHECK_FAIL",
    QUEUE="QUEUE",
    LOOP_WAITING="LOOP_WAITING",
    CALL_WAITING="CALL_WAITING",
    QUEUE_TIMEOUT="QUEUE_TIMEOUT",
    EXEC_TIMEOUT="EXEC_TIMEOUT",
    QUEUE_CACHE="QUEUE_CACHE",
)

DEVOPS_RUNNING_STATUS = [
    DEVOPS_STATUS.RUNNING,
    DEVOPS_STATUS.REVIEWING,
    DEVOPS_STATUS.PREPARE_ENV,
    DEVOPS_STATUS.SKIP,
    DEVOPS_STATUS.QUEUE,
    DEVOPS_STATUS.LOOP_WAITING,
    DEVOPS_STATUS.CALL_WAITING,
    DEVOPS_STATUS.QUEUE_CACHE,
    DEVOPS_STATUS.REVIEW_PROCESSED,
]

DEVOPS_FAILED_STATUS = [
    DEVOPS_STATUS.FAILED,
    DEVOPS_STATUS.QUALITY_CHECK_FAIL,
    DEVOPS_STATUS.REVIEW_ABORT,
    DEVOPS_STATUS.QUEUE_TIMEOUT,
    DEVOPS_STATUS.EXEC_TIMEOUT,
    DEVOPS_STATUS.HEARTBEAT_TIMEOUT,
]

DEVOPS_TASK_STATE_CHOICE = [
    (NOT_CREATED, '未创建'),
    (DEVOPS_STATUS.SUCCEED, '执行成功'),
    (DEVOPS_STATUS.FAILED, '执行失败'),
    (DEVOPS_STATUS.CANCELED, '已取消'),
    (DEVOPS_STATUS.TERMINATE, '已终止'),
    (DEVOPS_STATUS.RUNNING, '执行中'),
]

TASK_STATUS_CHOICE = [
    (NEW, _("新建")),
    # 进入到执行节点，不能再删除和修改
    (QUEUE, _("待处理")),
    # 下发到后台队列中，等待执行
    (WAITING_FOR_OPERATE, _("待处理")),
    (WAITING_FOR_BACKEND, '后台处理中'),
    (RUNNING, _("执行中")),
    (WAITING_FOR_CONFIRM, _("待总结")),
    # 任务无法正常结束，可设置为忽略状态
    (SKIPPED, _("已忽略")),
    # 自动任务执行失败
    (FAILED, _("失败")),
    (FINISHED, _("完成")),
    (REVOKED, _('被撤销')),
    (SUSPENDED, _('被挂起')),
    (DELETED, _('被删除')),
    (SUCCEED, _('执行成功')),
    (TERMINATE, _('已终止')),
    (CANCELED, _('已取消')),
]
