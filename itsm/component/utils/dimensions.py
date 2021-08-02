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

from datetime import timedelta, datetime, date


def fill_time_dimension(begin, end, data, time_delta=None):
    if time_delta == "days":
        data_dict = {i["date_str"]: i["count"] for i in data}
        dates_range = [
            {"date": str(begin + timedelta(i)), "count": data_dict.get(str(begin + timedelta(i)), 0)}
            for i in range((end - begin).days + 1)
        ]
    elif time_delta == "weeks":
        dates_range = []
        data_dict = {
            str(datetime.strptime('{} {} 1'.format(*str(i["date_str"]).split('-')), '%G %V %u').date()): i["count"]
            for i in data
        }
        begin = begin - timedelta(days=begin.weekday())
        end = end - timedelta(days=begin.weekday()) + timedelta(days=7)
        while begin < end:
            dates_range.append({"date": str(begin), "count": data_dict.get(str(begin), 0)})
            begin += timedelta(days=7)

    elif time_delta == "months":
        dates_range = []
        data_dict = {
            str(
                date(year=int(str(i["date_str"]).split("-")[0]), month=int(str(i["date_str"]).split("-")[1]), day=1)
            ): i["count"]
            for i in data
        }
        begin = date(year=int(str(begin).split("-")[0]), month=int(str(begin).split("-")[1]), day=1)
        end = date(year=int(str(end).split("-")[0]), month=int(str(end).split("-")[1]) + 1, day=1)
        while begin < end:
            dates_range.append({"date": str(begin), "count": data_dict.get(str(begin), 0)})
            begin = date(year=begin.year + (begin.month == 12), month=begin.month == 12 or begin.month + 1, day=1)
    else:
        dates_range = []
        data_dict = {str(date(year=int(str(i["date_str"])), month=1, day=1)): i["count"] for i in data}
        begin = date(year=int(str(begin).split("-")[0]), month=1, day=1)
        end = date(year=int(str(end).split("-")[0]) + 1, month=1, day=1)
        while begin < end:
            dates_range.append({"date": str(begin), "count": data_dict.get(str(begin), 0)})
            begin = date(year=begin.year + 1, month=1, day=1)

    return dates_range
