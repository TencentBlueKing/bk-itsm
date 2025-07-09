# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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


from django.urls import include, re_path


__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2025 Tencent BlueKing. All Rights Reserved."


# Uncomment the next two lines to enable the admin:

# 公共URL配置
from itsm.gateway.views import get_batch_users

urlpatterns = [
    # 流程管理模块
    re_path(r"^workflow/", include("itsm.workflow.urls")),
    # 单据模块
    re_path(r"^ticket/", include("itsm.ticket.urls")),
    # 任务模块
    re_path(r"^task/", include("itsm.task.urls")),
    # 服务模块
    re_path(r"^service/", include("itsm.service.urls")),
    # sla模块
    re_path(r"^sla/", include("itsm.sla.urls")),
    # postman
    re_path(r"^postman/", include("itsm.postman.urls")),
    # 角色模块
    re_path(r"^role/", include("itsm.role.urls")),
    # iadmin
    re_path(r"^iadmin/", include("itsm.iadmin.urls")),
    # 网关转发模块，目前主要用于转发esb侧的接口调用
    re_path(r"^gateway/", include("itsm.gateway.urls")),
    # "杂种"模块，没有model，且不知道放哪里合适，就放到这个模块吧！
    re_path(r"^misc/", include("itsm.misc.urls")),
    # 单据状态模块
    re_path(r"^ticket_status/", include("itsm.ticket_status.urls")),
    # Trigger Module
    re_path(r"^trigger/", include("itsm.trigger.urls")),
    # iam
    re_path(r"^iam/", include("itsm.auth_iam.urls")),
    # iam
    re_path(r"^project/", include("itsm.project.urls")),
    # 人员选择器
    re_path(r"^c/compapi/v2/usermanage/fs_list_users/$", get_batch_users),
    # 蓝鲸插件服务
    re_path(r"^plugin_service/", include("itsm.plugin_service.urls")),
]
