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

import hashlib
import json
from math import ceil
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import CACHE_5MIN, CACHE_30MIN, PREFIX_KEY
from itsm.component.esb.esbclient import client_backend
from itsm.component.exceptions import ComponentCallError
from itsm.component.esb.backend_component import bk
from itsm.component.tasks import (
    update_user_cache,
    update_bk_business,
    update_user_departments,
)

adapter_api = settings.ADAPTER_API


def get_biz_choices():
    cache_key = "%sapp_list" % PREFIX_KEY
    app_list = cache.get(cache_key)
    if app_list is not None:
        return app_list

    apps = get_all_apps()
    app_list = [
        {"key": item["bk_biz_id"], "name": item["bk_biz_name"], "desc": _("请选择关联业务")}
        for item in apps
    ]

    cache.set(cache_key, app_list, CACHE_30MIN)
    return app_list


def get_group_app_list(apps, group_apps, group_other, biz_group_conf):
    """
    业务分组
    """
    for group_inst_id in list(group_apps.keys()):
        group_next = get_group_next_data(biz_group_conf["biz_obj_id"], group_inst_id)
        for item in group_next:
            if str(item["bk_inst_id"]) not in list(apps.keys()):
                continue
            app = apps.pop(str(item["bk_inst_id"]))
            group_apps[group_inst_id]["items"].append(
                {
                    "key": app["bk_biz_id"],
                    "name": app["bk_biz_name"],
                    "desc": _("请选择关联业务"),
                }
            )
    if apps:
        group_other["items"].extend(
            [
                {"key": a["bk_biz_id"], "name": a["bk_biz_name"], "desc": _("请选择关联业务")}
                for a in list(apps.values())
            ]
        )

    app_list = list(group_apps.values())
    app_list.append(group_other)
    return app_list


def get_group(biz_group_conf, group_enum):
    """
    定制化需求：业务分组
    :param biz_group_conf: 环境变量设置的业务分组配置字典
    :return:
    """

    # 再获取分组的模块信息
    params = {"bk_supplier_account": 0, "bk_obj_id": biz_group_conf["biz_obj_id"]}
    try:
        search_group_list = client_backend.cc.search_inst(params).get("info")
    except ComponentCallError as error:
        logger.warning("获取分组信息失败：%s" % str(error))
        search_group_list = []

    if group_enum:
        enum = get_attr_enum(
            bk_obj_id=biz_group_conf["biz_obj_id"], enum_bk_property_id=group_enum
        )
        group_apps = {
            str(item["bk_inst_id"]): {
                "name": "%s（%s）"
                % (item["bk_inst_name"], enum.get(item.get(group_enum), _("未接管"))),
                "key": item["bk_inst_id"],
                "desc": settings.BIZ_GROUP_DESC,
                "items": [],
            }
            for item in search_group_list
        }

    else:
        group_apps = {
            str(item["bk_inst_id"]): {
                "name": item["bk_inst_name"],
                "key": item["bk_inst_id"],
                "desc": settings.BIZ_GROUP_DESC,
                "items": [],
            }
            for item in search_group_list
        }

    group_other = {
        "name": _("其他"),
        "key": "other",
        "items": [],
        "desc": settings.BIZ_GROUP_DESC,
    }
    return group_apps, group_other


def get_attr_enum(bk_obj_id, enum_bk_property_id):
    """
    获取模型属性枚举类型
    :param bk_obj_id: 模型id
    :param enum_bk_property_id: 枚举属性的bk_property_id
    """
    enum = {}
    attrs = client_backend.cc.search_object_attribute(
        {"bk_obj_id": bk_obj_id, "bk_supplier_account": "0"}
    )
    for attr in attrs:
        if attr["bk_property_id"] == enum_bk_property_id:
            enum = {value["id"]: value["name"] for value in attr["option"]}
            break

    return enum


def get_biz_names():
    """
    获取业务的名称，返回字典
    """
    cache_key = "%sget_biz_names" % PREFIX_KEY
    biz_names = cache.get(cache_key)
    if biz_names is not None:
        return biz_names

    biz_list = get_biz_choices()
    biz_names = {str(biz["key"]): biz["name"] for biz in biz_list}

    cache.set(cache_key, biz_names, 60 * 60)
    return biz_names


