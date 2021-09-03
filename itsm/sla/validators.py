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

import re
from collections import Counter
from six.moves import map, range

from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _
from rest_framework import serializers

from itsm.component.constants import (
    PRIORITY,
    PX_URGENCY,
    PY_IMPACT,
    WEEKDAY_CHOICES,
    DEFAULT_PROJECT_PROJECT_KEY,
)
from itsm.component.drf.exception import ValidationError
from itsm.component.exceptions import ParamError
from itsm.service.models import DictData, ServiceSla, SysDict
from itsm.service.validators import service_type_validator
from itsm.sla.models import PriorityMatrix, Schedule, Sla


def matrix_of_service_type_validate(service_type):
    """获取指定服务类型下的矩阵视图全量数据的校验"""

    service_type_validator(service_type)


def priority_value_validate(service_type, urgency_id, impact_id):
    """根据影响范围、紧急度获取优先级的校验"""

    if not all([service_type, urgency_id, impact_id]):
        raise ParamError(_("参数缺失，请联系管理员"))

    service_type_validator(service_type)

    try:
        urgency = DictData.objects.get(id=urgency_id)
        impact = DictData.objects.get(id=impact_id)
    except DictData.DoesNotExist:
        raise serializers.ValidationError(_("影响范围/紧急程度不存在"))
    else:
        return urgency, impact


def priority_matrix_batch_update_validate(
    service_type, impact_data, urgency_data, priority_matrix
):
    """批量更新优先级矩阵参数校验"""

    for s in service_type:
        service_type_validator(s)

    if impact_data:
        matrix_data_validator(impact_data, PY_IMPACT)

    if urgency_data:
        matrix_data_validator(urgency_data, PX_URGENCY)

    if priority_matrix:
        priority_matrix_validator(priority_matrix)

    priority_validate(impact_data, urgency_data, priority_matrix)


def matrix_data_validator(matrix_data, matrix_type):
    """影响范围和紧急程度数据校验"""
    matrix_type_msg = ""
    if matrix_type == PX_URGENCY:
        matrix_type_msg = "紧急程度"
    if matrix_type == PY_IMPACT:
        matrix_type_msg = "影响范围"
    for data in matrix_data:
        if data.get("id") is None:
            raise serializers.ValidationError(_("参数错误，%s数据缺少参数id") % matrix_type_msg)
        if data.get("is_enabled") is None:
            raise serializers.ValidationError(
                _("参数错误，%s数据缺少参数is_enabled") % matrix_type_msg
            )
        if data.get("name") is None:
            raise serializers.ValidationError(_("参数错误，%s数据缺少参数name") % matrix_type_msg)
        if data.get("key") is None:
            raise serializers.ValidationError(_("参数错误，%s数据缺少参数key") % matrix_type_msg)


def priority_matrix_validator(priority_matrix):
    """优先级数据校验"""
    for priority in priority_matrix:
        if priority.get("id") is None:
            raise ParamError(_("参数错误，优先级数据缺少参数id"))
        if priority.get("priority") is None:
            raise ParamError(_("参数错误，优先级数据缺少参数priority"))
        if not PriorityMatrix.objects.filter(id=priority.get("id")).exists():
            raise ParamError(_("参数错误，不存在id为[%s]的优先级对象") % priority.get("id"))


def priority_validate(impact_data, urgency_data, priority_matrix):
    """校验影响范围和紧急程度交叉处的priority值是否填写了"""

    # {impact.key: impact.is_enabled, .....}
    impact_dict = {
        impact.get("key"): impact.get("is_enabled") for impact in impact_data
    }
    # {urgency.key: urgency.is_enabled, .....}
    urgency_dict = {
        urgency.get("key"): urgency.get("is_enabled") for urgency in urgency_data
    }
    priority_set = SysDict.get_data_by_key(PRIORITY, "sets")

    for priority in priority_matrix:
        impact_is_enabled = impact_dict.get(priority.get("impact"))
        urgency_is_enabled = urgency_dict.get(priority.get("urgency"))

        if impact_is_enabled and urgency_is_enabled:
            if priority.get("priority") not in priority_set:
                raise ParamError(_("参数错误，优先级选项不能为空且必须合法"))


name_validator = RegexValidator(
    re.compile("^[*a-zA-Z0-9_()（） \u4e00-\u9fa5]+$"),
    message=_("请输入合法名称：中英文、中英文括号、数字、下划线、空格及星号"),
    code="invalid",
)


def schedule_can_destroy(instance):
    """服务模式可删除校验"""
    if instance.is_builtin:
        raise ValidationError(_("内置的服务模式不能删除"))

    if instance.policies.all():
        raise ValidationError(_("该服务模式已绑定服务协议，请解绑后再删除"))


def sla_can_destroy(instance):
    """服务协议可删除校验"""
    if instance.is_builtin:
        raise ValidationError(_("内置的服务协议不能删除"))

    if ServiceSla.objects.filter(sla_id=instance.id).exists():
        raise ValidationError(_("该服务协议已绑定服务，请解绑后再删除"))


class ScheduleValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.name_validate(value)
        self.holidays_workdays_validate(value)
        self.day_validate(value)

    def name_validate(self, value):
        """服务名称校验"""
        schedule_obj = Schedule.objects
        project_key = value.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        if self.instance:
            # 如果是更新，内置的名称不能更新
            if self.instance.is_builtin and value.get("name") != self.instance.name:
                raise ParamError(_("内置服务模式：[%s] 的名称不能修改") % self.instance.name)

            schedule_obj = schedule_obj.exclude(id=self.instance.id)
        if schedule_obj.filter(
            name=value.get("name"), project_key=project_key
        ).exists():
            raise ParamError(_("服务模式名称：[%s] 已存在") % value.get("name"))

    @staticmethod
    def holidays_workdays_validate(value):
        """假期和工作日校验"""

        def date_compare(dates, day_type_msg):
            """日期比较"""
            # 这里用了两层循环，相互对比时间区间是否重叠，应该有好一点的写法
            for idx, day in enumerate(dates):
                other_days = dates[:idx] + dates[idx + 1 :]
                for other_day in other_days:
                    if max(day.get("start_date"), other_day.get("start_date")) < min(
                        day.get("end_date"), other_day.get("end_date")
                    ):
                        raise ParamError(_("{}时间段设置有冲突，请检查").format(day_type_msg))

        holidays = value.get("holidays")
        workdays = value.get("workdays")
        # 假期和假期之间，特定工作日之间不能有冲突
        if holidays:
            date_compare(holidays, "节假日")
        if workdays:
            date_compare(holidays, "特殊工作日")

    @staticmethod
    def day_validate(value):
        """星期校验"""
        days = value.get("days")
        if days:
            days_of_week = ",".join([day.get("day_of_week") for day in days]).split(",")
            # 星期唯一性校验
            counter_res = Counter(days_of_week)
            for k, v in list(counter_res.items()):
                if v > 1:
                    raise ParamError(
                        _("请勿重复定义{}的工作时间").format(WEEKDAY_CHOICES[int(k)][1])
                    )


class DayValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.all_day_validate(value)

    def all_day_validate(self, value):
        """根据日期类型做不同的校验"""
        type_of_day = value.get("type_of_day")
        try:
            getattr(self, "{}_validate".format(type_of_day.lower()))(value)
        except AttributeError:
            raise ParamError(_("日期类型错误：[{}]").format(type_of_day))

    def normal_validate(self, day):
        """普通工作时间校验"""
        self.day_number_validate(day)
        self.day_durations_validate(day)

    @staticmethod
    def holiday_validate(holiday):
        """假期校验"""
        if not holiday.get("name"):
            raise serializers.ValidationError(_("请输入节假日名称"))
        if holiday.get("start_date") > holiday.get("end_date"):
            raise ParamError(_("节假日期：[%s]的时间范围设置错误") % holiday.get("name"))

    def workday_validate(self, workday):
        """特定工作日校验"""
        if workday.get("start_date") > workday.get("end_date"):
            raise ParamError(_("加班时间的范围设置错误，开始时间不能大于结束时间"))
        self.day_durations_validate(workday)

    @staticmethod
    def day_number_validate(day):
        """星期数字有效性校验"""
        day_set = set(day.get("day_of_week").split(","))
        if len(day_set & set(map(str, list(range(7))))) < len(day_set):
            raise ParamError(_("请输入正确的星期数字(0-6)"))

    def day_durations_validate(self, day):
        """工作时间段的名字校验"""
        durations = day.get("duration", [])
        if not durations:
            raise ParamError(_("参数缺失：[duration]"))
        name_list = [duration.get("name") for duration in durations]
        if len(set(name_list)) < len(name_list):
            raise ParamError(_("工作时间段的命名不能重复，请检查"))
        self.durations_unique_validate(durations)

    @staticmethod
    def durations_unique_validate(durations):
        """工作日的工作时间段重合校验"""
        for idx, duration in enumerate(durations):
            other_durations = durations[:idx] + durations[idx + 1 :]
            for other_duration in other_durations:
                if max(
                    duration.get("start_time"), other_duration.get("start_time")
                ) < min(duration.get("end_time"), other_duration.get("end_time")):
                    raise ParamError(_("工作日的工作时间段重合，请检查"))


class DurationValidator(object):
    """时间范围验证器"""

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.duration_validate(value)

    @staticmethod
    def duration_validate(value):
        if value.get("start_time") >= value.get("end_time"):
            raise ParamError(_("时间范围错误，开始时间不能大于或等于结束时间"))


class SlaValidator(object):
    """服务协议验证器"""

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.name_validate(value)

    def name_validate(self, value):
        """SLA名称校验"""
        sla_obj = Sla.objects
        project_key = value.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        if self.instance:
            # 如果是更新，内置的名称不能更新
            if self.instance.is_builtin and value.get("name") != self.instance.name:
                raise ParamError(_("内置服务协议：[%s] 的名称不能修改" % self.instance.name))

            sla_obj = sla_obj.exclude(id=self.instance.id)
        if sla_obj.filter(name=value.get("name"), project_key=project_key).exists():
            raise ParamError(_("服务协议名称：[%s] 已存在") % value.get("name"))


class SlaTimerRuleValidator(object):
    """
    sla到达规则验证器
    """

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.condition_validate(value)

    @staticmethod
    def condition_validate(value):
        condition = value.get("condition")
        if condition.get("type") is None:
            raise serializers.ValidationError(_("参数错误，计时规则条件表达式缺少type"))
        expressions = condition.get("expressions", [])
        if expressions:
            for expression in expressions:
                if expression.get("operator") is None:
                    raise serializers.ValidationError(_("参数错误，计时规则条件表达式缺少operator"))
                if expression.get("name") is None:
                    raise serializers.ValidationError(_("参数错误，计时规则条件表达式缺少name"))
                if expression.get("value") is None:
                    raise serializers.ValidationError(_("参数错误，计时规则条件表达式缺少value"))
