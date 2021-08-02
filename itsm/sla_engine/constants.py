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

from django.utils.translation import gettext as _

TO_MIN = {"m": 1, "h": 60, "d": 24 * 60}

TO_SECOND = {"m": 60, "h": 60 * 60, "d": 24 * 60 * 60}

PERCENT = 0.01

# Redis中SLA动作触发时间集合
SLA_ACTION_TIME = "SLA_ACTION_TIME"

# SlaTask 任务类型
UNACTIVATED = 1  # 未激活
RUNNING = 2  # 计时中
PAUSED = 3  # 暂停中
STOPPED = 4  # 已停止
TIMEOUT = 5  # 已超时

SLA_TASK_STATUS = [
    (UNACTIVATED, _("未激活")),
    (RUNNING, _("计时中")),
    (PAUSED, _("暂停中")),
    (STOPPED, _("已停止")),
]

# 升级事件类型
REPLY_WARING = 1
REPLY_TIMEOUT = 2
HANDLE_WARING = 3
HANDLE_TIMEOUT = 4

ACTION_POLICY_TYPES = [
    (REPLY_WARING, _("响应提醒")),
    (REPLY_TIMEOUT, _("响应超时")),
    (HANDLE_WARING, _("处理提醒")),
    (HANDLE_TIMEOUT, _("处理超时")),
]

# SlaTask 计时状态
NORMAL = 5  # 正常
SLA_TIMING_STATUS = [
    (REPLY_WARING, _("响应提醒")),
    (REPLY_TIMEOUT, _("响应超时")),
    (HANDLE_WARING, _("处理提醒")),
    (HANDLE_TIMEOUT, _("处理超时")),
    (NORMAL, _("正常"))
]

REPLY_TIMEOUT_COLOR = "#FFF5E3"  # 响应超时颜色
HANDLE_TIMEOUT_COLOR = "#FFECEC"  # 处理超时颜色

WARING_TYPE = [REPLY_WARING, HANDLE_WARING]

# 响应操作标识
REPLY = "REPLY"
REPLY_NAME = _("响应")
