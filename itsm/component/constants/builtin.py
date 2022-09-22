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

import itertools

from django.utils.translation import gettext as _

from .service import *  # noqa
from .ticket import *  # noqa

# 内置影响范围/严重程度/优先级
IMPACTS = URGENCYS = PRIORITYS = [
    # key/name/order
    (1, _("低"), 1),
    (2, _("中"), 2),
    (3, _("高"), 3),
]

# 对应RPC数据的关键字
STATUS = "ticket_status"
TABLE_FIELDS = "table_fields"
STATE_FIELDS = "first_state_fields"
FLOW_STATES = "flow_states"
SERVICE_CATALOG = "service_catalog"

# 对应数据字典的关键字
PY_IMPACT = "IMPACT"
PX_URGENCY = "URGENCY"
PRIORITY = "PRIORITY"

SLA_MATRIX = [PY_IMPACT, PX_URGENCY]

EVENT_TYPE = {"fault": "故障", "alarm": "告警"}
PLAT_TYPE = {"fault": "业务平台", "alarm": "云平台"}

FAULT_SOURCE_CHOICES = [
    ("INSPECTION", "巡检"),
    ("MANUAL", "人工报障"),
    ("MONITOR", "监控"),
]

STATE_TAG_TYPE = {DEFAULT_STRING: "默认"}

# 通知规则
NOTIFY_RULE_CHOICES = [
    ("NONE", "不通知"),
    ("ONCE", "发送一次"),
    ("RETRY", "重试发送，直到处理完"),
]

# 内置公共字段
DEFAULT_TEMPLATE_FIELDS = [
    # 公共字段
    # name, type, source_type, choice, key, display, related_fields, source_uri, desc,
    # is_builtin, is_readonly, is_valid, regex
    (
        "标题",
        "STRING",
        "CUSTOM",
        [],
        FIELD_TITLE,
        True,
        {},
        "",
        "请输入标题",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "影响范围",
        "SELECT",
        "DATADICT",
        [],
        FIELD_PY_IMPACT,
        True,
        {},
        PY_IMPACT,
        "请选择影响范围",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "紧急程度",
        "SELECT",
        "DATADICT",
        [],
        FIELD_PX_URGENCY,
        True,
        {},
        PX_URGENCY,
        "请选择紧急程度",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "优先级",
        "SELECT",
        "DATADICT",
        [],
        FIELD_PRIORITY,
        True,
        {"rely_on": [FIELD_PX_URGENCY, FIELD_PY_IMPACT]},
        PRIORITY,
        "请选择优先级",
        True,
        True,
        True,
        "EMPTY",
    ),
    (
        "工单状态",
        "SELECT",
        "RPC",
        [],
        FIELD_STATUS,
        True,
        {},
        STATUS,
        "请选择工单状态",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "申请内容",
        "TEXT",
        "CUSTOM",
        [],
        FIELD_APPLY_CONTENT,
        True,
        {},
        "",
        "请输入申请内容",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "申请理由",
        "TEXT",
        "CUSTOM",
        [],
        FIELD_APPLY_REASON,
        True,
        {},
        "",
        "请输入理由",
        True,
        False,
        True,
        "EMPTY",
    ),
    (
        "关联业务",
        "SELECT",
        "API",
        [],
        FIELD_BIZ,
        True,
        {},
        "",
        "请选择关联业务",
        True,
        False,
        True,
        "EMPTY",
    ),
]

# 内置数据字典·
BUILTIN_SYSDICT_LIST = [
    {
        "key": "CHANGE_TYPE",
        "name": "变更类型",
        "items": {},
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "EVENT_TYPE",
        "name": "事件类型",
        "items": EVENT_TYPE,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "PLAT_TYPE",
        "name": "平台类型",
        "items": PLAT_TYPE,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "EVENT_SOURCE_TYPE",
        "name": "事件来源",
        "items": dict(FAULT_SOURCE_CHOICES),
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "SERVICE_TYPE",
        "name": "服务类型",
        "items": SERVICE_DICT,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "FLOW_TYPE",
        "name": "流程类型",
        "items": dict(FLOW_TYPE_CHOICE),
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "OPERATE_TYPE",
        "name": "操作类型",
        "items": OPERATE_TYPE,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": "STATE_TAG_TYPE",
        "name": "节点标签类型",
        "items": STATE_TAG_TYPE,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": PY_IMPACT,
        "name": "影响范围",
        "items": IMPACTS,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": PX_URGENCY,
        "name": "紧急程度",
        "items": URGENCYS,
        "init_by": "jsondata",
        "is_show": True,
    },
    {
        "key": PRIORITY,
        "name": "优先级",
        "items": PRIORITYS,
        "init_by": "jsondata",
        "is_show": True,
    },
    # {"key": "TIMEZONE", "name": u"时区", "items": "timezone.json", "init_by": "jsonfile"},
]

