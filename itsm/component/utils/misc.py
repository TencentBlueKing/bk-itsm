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
import json
import os

from django.conf import settings
from dateutil.relativedelta import relativedelta

from common.log import logger
from itsm.component.constants import JSON_HANDLE_FIELDS
from itsm.component.utils.basic import walk
from itsm.component.utils.client_backend_query import get_bk_users


class JsonEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime(self.TIME_FORMAT)
        if isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)

        return super(JsonEncoder, self).default(o)


def transform_single_username(username, user_dict=None):
    """
    -> '' -> ''
    -> 'aaa'->'aaa(张三)'
    name_type=chname
    -> 'aaa'->'张三'
    单用户的用户名转换
    """

    if not username:
        return ""

    if not user_dict:
        user_dict = get_bk_users(format="dict", users=[username])

    return (
        user_dict.get(username) if user_dict.get(username) else "{}()".format(username)
    )


def transform_username(users, user_dict=None):
    """
    -> '' -> ''
    -> 'aaa,bbb,ccc'->'aaa(张三),bbb(李四),ccc(ccc)'
    -> ['aaa','bbb','ccc']->'aaa(张三),bbb(李四),ccc(ccc)'
    英文名字字符串转中英文名字字符串, 支持逗号分隔字符串和列表，返回逗号分隔字符串
    """

    # 空字符串直接返回
    if not users:
        return ""

    if isinstance(users, str):
        users = [user for user in users.split(",") if user]

    if not user_dict:
        user_dict = get_bk_users(format="dict", users=users)

    ret_data = []
    for user in users:
        if user_dict.get(user):
            ret_data.append(user_dict.get(user))
        else:
            ret_data.append("%s" % user)

    return ",".join(ret_data)


def get_days(begin, end):
    """根据日期间隔返回日期列表"""
    days = []
    while begin < end:
        days.append(begin.date())
        begin = begin + datetime.timedelta(days=1)
    days.append(end.date())
    return days


def get_month_list(begin, end):
    """根据日期返回列表"""
    begin_year, begin_month = begin.year, begin.month
    end_year, end_month = end.year, end.month
    months = (int(end_year) - int(begin_year)) * 12 + (
        int(end_month) - int(begin_month)
    )
    begin_year_month = datetime.datetime.strptime(begin.strftime("%Y-%m"), "%Y-%m")
    return [
        (begin_year_month + relativedelta(months=index)).strftime("%Y-%m")
        for index in range(months)
    ]


def get_choice_route(choice, item_id):
    if not choice:
        return []

    choice_dict = {
        str(item["id"]): item.get("route", [])
        + [{"id": item["id"], "name": item["name"]}]
        for c in choice
        for item in walk(c)
    }

    return choice_dict.get(item_id, [])


def get_field_value(field):
    """获取字段的值"""
    import ast

    try:
        if field.type in JSON_HANDLE_FIELDS:
            return json.loads(field._value)
    except Exception as e:
        logger.warning(
            "convert field value exception: {0}; value: {1}".format(e, field._value)
        )
        try:
            return ast.literal_eval(field._value)
        except Exception:
            pass

    return field._value


def set_field_value(field, v):
    try:
        if field.type in JSON_HANDLE_FIELDS:
            field._value = json.dumps(v)
        else:
            field._value = v
    except Exception as e:
        logger.warning(
            "convert field value exception: {0}; value: {1}".format(e, field._value)
        )


def get_field_display_value(field):
    """获取字段的显示值"""

    if not field._value:
        return ""

    # 兼容旧数据
    if field.type == "CASCADE" and settings.IS_BIZ_GROUP:
        for choice in field.choice:
            for item in choice["items"]:
                if str(item["key"]) == field._value:
                    return "{}->{}".format(choice["name"], item["name"])

    if field.type in ["SELECT", "RADIO"]:
        return {str(choice["key"]): choice["name"] for choice in field.choice}.get(
            field._value, field._value
        )

    if field.type in ["MULTISELECT", "CHECKBOX", "MEMBERS"]:
        choice = {str(choice["key"]): str(choice["name"]) for choice in field.choice}
        return ",".join([choice.get(key, key) for key in field._value.split(",")])

    if field.type == "TREESELECT":
        route = get_choice_route(field.choice, field._value)
        return "->".join([item["name"] for item in route]) or field._value

    if field.type == "INPUTSELECT":
        choice = {str(choice["key"]): str(choice["name"]) for choice in field.choice}
        return choice.get(field._value)

    # if field.type in JSON_HANDLE_FIELDS:
    #     return field.value

    return field.value


def get_dept_route(depts, dept_id):
    """
    根据部门id获取其父部门
    :return: 部门id列表
    """
    dept_ids = []
    for dept in depts:
        if dept["id"] == dept_id:
            return [dept["id"] for dept in dept["route"]]
        if dept.get("children"):
            dept_ids.extend(get_dept_route(dept["children"], dept_id))
    dept_ids.append(dept_id)
    return dept_ids


def find_sub_string(s, splitter):
    """
    找到子字符串
    """
    if s.rfind(splitter) > -1:
        return s[0 : s.rfind(splitter)]
    return s


def find_json_file(path):
    """查找目录中以json文件"""
    file_path = []
    for p in os.listdir(path):
        if p.endswith(".json"):
            file_path.append(os.path.join(path, p))
            continue
        if os.path.isdir(os.path.join(path, p)):
            file_path.extend(find_json_file(os.path.join(path, p)))
    return file_path
