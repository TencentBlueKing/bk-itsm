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


from calendar import FRIDAY, MONDAY, SATURDAY, SUNDAY, THURSDAY, TUESDAY, WEDNESDAY

from django.conf import settings
from django.utils.translation import ugettext as _

from itsm.component.utils.basic import choices_to_namedtuple, tuple_choices


class ConstantDict(dict):
    """ConstantDict is a subclass of :class:`dict`, implementing __setitem__
    method to avoid item assignment::

    >>> d = ConstantDict({'key': 'value'})
    >>> d['key'] = 'value'
    Traceback (most recent call last):
        ...
    TypeError: 'ConstantDict' object does not support item assignment
    """

    def __setitem__(self, key, value):
        raise TypeError(
            "'%s' object does not support item assignment" % self.__class__.__name__
        )

    def update(self, **kwargs):
        raise TypeError(
            "'%s' object does not support item assignment" % self.__class__.__name__
        )


# 返回状态码
CODE_STATUS_TUPLE = (
    "OK",
    "UNAUTHORIZED",
    "VALIDATE_ERROR",
    "METHOD_NOT_ALLOWED",
    "PERMISSION_DENIED",
    "SERVER_500_ERROR",
    "OBJECT_NOT_EXIST",
    "FAILED",
)
CODE_STATUS_CHOICES = tuple_choices(CODE_STATUS_TUPLE)
ResponseCodeStatus = choices_to_namedtuple(CODE_STATUS_CHOICES)

# 常规字段长度定义
LEN_SHORT = 32
LEN_NORMAL = 64
LEN_MIDDLE = 128
LEN_LONG = 255
LEN_X_LONG = 1000
LEN_XX_LONG = 10000
LEN_XXX_LONG = 20000

# 字段默认值
EMPTY_INT = 0
EMPTY_STRING = ""
EMPTY_DISPLAY_STRING = "--"
EMPTY_LIST = []
EMPTY_DICT = ConstantDict({})
EMPTY_VARIABLE = {"inputs": [], "outputs": []}
DEFAULT_BK_BIZ_ID = -1
EMPTY = "EMPTY"

# 公共常量定义
DEFAULT_STRING = "DEFAULT"
DEFAULT_VERSION = "0"
DEFAULT_ENGINE_VERSION = "PIPELINE_V1"

FRONT_ORDER = 0
END_ORDER = 9999
DEFAULT_ORDER = -1

# CACHE
CACHE_5MIN = 5 * 60
CACHE_10MIN = 10 * 60
CACHE_30MIN = 30 * 60
CACHE_1H = 1 * 60 * 60

WEIXIN = "WEIXIN"
EMAIL = "EMAIL"
SMS = "SMS"
GENERAL_NOTICE = "GENERAL"

NOTIFY_TYPE_CHOICES = [
    (WEIXIN, "微信"),
    (EMAIL, "邮箱"),
    (SMS, "短信"),
]

# 兼容已存在的通知方式
# GENERAL_NOTICE 不作为通知方式, 不存入 Notify
NOTIFY_TYPE_MAPPING = {"weixin": WEIXIN, "mail": EMAIL, "sms": SMS}

# 内置通知方式
# GENERAL_NOTICE 通知模版, 存入 CustomNotice
# 在获取通知方式失败时使用通用通知模版构建通知信息
BUILTIN_NOTIFY_TYPE = [WEIXIN, EMAIL, SMS, GENERAL_NOTICE]

HOLIDAY = "HOLIDAY"
WORKDAY = "WORKDAY"
NORMAL_DAY = "NORMAL"
DAY_TYPE_CHOICES = [
    (NORMAL_DAY, "常规日"),
    (WORKDAY, "加班日"),
    (HOLIDAY, "节假日"),
]

WEEKDAY_CHOICES = [
    (MONDAY, "MONDAY"),
    (TUESDAY, "TUESDAY"),
    (WEDNESDAY, "WEDNESDAY"),
    (THURSDAY, "THURSDAY"),
    (FRIDAY, "FRIDAY"),
    (SATURDAY, "SATURDAY"),
    (SUNDAY, "SUNDAY"),
]

# 日志来源
WEB = "WEB"
MOBILE = "MOBILE"
API = "API"
SYS = "SYS"  # 特指提单/结束节点