def get_all_apps():
    """通过search_bussiness 获取APP列表"""

    params = {"bk_supplier_id": 0, "fields": [], "condition": {}}

    try:
        all_apps = client_backend.cc.search_business(params).get("info")
    except ComponentCallError as error:
        logger.warning("获取业务列表失败：%s" % str(error))
        all_apps = []
    return all_apps


def get_bk_users(format="list", name_type="bk_username", users=None):
    """
    抽出获取bk_users的逻辑，并添加10分钟缓存，不再支持全量查询
    """
    if not users:
        return [] if format == "list" else {}
    user_md5 = hashlib.md5(json.dumps(users).encode()).hexdigest()
    cache_key = "{}bk_users_{}_{}_{}".format(PREFIX_KEY, format, name_type, user_md5)
    bk_users = cache.get(cache_key)
    if not bk_users:
        bk_users = update_user_cache(cache_key, format, name_type, users)
    # else:
    #     update_user_cache.delay(cache_key, format, name_type, users)
    return bk_users


def get_bk_business(bk_biz_id, role_type):
    """
    抽离cc查询业务逻辑，并添加5分钟缓存
    """

    cache_key = "%sbk_business_%s_%s" % (PREFIX_KEY, bk_biz_id, "_".join(role_type))
    search_business_list = cache.get(cache_key)

    if not isinstance(search_business_list, list):
        search_business_list = update_bk_business(cache_key, bk_biz_id, role_type)
    else:
        update_bk_business.delay(cache_key, bk_biz_id, role_type)

    if not search_business_list:
        return ""

    bk_business = []
    print("----search_business_list is {}".format(search_business_list))
    print("----search_business_list type is {}".format(type(search_business_list)))
    for business in search_business_list:
        if not business:
            continue
        for _type in role_type:
            role_info = business.get(_type)
            if role_info:
                bk_business.append(role_info)

    return ",".join(bk_business)


def get_list_department_profiles(params, page_size=500):
    """
    分页查询部门的用户信息

    @params params: dict 参数信息
    @params page_size: int 每页拉取的数量
    @return result list
    """

    params["page_size"] = page_size
    res = client_backend.usermanage.list_department_profiles(params)
    count = res.get("count")

    # 获取第一页的结果
    result = res.get("results", [])
    # 算出来总页数
    page_number = ceil(count / page_size)

    # 从第二页开始拉取
    for page in range(2, page_number + 1):
        params["page"] = page
        res = client_backend.usermanage.list_department_profiles(params)
        result.extend(res.get("results", []))

    return result


def get_list_departments(params, page_size=500):
    """
    分页拉取部门信息

    @params params: dict 参数信息
    @params page_size: int 每页拉取的数量
    @return result list
    """

    params["page_size"] = page_size
    res = client_backend.usermanage.list_departments(params)
    count = res.get("count")

    # 获取第一页的结果
    result = res.get("results", [])
    # 算出来总页数
    page_number = ceil(count / page_size)

    # 从第二页开始拉取
    for page in range(2, page_number + 1):
        params["page"] = page
        res = client_backend.usermanage.list_departments(params)
        result.extend(res.get("results", []))

    return result


def get_department_users(department_id, recursive=False, detail=False):
    """获取部门用户列表，支持递归查询"""
    cache_key = "{}department|{}users|{}".format(PREFIX_KEY, department_id, recursive)
    users = cache.get(cache_key)

    if users is None:
        try:
            res = get_list_department_profiles(
                {
                    "id": department_id,
                    "recursive": recursive,
                    # 默认只返回id/username，detail为True则返回所有字段
                    "detail": detail,
                }
            )
            users = [item["username"] for item in res]
            cache.set(cache_key, users, CACHE_5MIN)
        except ComponentCallError as e:
            logger.error(
                "获取组织架构用户失败：department_id=%s, error=%s" % (department_id, str(e))
            )
            return []

    return users


