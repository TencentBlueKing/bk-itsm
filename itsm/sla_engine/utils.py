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

import datetime
from functools import cmp_to_key

from common.log import logger
from dateutil import rrule
from itsm.sla.models import Sla

EMPTY_DELTA = 0


def seconds_format(seconds):
    """秒转换为可读时间"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h == 0:
        return "%02d:%02d" % (m, s)

    return "%d:%02d:%02d" % (h, m, s)


def action_time_delta(start_time, end_time, sla_id, priority):
    """计算耗时
    :param start_time: 开始计时时间
    :param end_time: 结束计时时间
    :param sla_id: sla协议ID
    :param priority: 优先级key
    :return seconds: sla耗时(s)
    """
    time_delta = TimeDelta(start_time, end_time)
    sla_time = SlaTime(sla_id, priority)
    seconds = sla_time.sla_time(time_delta)
    return seconds


def action_time(seconds, sla_id, priority, start_time=None):
    """计算动作触发时间
    :param seconds: sla时长(s)
    :param sla_id: sla协议ID
    :param priority: 优先级key
    :param start_time: 开始计时时间
    :return deadline: sla截止时间
    """
    # 开始计时时间的缺省参数值为当前时间
    start_time = datetime.datetime.now() if start_time is None else start_time

    sla_time = SlaTime(sla_id, priority)
    deadline = sla_time.sla_deadline(start_time, seconds)
    return deadline


class TimeDelta(object):
    """时间段"""

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return "<{cls} {start_time} - {end_time}>".format(
            cls=type(self).__name__, start_time=self.start_time, end_time=self.end_time
        )

    def seconds(self):
        """间隔时长(s)"""
        return int((self.end_time - self.start_time).total_seconds())

    def intersection(self, time_delta):
        """交集"""
        if self.is_intersect(time_delta):
            return TimeDelta(max(self.start_time, time_delta.start_time), min(self.end_time, time_delta.end_time))

    def is_intersect(self, time_delta):
        """是否交叉"""
        return max(self.start_time, time_delta.start_time) < min(self.end_time, time_delta.end_time)

    def difference(self, time_delta):
        """差集"""
        if self.is_intersect(time_delta):

            if self.start_time < time_delta.start_time:
                if self.end_time < time_delta.end_time:
                    # s1 - e1
                    #    s2 - e2
                    return [TimeDelta(self.start_time, time_delta.start_time)]
                else:
                    # s1  -  e1
                    #  s2 - e2
                    return [
                        TimeDelta(self.start_time, time_delta.start_time),
                        TimeDelta(time_delta.end_time, self.end_time),
                    ]
            else:
                if self.end_time > time_delta.end_time:
                    #    s1 - e1
                    # s2 - e2
                    return [TimeDelta(time_delta.end_time, self.end_time)]
                else:
                    #  s1 - e1
                    # s2  -  e2
                    return []
        else:
            return [self]

    def union(self, time_delta):
        """并集"""
        if self.is_intersect(time_delta):
            return [TimeDelta(min(self.start_time, time_delta.start_time), max(self.end_time, time_delta.end_time))]
        else:
            return [self, time_delta]

    def date_list(self):
        """跨度日期"""
        return [
            x.date() for x in list(rrule.rrule(rrule.DAILY, dtstart=self.start_time.date(), until=self.end_time.date()))
        ]

    def position(self, time):
        """指定时间在时间段的位置, 左侧为-1, 内部为0, 右侧为1"""
        if time < self.start_time:
            return -1
        if self.start_time <= time <= self.end_time:
            return 0
        else:
            return 1


class MultiTimeDelta(object):
    """多个时间段"""

    def __init__(self, *time_deltas):
        self.time_deltas = time_deltas

    def __repr__(self):
        return "<{cls} ({count})个TimeDelta>".format(cls=type(self).__name__, count=len(self.time_deltas))

    def diff_manytoone(self, time_delta):
        """多个时间段对单个时间段的差集"""
        source_td_diffs = []
        for source_td in self.time_deltas:
            source_td_diffs.extend(source_td.difference(time_delta))

        return source_td_diffs

    def difference(self, multi_time_delta):
        """多个时间段之间的差集"""
        for time_delta in multi_time_delta.time_deltas:
            self.time_deltas = self.diff_manytoone(time_delta)

        return self.time_deltas

    def intersect_manytoone(self, time_delta):
        """多个时间段和单个时间段的交集"""
        td_intersects = []
        for source_td in self.time_deltas:
            td_intersect = source_td.intersection(time_delta)
            if td_intersect:
                td_intersects.append(td_intersect)

        return td_intersects

    def intersection(self, multi_time_delta):
        """多个时间段之间的交集"""
        for time_delta in multi_time_delta.time_deltas:
            self.time_deltas = self.intersect_manytoone(time_delta)

        return self.time_deltas

    def closest_td_time(self, time, is_forward):
        """
        正向查找: 获取指定时间最近的下一个时间段的开始时间
        反向查找: 获取指定时间最近的上一个时间段的结束时间
        """
        for time_delta in self.sort(not is_forward).time_deltas:
            if time_delta.position(time) == 0:
                return time

            # 正向查找: 指定时间在当前时间段的左侧
            if is_forward and time_delta.position(time) == -1:
                return time_delta.start_time

            # 反向查找: 指定时间在当前时间段的右侧
            if not is_forward and time_delta.position(time) == 1:
                return time_delta.end_time

    def sort(self, reverse=False):
        """多个时间段进行排序
        """

        def _sort(td_a, td_b):
            if td_a.start_time > td_b.start_time:
                return 1
            if td_a.start_time < td_b.start_time:
                return -1
            if td_a.end_time > td_b.end_time:
                return 1
            if td_a.end_time < td_b.end_time:
                return -1
            return 1

        time_deltas = list(self.time_deltas)
        time_deltas.sort(key=cmp_to_key(_sort), reverse=reverse)
        self.time_deltas = tuple(time_deltas)
        return self

    def union(self, multi_time_delta):
        """多个时间段之前的并集"""
        # 1. 先排序 2. 依次循环 将最新的时间段和最后一个时间段取并集
        union_multi_td = MultiTimeDelta(*(self.time_deltas + multi_time_delta.time_deltas))
        union_multi_td.sort()

        union_time_deltas = []
        for time_delta in union_multi_td.time_deltas:
            if not union_time_deltas:
                union_time_deltas.append(time_delta)
                continue

            ltime_delta = union_time_deltas[-1]
            if ltime_delta.start_time <= time_delta.start_time <= ltime_delta.end_time < time_delta.end_time:
                union_time_deltas[-1].end_time = time_delta.end_time
            if time_delta.start_time > ltime_delta.end_time:
                union_time_deltas.append(time_delta)

        return union_time_deltas


class SlaEngine(object):
    """sla协议引擎"""

    def __init__(self, sla_id):
        """
        :param sla_id: sla协议ID
        """
        self.sla = Sla.objects.get(id=sla_id)


class SlaTime(SlaEngine):
    """sla耗时"""

    def __init__(self, sla_id, priority):
        """
        :param sla_id: sla协议ID
        :param priority: 优先级key
        """
        super(SlaTime, self).__init__(sla_id)
        self.priority = priority
        self._get_policy()

    def _get_policy(self):
        self.policy = self.sla.get_priority_policy(self.priority)
        # 判断是否配置sla服务策略
        if self.policy:
            self.schedule_days = self.policy.schedule_days()
        else:
            self.schedule_days = None

    def sla_time(self, time_delta):
        """
        :param time_delta: 时间段实例
        :return: sla计算耗时
        """
        seconds = EMPTY_DELTA
        if self.policy:
            sla_time_deltas = []

            for date in time_delta.date_list():
                sla_time_deltas.extend(self.date_time_deltas(date))

            intersect_tds = []
            for sla_td in sla_time_deltas:
                intersect_td = time_delta.intersection(sla_td)

                if intersect_td:
                    intersect_tds.append(intersect_td)
                    seconds += intersect_td.seconds()

            logger.debug(
                "SLA协议: {sla_name}({sla_id}), 计算时段: {time_delta}, 实际服务时段: {intersect_tds}".format(
                    sla_name=self.sla.name, sla_id=self.sla.id, time_delta=time_delta, intersect_tds=intersect_tds
                )
            )

        return seconds

    def sla_deadline(self, start_time, seconds):
        """
        sla截止时间
        1. 以"自然时长"推进或者回退, 计算: 时长差值 = sla服务时长 - sla计算时长
        2. seconds >= 0: "下一个最近sla开始时间" + "时长差值", 时长差值以"自然时长"推进, 直到时长差值为0, 最后的时间点为sla截止时间
           seconds < 0: "上一个最近sla结束时间" + "时长差值", 时长差值以"自然时长"回退, 直到时长差值为0, 最后的时间点为sla截止时间
        :param start_time: 开始计时时间
        :param seconds: sla服务时长(s)
        """
        is_forward = True if seconds > 0 else False
        sla_seconds = EMPTY_DELTA
        difference_seconds = abs(seconds) - sla_seconds
        return self._update_deadline(start_time, difference_seconds, is_forward)

    def _update_deadline(self, deadline, difference_seconds, is_forward):
        """
        :param deadline: 最新sla截止时间
        :param difference_seconds: 时长差值
        :param is_forward: 是否为正向
        """
        if difference_seconds > 0:
            start_time = deadline
            start_date = start_time.date()

            # 从当天开始向前/后依次循环, 直到获取下一个最近sla间隔时长
            closest_td_time = None
            while closest_td_time is None:
                date_time_deltas = self.date_time_deltas(start_date)

                if is_forward:
                    # 往前推进一天
                    start_date += datetime.timedelta(days=1)
                else:
                    # 往后回退一天
                    start_date -= datetime.timedelta(days=1)

                # 当前日期存在sla时间段
                if date_time_deltas:
                    multi_td = MultiTimeDelta(*date_time_deltas)
                    closest_td_time = multi_td.closest_td_time(start_time, is_forward)

            if is_forward:
                # 往前推进时长差值
                deadline = closest_td_time + datetime.timedelta(seconds=difference_seconds)
                sla_seconds = self.sla_time(TimeDelta(start_time, deadline))
            else:
                # 往后回退时长差值
                deadline = closest_td_time - datetime.timedelta(seconds=difference_seconds)
                sla_seconds = self.sla_time(TimeDelta(deadline, start_time))

            difference_seconds -= sla_seconds
            return self._update_deadline(deadline, difference_seconds, is_forward)
        else:
            return deadline

    @staticmethod
    def full_datetime(date, time):
        """获取完整的日期时间"""
        return datetime.datetime(
            year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second
        )

    def _time_delta(self, date, date_type):
        """获取包括指定日期的假期或者加班日中配置的时间段
        """
        time_deltas = []
        for day in self.schedule_days[date_type]:
            if day["start_date"] <= date <= day["end_date"]:
                for duration in day["duration"]:
                    td = TimeDelta(
                        self.full_datetime(date, duration["start_time"]), self.full_datetime(date, duration["end_time"])
                    )
                    time_deltas.append(td)
                break
        return time_deltas

    def date_time_deltas(self, date):
        """该日期对应的sla服务日的时间段"""

        # 工作日时段
        d_time_deltas = []
        for day in self.schedule_days["days"]:
            if str(date.weekday()) in day["day_of_week"]:
                for duration in day["duration"]:
                    days_td = TimeDelta(
                        self.full_datetime(date, duration["start_time"]), self.full_datetime(date, duration["end_time"])
                    )
                    d_time_deltas.append(days_td)
                break

        # 工作日时段和假期时段取差集
        h_time_deltas = self._time_delta(date, "holidays")

        if h_time_deltas:
            hd_time_deltas = MultiTimeDelta(*d_time_deltas).difference(MultiTimeDelta(*h_time_deltas))
        else:
            hd_time_deltas = d_time_deltas

        # 如果加班日包括该日期, 取并集
        w_time_deltas = self._time_delta(date, "workdays")

        if w_time_deltas:
            whd_time_deltas = MultiTimeDelta(*hd_time_deltas).union(MultiTimeDelta(*w_time_deltas))
        else:
            whd_time_deltas = hd_time_deltas

        return whd_time_deltas
