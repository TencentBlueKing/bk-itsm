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
from rest_framework import serializers

from common.log import logger
from itsm.service.validators import service_type_validator
from itsm.ticket_status.models import TicketStatus


def save_ticket_status_validate(service_type, ticket_status_ids, start_status_id, over_status_ids):
    """保存工单状态的校验"""

    service_type_validator(service_type)

    # 确保传入完整的工单状态ID用于排序
    status_ids = list(TicketStatus.objects.status_of_service_type(service_type).values_list("id", flat=True))
    if set(status_ids) != set(ticket_status_ids):
        raise serializers.ValidationError(_("用于排序的工单状态参数不合法，请联系管理员"))

    if start_status_id not in status_ids:
        raise serializers.ValidationError(_("设置为起始状态的工单状态不存在，请联系管理员"))

    if set(over_status_ids).difference(status_ids):
        logger.error("设置为结束状态的工作状态(id=%s)不存在" % set(over_status_ids).difference(status_ids))
        raise serializers.ValidationError(_("设置为结束状态的工作状态不存在，请联系管理员"))


def save_transit_validate(service_type, transits):
    """保存状态转换规则的校验"""
    service_type_validator(service_type)

    # 校验规则: 1. 所有status_id必须合法 2. 结束状态无法继续转换
    all_status_ids = []
    not_over_status_ids = []
    status = TicketStatus.objects.filter(service_type=service_type)

    for s in status:
        all_status_ids.append(s.id)

        if not s.is_over:
            not_over_status_ids.append(s.id)

    for transit in transits:
        if transit.get("from_status") not in all_status_ids or transit.get("to_status") not in all_status_ids:
            logger.error("单据状态ID(%s)不存在" % transit.get("from_status"))
            serializers.ValidationError(_("单据状态不存在，请联系管理员"))

        if transit.get("from_status") not in not_over_status_ids:
            logger.error("单据状态ID(%s)为结束状态，无法继续转换" % transit.get("from_status"))
            serializers.ValidationError(_("单据状态为结束状态，无法继续转换"))


def set_transit_rule_validate(from_status, to_status_id, threshold, threshold_unit):
    """设置状态转换规则"""

    if threshold_unit not in ['m', 'h', 'd']:
        raise serializers.ValidationError(_("阈值单位错误，请重新输入"))

    if not str(threshold).isdigit():
        raise serializers.ValidationError(_("阈值必须为正整数，请重新输入"))

    try:
        TicketStatus.objects.get(id=to_status_id, service_type=from_status.service_type)
    except TicketStatus.DoesNotExist:
        raise serializers.ValidationError(_("流转目标的单据状态不存在，请联系管理员"))


def from_status_id_validator(from_status_id):
    """源工单状态id校验"""
    if from_status_id is None:
        raise serializers.ValidationError(_("from_status_id不能为空"))
    if not TicketStatus.objects.filter(id=from_status_id).exists():
        raise serializers.ValidationError(_("id为【{}】的工单状态不存在，请联系管理员".format(from_status_id)))


class TicketStatusValidator(object):
    """工单状态验证器"""

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.name_unique_validate(value)

    def name_unique_validate(self, value):
        """名称唯一性校验"""
        if self.instance:
            obj = TicketStatus.objects.filter(service_type=self.instance.service_type).exclude(id=self.instance.id)
        else:
            service_type = value.get('service_type')
            obj = TicketStatus.objects.filter(service_type=service_type)
        if obj.filter(name=value.get('name')).exists():
            raise serializers.ValidationError(_("状态名称已存在，请重新输入"))