def get_user_department_ids(username):
    """
    获取用户的组织架构ID，用于提升用户的组织架构提单速度
    """
    try:
        res = client_backend.usermanage.list_profile_departments(
            {"id": username, "with_family": True}
        )
        # 用户当前的组织架构id
        current_department_ids = [int(item["id"]) for item in res]
        department_ids = []
        for item in res:
            for family in item.get("family", []):
                department_ids.append(family["id"])

        department_ids.extend(current_department_ids)

    except ComponentCallError as e:
        logger.error("获取用户部门ids失败：username=%s, error=%s" % (username, str(e)))
        return []
    return set(department_ids)


def get_department_info(department_id):
    try:
        res = client_backend.usermanage.retrieve_department({"id": department_id})
    except ComponentCallError as e:
        logger.error("获取组织架构详情失败：department_id=%s, error=%s" % (department_id, str(e)))
        return []
    return res


def list_departments_info():
    try:
        res = get_list_departments({"fields": "name,id"})
    except ComponentCallError as e:
        logger.error("获取组织架构失败：error={}".format(str(e)))
        return []
    return res


def get_user_departments(username, id_only):
    """获取用户所属部门信息"""
    cache_key = "%suser_departments_%s_%s" % (PREFIX_KEY, username, id_only)
    departments = cache.get(cache_key)

    if not departments:
        departments = update_user_departments(cache_key, username, id_only)
    else:
        update_user_departments.delay(cache_key, username, id_only)

    return departments


def get_systems():
    """获取ESB中的组件系统列表"""
    try:
        # res = client_backend.api_gateway.get_systems()
        res = bk.http(
            {
                "path": "/api/c/compapi/v2/esb/get_systems/",
                "method": "get",
                "query_params": {},
            }
        )
        return res.get("data", [])
    except Exception as e:
        logger.error("获取ESB中的组件系统列表：error=%s" % str(e))
        return []


def get_components(system_names):
    """获取指定系统的组件列表"""
    try:
        # res = client_backend.api_gateway.get_components({"system_names": system_names})
        res = bk.http(
            {
                "path": "/api/c/compapi/v2/esb/get_components/",
                "method": "get",
                "query_params": {"system_names": system_names},
            }
        )
        return res.get("data", [])
    except Exception as e:
        logger.error("获取指定系统的组件列表: system_names=%s, error=%s" % (system_names, str(e)))
        return []


def get_group_next_data(bk_obj_id, bk_inst_id):
    params = {
        "bk_supplier_account": "0",
        "bk_obj_id": bk_obj_id,
        "bk_inst_id": bk_inst_id,
    }
    try:
        rsp = client_backend.cc.search_inst_association_topo(params)
        next_topo = rsp[0]["children"]
    except (ComponentCallError, KeyError, IndexError, TypeError) as error:
        logger.warning("获取业务列表失败：%s" % str(error))
        next_topo = []
    return next_topo


def get_template_list(bk_biz_id=2):
    params = {"bk_biz_id": bk_biz_id, "template_source": "business"}
    try:
        response = client_backend.sops.get_template_list(**params)
        return response
    except Exception as error:
        message = "获取标准运维流程列表出错，%s" % str(error)
        logger.warning(message)
        return []


def get_user_leader(username):
    name_list = username.strip(",").split(",")
    leaders_results = settings.ADAPTER_API.get_batch_users(
        name_list, properties="leader", is_exact=True
    )

    def retry(user_list):
        """
        重试拉取leader
        """
        results = settings.ADAPTER_API.get_batch_users(
            user_list, properties="leader", is_exact=True
        )

        logger.info(
            "[retry] name_list is {}, leaders_results is {}".format(user_list, results)
        )

        if not results:
            return []

        return results

    logger.info(
        "name_list is {}, leaders_results is {}".format(name_list, leaders_results)
    )
    if not leaders_results:
        leaders_results = retry(user_list=name_list)

    leaders = set()
    for detail in leaders_results:
        for leader in detail["leader"]:
            leaders.add(leader["username"])
    return list(leaders)
