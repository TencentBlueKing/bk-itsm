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

from common.enum import enum

# 流程节点类型
START_STATE = "START"
NORMAL_STATE = "NORMAL"
SIGN_STATE = "SIGN"
APPROVAL_STATE = "APPROVAL"
TASK_STATE = "TASK"
TASK_SOPS_STATE = "TASK-SOPS"
TASK_DEVOPS_STATE = "TASK-DEVOPS"
ROUTER_STATE = "ROUTER"
ROUTER_P_STATE = "ROUTER-P"
COVERAGE_STATE = "COVERAGE"
END_STATE = "END"
VIRTUAL_STATE = "MIGRATE"
WEBHOOK_STATE = "WEBHOOK"
BK_PLUGIN_STATE = "BK-PLUGIN"

GATEWAY_STATES = [ROUTER_P_STATE, COVERAGE_STATE]
NORMAL_STATES = [
    START_STATE,
    NORMAL_STATE,
    TASK_STATE,
    TASK_SOPS_STATE,
    TASK_DEVOPS_STATE,
    WEBHOOK_STATE,
    BK_PLUGIN_STATE,
    SIGN_STATE,
    END_STATE,
    APPROVAL_STATE,
]

STATE_TYPE_CHOICES = [
    (START_STATE, "开始节点(圆形)"),
    (NORMAL_STATE, "普通节点"),
    (SIGN_STATE, "会签节点"),
    (APPROVAL_STATE, "审批节点"),
    (TASK_STATE, "自动节点"),
    (TASK_SOPS_STATE, "标准运维节点"),
    (TASK_DEVOPS_STATE, "蓝盾任务节点"),
    (WEBHOOK_STATE, "WebHook节点"),
    (BK_PLUGIN_STATE, "蓝鲸插件节点"),
    (ROUTER_STATE, "分支网关节点(菱形)"),
    (ROUTER_P_STATE, "并行网关节点"),
    (COVERAGE_STATE, "汇聚网关节点"),
    (END_STATE, "结束节点(圆形)"),
]

# 流程状态定义
PROCESS_RUNNING = "RUNNING"
PROCESS_SUSPENDED = "SUSPEND"
PROCESS_FINISHED = "FINISHED"
PROCESS_FAILED = "FAILED"
PROCESS_REVOKED = "TERMINATED"
FLOW_STATUS_CHOICES = [
    (PROCESS_SUSPENDED, "挂起中"),
    (PROCESS_RUNNING, "执行中"),
    (PROCESS_FINISHED, "成功结束"),
    (PROCESS_FAILED, "失败结束"),
    (PROCESS_REVOKED, "撤销结束"),
]

# 节点状态 in 流程状态
RUNNING = PROCESS_RUNNING
TERMINATED = PROCESS_REVOKED
FINISHED = PROCESS_FINISHED
FAILED = PROCESS_FAILED
SUSPEND = PROCESS_SUSPENDED

# 节点状态 not in 流程状态
WAIT = "WAIT"
RECEIVING = "RECEIVING"
DISTRIBUTING = "DISTRIBUTING"
QUEUEING = "QUEUEING"  # 节点处理中状态

STATUS_CHOICES = [
    (WAIT, "待处理"),
    (RUNNING, "处理中"),
    (QUEUEING, "后台处理中"),
    (RECEIVING, "待认领"),
    (DISTRIBUTING, "待分派"),
    (TERMINATED, "被终止"),
    (FINISHED, "已结束"),
    (FAILED, "执行失败"),
    (SUSPEND, "被挂起"),
]
STATUS_DICT = dict(STATUS_CHOICES)

# 流程节点操作标识
TERMINATE_OPERATE = "TERMINATE"
TRANSITION_OPERATE = "TRANSITION"
SIGN_OPERATE = "SIGN"
SUSPEND_OPERATE = "SUSPEND"
UNSUSPEND_OPERATE = "UNSUSPEND"
DELIVER_OPERATE = "DELIVER"
WITHDRAW_OPERATE = "WITHDRAW"
CLAIM_OPERATE = "CLAIM"
DISTRIBUTE_OPERATE = "DISTRIBUTE"
EXCEPTION_DISTRIBUTE_OPERATE = "EXCEPTION_DISTRIBUTE"
FOLLOW_OPERATE = "FOLLOW"
NOTIFY_FOLLOWER_OPERATE = "NOTIFY_FOLLOWER"
REJECT_OPERATE = "REPULSE"
SYSTEM_OPERATE = "AUTOMATIC"
INVITE_OPERATE = "INVITE"
SUPERVISE_OPERATE = "SUPERVISE"
CUSTOM_ACTION_OPERATE = "CUSTOM_ACTION"
TRIGGER_ACTION_OPERATE = "TRIGGER_ACTION_OPERATE"
RETRY = "RETRY"
IGNORE = "IGNORE"
MANUAL = "MANUAL"

