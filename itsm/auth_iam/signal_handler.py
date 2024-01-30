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

from django.conf import settings
from itsm.auth_iam.utils import grant_instance_creator_related_actions
from itsm.component.constants import SOURCE_TICKET
from itsm.role.models import UserRole
from itsm.trigger.models import Trigger


def grant_related_action_after_instance_created(
    sender, instance, created, *args, **kwargs
):
    # 对于生成的流程版本的触发器，将不再关联授权
    if isinstance(instance, Trigger):
        if instance.source_type == SOURCE_TICKET:
            return

    # 对于非用户组角色
    if isinstance(instance, UserRole):
        if instance.role_type != "GENERAL":
            return

    if not (created and getattr(sender, "need_auth_grant", False)):
        return

    if settings.ENVIRONMENT == "dev":
        # dev 环境不走权限中心
        return

    grant_instance_creator_related_actions(instance)