# 紧急程度/影响范围/优先级 默认启用项
for service, matrix in itertools.product(SERVICE_LIST, SLA_MATRIX):
    key = "%s_%s" % (service.upper(), matrix)
    items = []

    if matrix == PY_IMPACT:
        items = [(x[0], x[1], 0) for x in IMPACTS]
    elif matrix == PX_URGENCY:
        items = [(x[0], x[1], 0) for x in URGENCYS]

    BUILTIN_SYSDICT_LIST.append(
        {
            "key": key,
            "name": key,
            "items": items,
            "init_by": "jsondata",
            "is_show": False,
        }
    )

ITSM_CHANNEL_LIST = [{"code": "itsm_sla", "label": "ITSM内置SLA", "desc": ""}]
ITSM_CHANNEL_CHOICE = [item["code"] for item in ITSM_CHANNEL_LIST]
ITSM_CHANNEL_PATH_DICT = {
    "itsm_sla": {
        "label": "SLA",
        "path": "/service/slas",
        "system_id": 2,
        "type": 1,
        "version": "v2",
        "desc": "",
        "method": "GET",
    }
}

# 内置基础模型
DEFAULT_TABLE = [
    (
        "默认",
        "默认基础模型",
        [FIELD_TITLE, FIELD_PY_IMPACT, FIELD_PX_URGENCY, FIELD_PRIORITY, FIELD_STATUS],
    ),
    (
        "变更",
        "变更管理基础模型",
        [FIELD_TITLE, FIELD_PY_IMPACT, FIELD_PX_URGENCY, FIELD_PRIORITY, FIELD_STATUS],
    ),
    (
        "事件",
        "事件管理基础模型",
        [FIELD_TITLE, FIELD_PY_IMPACT, FIELD_PX_URGENCY, FIELD_PRIORITY, FIELD_STATUS],
    ),
    (
        "请求",
        "请求管理基础模型",
        [FIELD_TITLE, FIELD_PY_IMPACT, FIELD_PX_URGENCY, FIELD_PRIORITY, FIELD_STATUS],
    ),
    (
        "问题",
        "问题管理基础模型",
        [FIELD_TITLE, FIELD_PY_IMPACT, FIELD_PX_URGENCY, FIELD_PRIORITY, FIELD_STATUS],
    ),
    (
        "审批",
        "一般审批流程基础模型",
        [FIELD_TITLE, FIELD_STATUS, FIELD_APPLY_CONTENT, FIELD_APPLY_REASON],
    ),
    (
        "简单",
        "只有一个标题字段的基础模型",
        [FIELD_TITLE],
    ),
]
TABLE = "TABLE"
BASE_MODEL = "BASE-MODEL"

# 内置服务目录 V2.2.X
CATALOG = [
    {"level": 1, "name": _("服务反馈"), "key": "FUWUFANKUI", "parent_key": "root"},
    {"level": 1, "name": _("基础配置"), "key": "JICHUPEIZHI", "parent_key": "root"},
    {"level": 1, "name": _("资源服务"), "key": "ZIYUANFUWU", "parent_key": "root"},
    {"level": 2, "name": _("咨询建议"), "key": "ZIXUNJIANYI", "parent_key": "FUWUFANKUI"},
    {"level": 2, "name": _("问题管理"), "key": "WENTIGUANLI", "parent_key": "FUWUFANKUI"},
    {"level": 2, "name": _("事件管理"), "key": "SHIJIANGUANLI", "parent_key": "FUWUFANKUI"},
    {"level": 2, "name": _("主机管理"), "key": "ZHUJIGUANLI", "parent_key": "JICHUPEIZHI"},
    {"level": 2, "name": _("业务管理"), "key": "YEWUGUANLI", "parent_key": "JICHUPEIZHI"},
    {"level": 2, "name": _("运维资源"), "key": "YUNWEIZIYUAN", "parent_key": "ZIYUANFUWU"},
]