# 流程节点失败标识
NODE_FAILED = "NODE_FAILED"

# 单据审批意见标识别
TONGYI = "true"
JUJUE = "false"

API_FAILED_CHOICES = [
    (RETRY, "重试"),
    (IGNORE, "忽略"),
    (MANUAL, "手动修改"),
]

API_DICT = dict(API_FAILED_CHOICES)

# 单据处理操作类型
OPERATE_CHOICES = [
    (TRANSITION_OPERATE, "提交"),
    (CLAIM_OPERATE, "认领工单"),
    (DISTRIBUTE_OPERATE, "分派工单"),
    (TERMINATE_OPERATE, "终止"),
    (SUSPEND_OPERATE, "挂起"),
    (UNSUSPEND_OPERATE, "恢复"),
    (DELIVER_OPERATE, "转单"),
    (WITHDRAW_OPERATE, "撤单"),
    (FOLLOW_OPERATE, "关注"),
    (FINISHED, "已完成"),
    (REJECT_OPERATE, "打回"),
    (SYSTEM_OPERATE, "自动执行"),
    (SIGN_OPERATE, "会签操作"),
    (TRIGGER_ACTION_OPERATE, "触发器操作"),
]
OPERATE_TYPE = dict(OPERATE_CHOICES)
OPERATE_TYPE.update(API_DICT)

ACTION_CHOICES = [
    (TRANSITION_OPERATE, "提交"),
    (DISTRIBUTE_OPERATE, "分派"),
    (CLAIM_OPERATE, "认领"),
    (SIGN_OPERATE, "会签"),
    (SYSTEM_OPERATE, "自动执行"),
]

ALL_ACTION_CHOICES = [
    (TRANSITION_OPERATE, "提交"),
    (DISTRIBUTE_OPERATE, "分派"),
    (EXCEPTION_DISTRIBUTE_OPERATE, "异常分派"),
    (CLAIM_OPERATE, "认领"),
    (SYSTEM_OPERATE, "自动执行"),
    (SUSPEND_OPERATE, "挂起"),
    (UNSUSPEND_OPERATE, "恢复"),
    (TERMINATE_OPERATE, "终止"),
    (WITHDRAW_OPERATE, "撤单"),
    (DELIVER_OPERATE, "转单"),
]

APPROVAL_CHOICES = [
    (TONGYI, "同意"),
    (JUJUE, "拒绝"),
]

ACTION_DICT = dict(ALL_ACTION_CHOICES)

METHOD_CHOICES = [
    ("==", "等于"),
    ("!=", "不等于"),
    (">", ">"),
    ("<", "<"),
    ("<=", "<="),
    (">=", ">="),
    ("issuperset", "包含"),
    ("notissuperset", "不包含"),
    ("in", "包含(字符类型)"),
    ("notin", "不包含(字符类型)"),
    # ("startswith", u"以某某开头"),
    # ("endswith", u"以某某结尾"),
]

FLOW_CONDITION_TYPE_CHOICES = [
    ("default", "默认"),
    ("by_field", "字段判断"),
]

# 标准运维任务执行状态
TASK_STATUS_CHOICE = [
    (FINISHED, "执行成功"),
    (FAILED, "执行失败"),
    (RUNNING, "执行中"),
]
TASK_STATUS_DICT = dict(TASK_STATUS_CHOICE)

# 标准运维字段类型对应表
SOPS_FIELD_MAP = [
    ("int", "INT"),
    ("input", "STRING"),
    ("textarea", "TEXT"),
    ("datetime", "DATETIME"),
]

