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
from rest_framework.fields import empty

from itsm.component.constants import DAY_TYPE_CHOICES, LEN_MIDDLE, LEN_SHORT
from itsm.sla.models import Day, Duration, Schedule
from itsm.sla.validators import DayValidator, DurationValidator, ScheduleValidator, name_validator

from .basic import ModelSerializer
from ...component.drf.serializers import AuthModelSerializer


class DurationSerializer(ModelSerializer):
    name = serializers.CharField(required=True, validators=[name_validator])
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)

    class Meta:
        model = Duration
        fields = ('id', 'name', 'start_time', 'end_time')

    def run_validation(self, data=empty):
        self.validators = [DurationValidator(self.instance)]
        return super(DurationSerializer, self).run_validation(data)


class DaySerializer(ModelSerializer):
    """服务优先级序列化"""

    id = serializers.CharField(required=False, max_length=LEN_SHORT, allow_null=True)

    day_of_week = serializers.CharField(required=False, max_length=LEN_SHORT, allow_null=True)

    start_date = serializers.DateField(required=False, allow_null=True)

    end_date = serializers.DateField(required=False, allow_null=True)

    type_of_day = serializers.CharField(
        required=True,
        error_messages={'blank': _("日期类型不能为空")},
        max_length=LEN_SHORT,
        # choices=DAY_TYPE_CHOICES
    )

    name = serializers.CharField(
        required=False,
        allow_blank=True,
        # validators=[name_validator],
        max_length=LEN_MIDDLE,
    )

    duration = DurationSerializer(many=True)

    class Meta:
        model = Day
        fields = ('id', 'name', 'type_of_day', 'day_of_week', 'start_date', 'end_date', 'duration')

    def create(self, validated_data):
        duration = [
            Duration.objects.create(**duration_params) for duration_params in
            validated_data.pop("duration", [])
        ]
        day = super(DaySerializer, self).create(validated_data)
        if duration:
            day.duration.set(duration)
            day.save()
        return day

    def update(self, instance, validated_data):
        duration = validated_data.pop("duration", [])
        instance = super(DaySerializer, self).update(instance, validated_data)
        if not duration:
            return instance

        duration = [Duration.objects.create(**duration_params) for duration_params in duration]
        instance.duration.set(duration)
        instance.save()
        return instance

    def run_validation(self, data=empty):
        self.validators = [DayValidator(self.instance)]
        return super(DaySerializer, self).run_validation(data)


class ScheduleSerializer(AuthModelSerializer, ModelSerializer):
    """服务工作模式序列化"""

    name = serializers.CharField(
        required=True,
        error_messages={'blank': _("服务模式名称不能为空")},
        # validators=[name_validator],
        max_length=LEN_MIDDLE,
    )
    is_enabled = serializers.BooleanField(required=False, default=True)
    days = DaySerializer(many=True)
    workdays = DaySerializer(required=False, many=True, allow_null=True)
    holidays = DaySerializer(required=False, many=True, allow_null=True)
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = Schedule
        related_fields = ("days", "workdays", "holidays")
        fields = (
        'id', 'name', 'is_enabled', 'is_builtin', 'days', 'workdays', 'holidays', 'project_key')

    def create(self, validated_data):
        ScheduleValidator(self.instance)(validated_data)
        days = validated_data.pop('days', [])
        workdays = validated_data.pop('workdays', [])
        holidays = validated_data.pop('holidays', [])

        schedule = super(ScheduleSerializer, self).create(validated_data)

        # 创建对应的工作日和假期
        self.set_days(days, schedule)

        # 加班日和假期实际上都属于单个添加，当前这个为全局接口
        self.set_holidays(holidays, schedule)
        self.set_workdays(workdays, schedule)
        schedule.save()

        return schedule

    def update(self, instance, validated_data):

        rel_fields = {key: validated_data.pop(key, []) for key in self.Meta.related_fields}

        instance = super(ScheduleSerializer, self).update(instance, validated_data)

        instance = self.update_many_to_many_relation(instance, rel_fields)
        return instance

    def set_days(self, days, schedule):
        if not days:
            return
        days = [self.fields.fields['days'].child.create(day_params) for day_params in days]
        schedule.days.set(days) 

    def set_workdays(self, workdays, schedule):
        if not workdays:
            return
        workdays = [self.fields.fields['workdays'].child.create(day_params) for day_params in
                    workdays]

        schedule.workdays.set(workdays)

    def set_holidays(self, holidays, schedule):
        if not holidays:
            return
        holidays = [self.fields.fields['holidays'].child.create(day_params) for day_params in
                    holidays]
        schedule.holidays.set(holidays)

    def run_validation(self, data=empty):
        return super(ScheduleSerializer, self).run_validation(data)

    def to_representation(self, instance):
        data = super(ScheduleSerializer, self).to_representation(instance)
        return self.update_auth_actions(instance, data)


class ScheduleDayRelationSerializer(serializers.Serializer):
    """
    添加单条工作日或者单个假期
    """

    day_of_type = serializers.ChoiceField(required=True, choices=DAY_TYPE_CHOICES)
    days = DaySerializer(many=True)

    def to_internal_value(self, data):
        days = data.pop("days", [])
        data['days'] = [self.fields.fields['days'].child.to_internal_value(day) for day in days]
        return data

    def to_representation(self, instance):
        return ScheduleSerializer(instance).to_representation(instance)

    def update(self, instance, validated_data):
        days = validated_data.pop("days", [])
        try:
            add_method = getattr(self, "add_{}s".format(validated_data['type_of_day'].lower()))
        except AttributeError:
            raise serializers.ValidationError(_("不存在的日期类型"))
        add_method(days, instance)
        return instance

    def add_workdays(self, workdays, schedule):
        for day_params in workdays:
            schedule.workdays.add(self.fields.fields['days'].child.create(day_params))

    def add_holidays(self, holidays, schedule):
        for day_params in holidays:
            schedule.holidays.add(self.fields.fields['days'].child.create(day_params))

    def create(self, validated_data):
        pass
