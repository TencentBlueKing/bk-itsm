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

from datetime import datetime, timedelta


units = ("year", "day", "hour", "minute", "second", "millisecond", "microsecond")


def get_delta_from_subject(subject):
    """Convert the subject to a timedelta and return it."""
    if isinstance(subject, timedelta):
        return subject

    if isinstance(subject, datetime):
        dt = subject
    else:
        # if it's not a datetime, assume it's a unix timestamp
        try:
            subject = float(subject)
        except ValueError:
            # some unknown type that couldn't be converted to a float
            raise TypeError("Unsupported subject type")

        dt = datetime.fromtimestamp(subject)

    # return a timedelta from the datetime, using its timezone (if it has one)
    return datetime.now(tz=dt.tzinfo) - dt


def delta2dict(delta):
    """Accepts a delta, returns a dictionary of units"""
    delta = abs(delta)
    return {
        "year": int(delta.days / 365),
        "day": int(delta.days % 365),
        "hour": int(delta.seconds / 3600),
        "minute": int(delta.seconds / 60) % 60,
        "second": delta.seconds % 60,
        "millisecond": delta.microseconds / 1000,
        "microsecond": delta.microseconds % 1000,
    }


def human(subject, precision=2, past_tense="{} ago", future_tense="in {}", abbreviate=False):
    """
    Accept a subject, return a human readable timedelta string.

    :param subject: a datetime, timedelta, or timestamp (integer / float) object
    :param precision: the desired amount of unit precision (default: 2)
    :param past_tense: the format string used for a past timedelta (default: '{} ago')
    :param future_tense: the format string used for a future timedelta (default: 'in {}')
    :param abbreviate: boolean to abbreviate units (default: False)

    :returns: Human readable timedelta string (Str)
    """
    delta = get_delta_from_subject(subject)
    the_tense = future_tense if delta < timedelta(0) else past_tense

    d = delta2dict(delta)

    hlist = []
    count = 0

    # start building up the output in the hlist.
    for unit in units:
        if count >= precision:
            break  # met precision
        if d[unit] == 0:
            continue  # skip 0's
        if abbreviate:
            if unit == "millisecond":
                abr = "ms"
            elif unit == "microsecond":
                abr = "um"
            else:
                abr = unit[0]
            hlist.append("{}{}".format(d[unit], abr))
        else:
            s = "" if d[unit] == 1 else "s"  # handle plurals
            hlist.append("{} {}{}".format(d[unit], unit, s))
        count += 1

    return the_tense.format(", ".join(hlist))