DEFAULT_START_AXIS = {"x": 150, "y": 150}
DEFAULT_FIRST_AXIS = {"x": 285, "y": 150}
DEFAULT_APPROVAL_AXIS = {"x": 575, "y": 150}
DEFAULT_END_AXIS = {"x": 620, "y": 150}

INNER_STATE_ID = "$__state_id$"
INNER_TICKET_ID = "$__ticket_id$"
INNER_API_INSTANCE_ID = "$__api_instance_id$"

BOOL_VALUE_CHOICE = {"TRUE": True, "FALSE": False}

SUPPORTED_TYPE = [
    "STRING",
    "TEXT",
    "INT",
    "DATE",
    "DATETIME",
    "SELECT",
    "RADIO",
    "TREESELECT",
    "MULTISELECT",
    "BOOLEAN",
    "CHECKBOX",
    "MEMBER",
    "MEMBERS",
    "CUSTOM-FORM",
    "INPUTSELECT",
    "RICHTEXT",
]

EXPORT_SUPPORTED_TYPE = [
    "STRING",
    "TEXT",
    "INT",
    "DATE",
    "DATETIME",
    "SELECT",
    "RADIO",
    "TREESELECT",
    "MULTISELECT",
    "BOOLEAN",
    "CHECKBOX",
    "MEMBER",
    "MEMBERS",
    "INPUTSELECT",
]

DEFAULT_SHOW_CONDITION = {
    "type": "and",
    "expressions": [{"key": "G_INT_1", "condition": "==", "value": 1}],
}
SHOW_DIRECTLY = 1
SHOW_BY_CONDITION = 0

SELECT_TYPE_CHOICES = {
    "SELECT": "单选下拉框",
    "RADIO": "单选框",
    "CHECKBOX": "复选框",
    "MULTISELECT": "多选下拉框",
    "TABLE": "表格",
}

VIRTUAL_TRANSITION_ID = -1

TYPE_CHOICES = [
    ("STRING", "单行文本"),
    ("TEXT", "多行文本"),
    ("INT", "数字"),
    ("DATE", "日期"),
    ("DATETIME", "时间"),
    ("DATETIMERANGE", "时间间隔"),
    ("TABLE", "表格"),
    ("SELECT", "单选下拉框"),
    ("INPUTSELECT", "可输入单选下拉框"),
    ("MULTISELECT", "多选下拉框"),
    ("CHECKBOX", "复选框"),
    ("RADIO", "单选框"),
    ("MEMBER", "单选人员选择"),
    ("MEMBERS", "多选人员选择"),
    # ("COMPLEX-MEMBERS", "复杂多选人员选择"),
    ("RICHTEXT", "富文本"),
    ("FILE", "附件上传"),
    ("CUSTOMTABLE", "自定义表格"),
    ("TREESELECT", "树形选择"),
    ("LINK", "链接"),
    ("CUSTOM-FORM", "自定义表单"),
    ("CASCADE", "级联"),
]

SOURCE_CHOICES = [
    ("CUSTOM", "自定义数据"),
    ("API", "接口数据"),
    ("DATADICT", "数据字典"),
    ("RPC", "系统数据"),
    ("CUSTOM_API", "自定义API"),
]

LAYOUT_CHOICES = [
    ("COL_6", "半行"),
    ("COL_12", "整行"),
]

VALIDATE_CHOICES = [
    ("OPTION", "可选"),
    ("REQUIRE", "必填"),
    # ("REGEX", u"正则"),
]

# 节点触发器类型
STATE_BUTTON = "state_button"

TRIGGER_TYPE = [
    (STATE_BUTTON, "节点按钮"),
]

DEFAULT_FLOW_CONDITION = {
    "expressions": [
        {
            "type": "and",
            "expressions": [{"key": "G_INT_1", "condition": "==", "value": 1}],
        }
    ],
    "type": "and",
}

DEFAULT_API_INSTANCE = {
    "bk_biz_id": {
        "req_body": {"fields": ["bk_biz_id", "bk_biz_name"]},
        "rsp_data": "data.info",
    }
}

NORMAL_STATE_LABEL_PREFIX = "|N"
ROUTER_STATE_LABEL_PREFIX = "|P"
COVERAGE_STATE_LABEL_PREFIX = "|C"
GLOBAL_LABEL = "G"
LABEL_PREFIX = "|"

REVOKE_TYPE = enum(ALL=1, FIRST=2, ASSIGN=3)
