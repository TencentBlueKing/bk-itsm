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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2025 Tencent BlueKing. All Rights Reserved."

# 隐藏后台功能单元
# 安全说明：
#   1. 全部接口必须通过 itsm_superuser_required 校验，且写接口强制 POST + CSRF；
#   2. 异常一律走 safe_admin_response，仅记录日志，不向调用方回吐 str(e)/traceback；
#   3. 任何 print 调试已移除，统一改为 logger 输出，确保日志最小化原则。

import datetime
import json
import logging

from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_POST

from itsm.component.utils.client_backend_query import get_systems
from itsm.component.utils.misc import JsonEncoder
from itsm.helper.decorators import itsm_superuser_required, safe_admin_response
from itsm.helper.tasks import (
    _db_fix_after_2_0_3,
    _db_fix_after_2_0_7,
    _db_fix_after_2_0_9,
    _db_fix_after_2_0_14,
    _db_fix_after_2_1_1,
    _db_fix_after_2_1_x,
    _db_fix_default_value_for_field,
    _db_fix_for_attachments,
    _db_fix_for_ticket_processors,
    _db_fix_from_1_1_22_to_2_1_x,
    _fix_ticket_title,
    _update_logs_type,
    _db_fix_for_service_catalog,
    _db_fix_for_workflow_to_2_5_9,
    _db_fix_for_blueapps_after_2_6_0,
)
from itsm.ticket.models import Ticket, TicketEventLog

logger = logging.getLogger("root")

# 统一的"成功提示"——不携带任何内部实现细节
_OK_DISPATCHED = "任务已下发到后台，具体结果请查看 celery 日志。"


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_for_blueapps_after_2_6_0")
def db_fix_for_blueapps_after_2_6_0(request):
    """blueapps 升级后兼容修复"""
    _db_fix_for_blueapps_after_2_6_0.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_for_workflow_after_2_5_9")
def db_fix_for_workflow_after_2_5_9(request):
    """流程版本兼容修复"""
    _db_fix_for_workflow_to_2_5_9.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_for_service_catalog")
def db_fix_for_service_catalog(request):
    """服务目录添加前置路径"""
    _db_fix_for_service_catalog.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_3_1")
def db_fix_after_2_3_1(request):
    _db_fix_default_value_for_field.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_2_17")
def db_fix_after_2_2_17(request):
    _db_fix_for_ticket_processors.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_for_attachments")
def db_fix_for_attachments(request):
    _db_fix_for_attachments.delay()
    return HttpResponse(_OK_DISPATCHED)


# 此接口仅"读"导出，允许 GET，但仍要求超管
@require_http_methods(["GET"])
@itsm_superuser_required
@safe_admin_response("export_api_system")
def export_api_system(request):
    system = get_systems()
    response = HttpResponse(content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = "attachment; filename=bk_itsm_system_{}.json".format(
        datetime.datetime.now().strftime("%Y%m%d%H%M")
    )
    response.write(json.dumps(system, cls=JsonEncoder, indent=2))
    return response


@require_POST
@itsm_superuser_required
@safe_admin_response("update_logs_type")
def update_logs_type(request):
    """修复流转日志 type"""
    _update_logs_type.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("fix_ticket_title")
def fix_ticket_title(request):
    """补全以往单据的 title"""
    _fix_ticket_title.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_0_3")
def db_fix_after_2_0_3(request):
    _db_fix_after_2_0_3.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_1_x")
def db_fix_after_2_1_x(request):
    """第二次数据迁移"""
    _db_fix_after_2_1_x.delay()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_ticket_end_at_after_2_0_5")
def db_fix_ticket_end_at_after_2_0_5(request):
    Ticket.objects.filter(
        is_draft=False, current_status="FINISHED", end_at__isnull=True
    ).update(end_at=F("update_at"))
    return HttpResponse("命令执行成功")


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_deal_time_after_2_0_5")
def db_fix_deal_time_after_2_0_5(request):
    for log in TicketEventLog.objects.filter(type="CLAIM", deal_time=0):
        log.update_deal_time()
    return HttpResponse("命令执行成功")


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_0_7")
def db_fix_after_2_0_7(request):
    _db_fix_after_2_0_7.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_0_9")
def db_fix_after_2_0_9(request):
    _db_fix_after_2_0_9.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_0_14")
def db_fix_after_2_0_14(request):
    """修复脏数据导致安全问题"""
    _db_fix_after_2_0_14.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_after_2_1_1")
def db_fix_after_2_1_1(request):
    """打回日志添加类型"""
    _db_fix_after_2_1_1.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("db_fix_from_1_1_22_to_2_1_16")
def db_fix_from_1_1_22_to_2_1_16(request):
    _db_fix_from_1_1_22_to_2_1_x.apply_async()
    return HttpResponse(_OK_DISPATCHED)


@require_POST
@itsm_superuser_required
@safe_admin_response("weekly_statical")
def weekly_statical(request):
    """周报邮件发送（写操作，强制 POST + 超管）"""
    from itsm.ticket.tasks import weekly_statical as weekly_statical_task

    weekly_statical_task()
    return HttpResponse("发送邮件任务已完成")
