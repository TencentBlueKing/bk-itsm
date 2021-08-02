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

from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    DAY_TYPE_CHOICES,
    LEN_LONG,
    LEN_SHORT,
    NORMAL_DAY,
)

from .basic import Model


class Duration(Model):
    """
    时间段
    """

    name = models.CharField(_("时间段名称"), max_length=LEN_LONG)
    # 记录工作时间段
    start_time = models.TimeField(_("开始时间"))
    end_time = models.TimeField(_("结束时间"))

    class Meta:
        app_label = 'sla'
        verbose_name = _("工作时间段")
        verbose_name_plural = _("工作时间段")

    def __unicode__(self):
        return "{}-{}".format(self.start_time, self.end_time)


class Day(Model):
    """工作日和节假日"""

    name = models.CharField(_("假期名称"), max_length=LEN_LONG)
    day_of_week = models.CharField(_("星期几"), max_length=LEN_SHORT, default=-1)
    type_of_day = models.CharField(_("日期类型"), max_length=LEN_SHORT, choices=DAY_TYPE_CHOICES, default=NORMAL_DAY)

    # 比如十一假期范围
    start_date = models.DateField(_("开始日期"), null=True)
    end_date = models.DateField(_("结束日期"), null=True)
    duration = models.ManyToManyField(to='Duration', help_text=_("工作时间段，没有配置的情况下，默认从0:00 -23:59"))

    class Meta:
        app_label = 'sla'
        verbose_name = _("工作日和节假日")
        verbose_name_plural = _("工作日和节假日")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type_of_day)


class Schedule(Model):
    """服务时间策略"""

    name = models.CharField(_("名称"), max_length=LEN_LONG)
    is_enabled = models.BooleanField("配置是否生效", help_text="是：启用当前工作日历配置， 否：默认采用7*24小时", default=True)
    days = models.ManyToManyField(help_text=_("常规日历"), to='Day', related_name='days')
    workdays = models.ManyToManyField(help_text=_("加班日"), to='Day', related_name='workdays', default=None)
    holidays = models.ManyToManyField(help_text=_("假期"), to='Day', related_name='holidays', default=None)
    is_builtin = models.BooleanField(_("是否内置"), default=False)
    project_key = models.CharField(_("项目key"), max_length=LEN_SHORT, null=False, default=0)

    auth_resource = {"resource_type": "sla_calendar", "resource_type_name": "SLA 服务模式"}
    resource_operations = ["sla_calendar_view", "sla_calendar_edit", "sla_calendar_delete"]

    need_auth_grant = True

    class Meta:
        app_label = 'sla'
        verbose_name = _("服务运营时间")
        verbose_name_plural = _("服务运营时间")
        ordering = ['-id']

    def __unicode__(self):
        return self.name

    @classmethod
    def init_schedule(cls, project_key="0"):
        """初始化默认的服务模式"""
        default_schedule_name = ['5*8', '7*24']
        default_day_of_week = [
            ','.join(map(str, [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY])),
            ','.join(map(str, [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY])),
        ]
        default_durations = [
            [
                {'name': _('上午'), 'start_time': '08:00:00', 'end_time': '12:00:00'},
                {'name': _('下午'), 'start_time': '14:00:00', 'end_time': '18:00:00'},
            ],
            [{'name': _('全天'), 'start_time': '00:00:00', 'end_time': '23:59:59'}],
        ]
        schedules = []

        for index, schedule_name in enumerate(default_schedule_name):
            schedule = cls.objects.filter(name=schedule_name, project_key=project_key).first()

            if schedule:
                schedules.append(schedule)
                continue
            day_of_week = default_day_of_week[index]
            durations_data = default_durations[index]
            durations = []

            for duration_data in durations_data:
                duration = Duration.objects.create(**duration_data)
                durations.append(duration)
            day = Day.objects.create(day_of_week=day_of_week, type_of_day='NORMAL')
            day.duration.add(*durations)
            schedule = cls.objects.create(name=schedule_name, is_builtin=True, project_key=project_key)
            schedule.days.add(day)
            schedules.append(schedule)

        return schedules
