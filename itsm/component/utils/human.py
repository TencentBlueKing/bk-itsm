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

import humanize
from django.conf import settings


def get_time(the_time, i18n="zh_CN", format=""):
    """
    时间间隔大于一天则返回日期，小于则返回时间间隔
    """
    delta = datetime.datetime.now() - the_time
    if delta.days > 1:
        if format:
            return the_time.strftime(format)
        return the_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        try:
            humanize.i18n.activate(i18n, path=settings.LOCALE_PATHS[0])
            return humanize.naturaltime(delta)
        except IOError:
            return humanize.naturaltime(delta)
        finally:
            humanize.deactivate()


def get_time_string(the_time, i18n="zh_CN"):
    """
    时间间隔大于一天则返回按格式格式化的日期，小于则返回时间间隔
    """
    delta = datetime.datetime.now() - the_time
    if delta.days > 1:
        return the_time
    else:
        try:
            humanize.i18n.activate(i18n, path=settings.LOCALE_PATHS[0])
            return humanize.naturaltime(delta)
        except IOError:
            return humanize.naturaltime(delta)
        finally:
            humanize.deactivate()


def time_since(the_time, i18n="zh_CN"):
    """
    时间间隔友好显示
    """
    try:
        humanize.i18n.activate(i18n, path=settings.LOCALE_PATHS[0])
        return humanize.naturaldelta(datetime.datetime.now() - the_time)
    except IOError:
        return humanize.naturaldate(datetime.datetime.now() - the_time)
    finally:
        humanize.deactivate()


def natural_day(the_day, i18n="zh_CN"):
    """
    日期友好显示
    """
    try:
        humanize.i18n.activate(i18n, path=settings.LOCALE_PATHS[0])
        return humanize.naturalday(the_day, format="%Y-%m-%d")
    except IOError:
        return humanize.naturalday(the_day, format="%Y-%m-%d")
    finally:
        humanize.deactivate()


def natural_size(value, i18n="zh_CN", format_size="%.1f"):
    """
    文件大小友好显示
    """
    try:
        humanize.i18n.activate(i18n, path=settings.LOCALE_PATHS[0])
        return humanize.naturalsize(value, format=format_size)
    except IOError:
        return humanize.naturalsize(value)
    except Exception:
        return value
    finally:
        humanize.deactivate()