# 0点~23点
NOTIFY_FREQ_CHOICES = tuple(60 * 60 * i for i in range(25))
NOTIFY_GLOBAL_VARIABLES = [
    {
        "key": "sn",
        "name": _("单号"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "title",
        "name": _("标题(单据)"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "creator",
        "name": _("提单人"),
        "source": "ticket",
        "hidden": False,
        "type": "MEMBER",
    },
    {
        "key": "create_at",
        "name": _("提单时间"),
        "source": "ticket",
        "hidden": False,
        "type": "DATETIME",
    },
    {
        "key": "service_type_name",
        "name": _("服务项"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "catalog_fullname",
        "name": _("服务目录"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "catalog_service_name",
        "name": _("服务（服务目录+服务项）"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "current_status_display",
        "name": _("单据状态"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "running_status",
        "name": _("当前步骤(单据)"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    {
        "key": "ticket_url",
        "name": _("单据详情链接"),
        "source": "ticket",
        "hidden": False,
        "type": "STRING",
    },
    # {"key": "sla_cost_percent", "name": _("单据处理进度"), "source": "ticket", "hidden": False, "type": "STRING"},
    {
        "key": "ticket_current_processors",
        "name": _("当前各节点处理人"),
        "source": "ticket",
        "type": "MEMBERS",
    },
]

TICKET_GLOBAL_VARIABLES = [
    # dot style key not supported:
    # ticket.create -> constant content is invalid with error ['Undefined' object has no attribute 'creator']
    {"key": "ticket_sn", "name": _("单号"), "source": "ticket", "type": "STRING"},
    {"key": "ticket_title", "name": _("标题"), "source": "ticket", "type": "STRING"},
    {
        "key": "ticket_ticket_url",
        "name": _("单据链接"),
        "source": "ticket",
        "type": "STRING",
    },
    {"key": "ticket_creator", "name": _("提单人"), "source": "ticket", "type": "MEMBER"},
    {
        "key": "ticket_create_at",
        "name": _("提单时间"),
        "source": "ticket",
        "type": "DATETIME",
    },
    {
        "key": "ticket_service_type",
        "name": _("服务项"),
        "source": "ticket",
        "type": "STRING",
    },
    {
        "key": "ticket_current_status",
        "name": _("单据状态"),
        "source": "ticket",
        "type": "STRING",
    },
    {
        "key": "ticket_current_status_display",
        "name": _("单据状态名称"),
        "source": "ticket",
        "type": "STRING",
    },
    {
        "key": "ticket_bk_biz_id",
        "name": _("关联业务ID"),
        "source": "ticket",
        "type": "STRING",
    },
    {
        "key": "ticket_current_processors",
        "name": _("当前各节点处理人"),
        "source": "ticket",
        "type": "MEMBERS",
    },
    {
        "key": "ticket_sops_task_summary",
        "name": _("SOPS总结信息"),
        "source": "ticket",
        "type": "STRING",
    },
    {
        "key": "ticket_all_task_processors",
        "name": _("所有任务处理人"),
        "source": "ticket",
        "type": "MEMBERS",
    },
]

TASK_GLOBAL_VARIABLES = [
    # dot style key not supported:
    # ticket.create -> constant content is invalid with error ['Undefined' object has no attribute 'creator']
    {"key": "task_id", "name": _("任务ID"), "source": "task", "type": "STRING"},
    {"key": "task_name", "name": _("任务名称"), "source": "task", "type": "STRING"},
    {
        "key": "task_component_type_display",
        "name": _("任务类型名"),
        "source": "task",
        "type": "STRING",
    },
    {"key": "task_creator", "name": _("任务创建人"), "source": "task", "type": "MEMBER"},
    {"key": "task_operator", "name": _("任务处理人"), "source": "task", "type": "MEMBER"},
    {
        "key": "task_create_at",
        "name": _("任务创建时间"),
        "source": "task",
        "type": "DATETIME",
    },
    {"key": "task_status", "name": _("任务状态"), "source": "task", "type": "STRING"},
    {
        "key": "task_status_display",
        "name": _("任务状态名"),
        "source": "task",
        "type": "STRING",
    },
    {
        "key": "task_sops_step_list",
        "name": _("SOPS步骤信息"),
        "source": "task",
        "type": "STRING",
    },
]

# 开始序号
FIRST_ORDER = 1

# 获取key的前缀, 使用redis缓存, 保证不同环境下的key不相同
PREFIX_KEY = "%s:%s:" % (settings.APP_CODE, settings.ENVIRONMENT)
API_PERMISSION_ERROR_CODE = 9900403

TIME_DELTA = {
    "days": "DATE_FORMAT({field_name},'%%Y-%%m-%%d')",
    "weeks": "DATE_FORMAT({field_name},'%%Y-%%u')",
    "months": "DATE_FORMAT({field_name},'%%Y-%%m')",
    "years": "DATE_FORMAT({field_name},'%%Y')",
}


EXEMPT_HTTPS_REDIRECT = ("/openapi/", "/api/iam/resources/v1", "/monitor/")
