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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

# 隐藏后台功能单元

import datetime
import json

from django.contrib.auth.decorators import permission_required
from django.db.models import F
from django.http import HttpResponse

from itsm.component.utils.client_backend_query import get_systems
from itsm.component.utils.misc import JsonEncoder
from itsm.helper.tasks import (
    _db_fix_after_2_0_3,
    _db_fix_after_2_0_7,
    _db_fix_after_2_0_9,
    _db_fix_after_2_0_14,
    _db_fix_after_2_1_1,
    _db_fix_after_2_1_9,
    _db_fix_after_2_1_x,
    _db_fix_default_value_for_field,
    _db_fix_for_attachments,
    _db_fix_for_ticket_processors,
    _db_fix_from_1_1_22_to_2_1_x,
    _db_fix_from_2_1_x_to_2_2_1,
    _db_fix_sla,
    _fix_ticket_title,
    _update_logs_type,
    _db_fix_for_service_catalog,
    _db_fix_for_workflow_to_2_5_9,
    _db_fix_for_blueapps_after_2_6_0,
)
from itsm.ticket.models import Ticket, TicketEventLog


@permission_required('is_superuser')
def db_fix_for_blueapps_after_2_6_0(request):
    """服务目录添加前置路径"""
    try:
        _db_fix_for_blueapps_after_2_6_0.delay()
        return HttpResponse("_db_fix_for_blueapps_after_2_6_0: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def db_fix_for_workflow_after_2_5_9(request):
    """服务目录添加前置路径"""
    try:
        _db_fix_for_workflow_to_2_5_9.delay()
        return HttpResponse("_db_fix_for_workflow_to_2_5_9: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def db_fix_for_service_catalog(request):
    """服务目录添加前置路径"""
    try:
        _db_fix_for_service_catalog.delay()
        return HttpResponse("db_fix_for_service_catalog: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def db_fix_after_2_3_1(request):
    try:
        print("%s start task db_fix_after_2_3_1" % request.user.username)
        _db_fix_default_value_for_field.delay()
        return HttpResponse("db_fix_after_2_3_1: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def db_fix_after_2_2_17(request):
    try:
        print("%s start task db_fix_after_2_2_17" % request.user.username)
        _db_fix_for_ticket_processors.delay()
        return HttpResponse("db_fix_after_2_2_17: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def db_fix_for_attachments(request):
    try:
        _db_fix_for_attachments.delay()
        return HttpResponse("_db_fix_for_attachments: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required('is_superuser')
def export_api_system(request):
    system = get_systems()
    response = HttpResponse(content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=bk_itsm_system_{}.json".format(
        datetime.datetime.now().strftime('%Y%m%d%H%M')
    )
    response.write(json.dumps(system, cls=JsonEncoder, indent=2))

    return response


@permission_required("is_superuser")
def update_logs_type(request):
    """修复流转日志type"""
    try:
        _update_logs_type.apply_async()
        return HttpResponse("_update_logs_type: 任务下发到后台，请耐心等待，具体结果，请查看celery日志.")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required("is_superuser")
def fix_ticket_title(request):
    """补全以往单据的title"""
    try:
        _fix_ticket_title.apply_async()
        return HttpResponse("_fix_ticket_title: 任务下发到后台，请耐心等待，具体结果，请查看celery日志.")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required("is_superuser")
def db_fix_after_2_0_3(request):
    try:
        _db_fix_after_2_0_3.apply_async()
        return HttpResponse("_db_fix_after_2_0_3: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required("is_superuser")
def db_fix_after_2_1_x(request):
    """第二次数据迁移"""
    try:
        _db_fix_after_2_1_x.delay()
        return HttpResponse("_db_fix_after_2_1_x: 任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse('任务下发异常:%s' % e)


@permission_required("is_superuser")
def db_fix_ticket_end_at_after_2_0_5(request):
    try:
        Ticket.objects.filter(is_draft=False, current_status="FINISHED", end_at__isnull=True).update(
            end_at=F("update_at")
        )

        return HttpResponse("命令执行成功")
    except Exception as e:
        return HttpResponse("任务执行失败：%s" % e)


@permission_required("is_superuser")
def db_fix_deal_time_after_2_0_5(request):
    try:
        for log in TicketEventLog.objects.filter(type='CLAIM', deal_time=0):
            log.update_deal_time()
        return HttpResponse("命令执行成功")
    except Exception as e:
        return HttpResponse("任务执行失败：%s" % e)


@permission_required("is_superuser")
def db_fix_after_2_0_7(request):
    try:
        _db_fix_after_2_0_7.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


@permission_required("is_superuser")
def db_fix_after_2_0_9(request):
    try:
        _db_fix_after_2_0_9.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


@permission_required("is_superuser")
def db_fix_after_2_0_14(request):
    """
    修复脏数据导致安全问题
    """
    try:
        _db_fix_after_2_0_14.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


@permission_required("is_superuser")
def db_fix_after_2_1_1(request):
    """
    打回日志添加类型
    :param request:
    :return:
    """
    try:
        _db_fix_after_2_1_1.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


def db_fix_sla(request):
    try:
        _db_fix_sla.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


def db_fix_after_2_1_9(request):
    try:
        _db_fix_after_2_1_9.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


@permission_required('is_superuser')
def db_fix_from_1_1_22_to_2_1_16(request):
    try:
        _db_fix_from_1_1_22_to_2_1_x.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


def db_fix_from_2_1_x_to_2_2_1(request):
    try:
        _db_fix_from_2_1_x_to_2_2_1.apply_async()
        return HttpResponse("任务下发到后台，请耐心等待，具体结果，请查看celery日志。")
    except Exception as e:
        return HttpResponse("任务下发异常：%s" % e)


@permission_required('is_superuser')
def weekly_statical(request):
    from itsm.ticket.tasks import weekly_statical as weekly_statical_task

    try:
        weekly_statical_task()
    except BaseException as error:
        return HttpResponse("发送邮件任务失败： %s" % str(error))
    return HttpResponse("发送邮件任务已完成")