# 角色类型和角色名初始化
# ================================================
DEFAULT_USERS = ",admin,"
USER_ROLE_CHOICES = [
    # role_key name 3role_type access 5members desc
    # GENERAL
    ("DEV", "开发", "GENERAL", "", DEFAULT_USERS, "DEV"),
    ("PM", "开发经理", "GENERAL", "", DEFAULT_USERS, "PM"),
    ("OPT", "运营", "GENERAL", "", DEFAULT_USERS, "OPT"),
    ("OPS", "运维", "GENERAL", "", DEFAULT_USERS, "OPS"),
    ("TEST", "测试", "GENERAL", "", DEFAULT_USERS, "TEST"),
    # 新增角色类型
    ("GENERAL_6", "变更经理", "GENERAL", "", DEFAULT_USERS, ""),
    ("GENERAL_7", "故障派单员", "GENERAL", "", DEFAULT_USERS, ""),
    ("GENERAL_8", "服务台小组", "GENERAL", "", DEFAULT_USERS, ""),
    # ADMIN
    (
        ADMIN_STATICS_MANAGER_KEY,
        "工单统计管理员",
        "ADMIN",
        ADMIN_READ_ONLY,
        DEFAULT_USERS,
        "可查看所有单据",
    ),
    (
        ADMIN_SUPERUSER_KEY,
        "ITSM超级管理员",
        "ADMIN",
        ADMIN_SUPERUSER,
        DEFAULT_USERS,
        "可查看并处理所有单据",
    ),
    (
        WORKFLOW_SUPERUSER_KEY,
        "流程管理员",
        "ADMIN",
        WORKFLOW_SUPERUSER,
        DEFAULT_USERS,
        "可管理自己有权限的流程",
    ),
    (
        WIKI_ADMIN_SUPERUSER_KEY,
        "知识库管理员",
        "ADMIN",
        WIKI_ADMIN_SUPERUSER,
        DEFAULT_USERS,
        "可管理知识库所有文章",
    ),
    # IAM
    ("super_manager", "超级管理员", "IAM", "", "", "权限中心管理权限最高的角色"),
    ("system_manager", "系统管理员", "IAM", "", "", "每个接入系统在权限中心管理权限最高的角色"),
    ("rating_manager", "分级管理员", "IAM", "", "", "根据不同权限范围拥有其所在范围内的管理权限的角色"),
    ("instance_approver", "实例审批人", "IAM", "", "", "根据不同权限范围拥有其所在实例范围内的管理权限的角色"),
]

ROLE_CHOICES = [
    # type    name    is_display   is_processor
    (CMDB, "CMDB业务公用角色", True, True),
    (GENERAL, "自定义角色", True, True),
    (ADMIN, "管理员角色表", True, False),
    (OPEN, "不限", False, True),
    (PERSON, "个人", False, True),
    (STARTER, "提单人", False, True),
    (STARTER_LEADER, "提单人上级", False, True),
    (ASSIGN_LEADER, "指定节点处理人上级", False, True),
    (BY_ASSIGNOR, "派单人指定", False, True),
    (EMPTY, "无", False, True),
    (ORGANIZATION, "组织架构", False, True),
    (VARIABLE, "引用变量", False, True),
    (IAM, "权限中心角色", False, True),
    (API, "第三方系统", False, True),
]

BUILTIN_SERVICES = [{"name": "帐号开通申请", "flow_name": "一般审批流程", "desc": "内置审批服务"}]

BUILTIN_IAM_SERVICES = [
    {
        "name": "默认审批流程",
        "flow_name": "默认审批流程",
        "desc": "默认审批服务",
        "type": "IAM",
        "display_type": API,
        "display_role": "BK_IAM",
        "bind": "approve_service_catalog",
    },
    {
        "name": "用户组审批流程",
        "flow_name": "用户组审批流程",
        "desc": "用户组审批服务",
        "type": "IAM",
        "display_type": API,
        "display_role": "BK_IAM",
        "bind": "approve_service_catalog",
    },
]

BKBASE_CATALOG_KEY = "LANJINGJICHUPINGTAI"

BUILTIN_BKBASE_SERVICES = [
    {
        "name": "创建资源组",
        "flow_name": "创建资源组",
        "desc": "创建资源组",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "资源组扩容",
        "flow_name": "资源组扩容",
        "desc": "资源组扩容",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "项目申请资源组",
        "flow_name": "项目申请资源组",
        "desc": "项目申请资源组",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "项目申请业务数据",
        "flow_name": "项目申请业务数据",
        "desc": "项目申请业务数据",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "申请角色权限",
        "flow_name": "申请角色权限",
        "desc": "申请角色权限",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "离线计算补算",
        "flow_name": "离线计算补算",
        "desc": "离线计算补算",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "第三方应用授权申请",
        "flow_name": "第三方应用授权申请",
        "desc": "第三方应用授权申请",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
    {
        "name": "TDM数据源接入",
        "flow_name": "TDM数据源接入",
        "desc": "TDM数据源接入",
        "type": "BKBASE",
        "display_type": API,
        "display_role": "BK_BASE",
        "bind": BKBASE_CATALOG_KEY,
    },
]

DEFAULT_PROJECT_PROJECT_KEY = "0"
PUBLIC_PROJECT_PROJECT_KEY = "public"
LESSCODE_PROJECT_KEY = "lesscode"
