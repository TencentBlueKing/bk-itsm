# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

import json

from bkapi_client_core.exceptions import APIGatewayResponseError
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.http import JsonResponse, HttpResponse

from blueking.apigw.bkapis.bk_sops import BkSopsApi
from blueking.apigw.bkapis.bk_user import BkUserApi
from common.log import logger
from common.utils import filter_user_sensitive_info
from itsm.component.constants import CACHE_5MIN, PREFIX_KEY, CACHE_30MIN
from itsm.component.decorators import fbv_exception_handler
from itsm.component.esb.esbclient import client_backend
from itsm.component.exceptions import (
    ComponentCallError,
    IamPermissionDenied,
    RemoteCallError,
)
from itsm.component.constants import ResponseCodeStatus
from itsm.component.constants.iam import HTTP_499_IAM_FORBIDDEN
from itsm.component.utils.basic import build_tree
from itsm.component.utils.client_backend_query import (
    get_biz_choices,
    get_list_departments,
    get_list_department_profiles,
)
from itsm.component.utils.response import Fail, Success
from itsm.component.apigw import client as apigw_client

from django.conf import settings

from itsm.gateway.utils import batch_process

adapter_api = settings.ADAPTER_API

MAX_PAGE_SIZE = 50
MIN_PAGE_SIZE = 1


@fbv_exception_handler
def get_token(request):
    try:
        import bkoauth

        user = request.GET.get("user")
        access_token_obj = bkoauth.get_access_token_by_user(user)
        access_token = access_token_obj.access_token
        return Success({"access_token": access_token}).json()
    except Exception as err:
        return Success({"access_token": err}).json()


@fbv_exception_handler
def get_batch_users(request):
    """批量获取用户信息"""
    users = (
        request.GET.get("users")
        or request.GET.get("exact_lookups")
        or request.GET.get("fuzzy_lookups")
    )
    properties = request.GET.get("properties", "")
    callback_func_name = request.GET.get("callback")

    page_params = {
        "page": int(request.GET.get("page", 1)),
        "page_size": int(request.GET.get("page_size", 20)),
    }

    # 是否启用精准匹配，默认为True
    is_exact = True
    if "fuzzy_lookups" in request.GET:
        is_exact = False

    if not users:
        return Fail(_("用户名列表不能为空"), "BK_LOGIN.GET_BATCH_USERS").json()
    if isinstance(users, str):
        users = users.split(",")

    try:
        res = filter_user_sensitive_info(adapter_api.get_batch_users(users, properties, is_exact, page_params))
        if callback_func_name:
            response = {
                "result": True,
                "message": "success",
                "data": {"results": res, "count": len(res)},
                "code": 0,
            }
            response = HttpResponse(
                "{}({})".format(callback_func_name, json.dumps(response))
            )
            response["Content-Type"] = "application/x-javascript; charset=utf-8"
            return response
        return Success(res).json()
    except Exception as error:
        logger.warning(_("批量获取用户信息出错，%s"), str(error))
        return Fail(
            _("批量获取用户信息出错，%s") % str(error), "BK_LOGIN.GET_BATCH_USERS"
        ).json()


@fbv_exception_handler
def get_all_users(request):
    """获取所有用户列表"""

    cache_key = "%sall_users" % PREFIX_KEY
    all_users = cache.get(cache_key)
    if all_users is not None:
        return Success(all_users).json()

    try:
        users = adapter_api.get_all_users()
    except ComponentCallError as e:
        return Fail(str(e), "BK_LOGIN.GET_ALL_USERS").json()

    cache.set(cache_key, users, CACHE_30MIN)

    return Success(users).json()


@cache_page(CACHE_5MIN, cache="default")
def get_app_list(request):
    return Success(get_biz_choices()).json()


@cache_page(CACHE_5MIN, cache="default")
def get_departments(request):
    """获取部门列表信息
    data = [
        {
            "parent": -1,
            "route": [],
            "id": 1,
            "name": "blarg",
            "prop2": "blarg2",
            "children": [
                {
                    "parent": 1,
                    "route": [
                        1
                    ],
                    "id": 2,
                    "name": "blarg",
                    "prop2": "blarg2",
                    "children": [
                        {
                            "prop2": "blarg2",
                            "route": [
                                1,
                                2
                            ],
                            "id": 6,
                            "parent": 2,
                            "name": "blarg"
                        },
                        {
                            "prop2": "blarg2",
                            "route": [
                                1,
                                2
                            ],
                            "id": 7,
                            "parent": 2,
                            "name": "blarg"
                        }
                    ]
                },
                {
                    "prop2": "blarg2",
                    "route": [
                        1
                    ],
                    "id": 4,
                    "parent": 1,
                    "name": "blarg"
                }
            ]
        }
    ]

    """
    try:
        # 获取所有部门的扁平化列表信息
        res = get_list_departments({"fields": "id,name,parent,level,order"})

        # 转换成树状结构
        res = build_tree(res, "parent", need_route=True)
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_LIST").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_first_level_departments(request):
    # 仅仅获取第一层的组织架构
    try:
        params = {
            "lookup_field": "level",
            "exact_lookups": "0",
        }
        res = get_list_departments(params)
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_LIST").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_users(request):
    """获取部门用户列表，支持递归查询"""
    try:
        department_id = request.GET.get("id")
        recursive = request.GET.get("recursive") == "true"

        res = filter_user_sensitive_info(get_list_department_profiles(
            {"id": department_id, "recursive": recursive, "detail": True}
        ))

    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_USERS").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_users_count(request):
    """获取某个部门下的人员数量"""
    try:
        department_id = request.GET.get("id")
        # 只拉取第一页的数据，拿到用户数
        _client = BkUserApi.get_client()
        res = _client.list_department_user(
            path_params={"department_id": department_id},
            params={"recursive": True, "page": 1, "page_size": 1}
        )
    except APIGatewayResponseError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_USERS").json()
    return Success({"count": res.get("count", 0)}).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_info(request):
    """获取部门详情"""
    try:
        department_id = request.GET.get("id")
        _client = BkUserApi.get_client()
        res = _client.retrieve_department(
            path_params={"department_id": department_id}
        )
    except APIGatewayResponseError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_INFO").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_user_info(request):
    """获取人员所属部门"""
    try:
        username = request.GET.get("username", request.user.username)
        _client = BkUserApi.get_client()
        res = _client.list_user_department(
            path_params={"bk_username": username}
        )
    except APIGatewayResponseError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_USER_INFO").json()

    return Success(res).json()


@fbv_exception_handler
def get_user_project_list(request):
    """
    获取标准运维用户有权限的项目
    """
    try:
        sops_client = BkSopsApi.get_client_by_request(request)
        response = sops_client.get_user_project_list()
        
        # 获取返回数据
        res = response.get("data", [])
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_USER_PROJECT_LIST").json()


@fbv_exception_handler
def get_template_list(request):
    """
    获取标准运维流程模版列表
    BLAME: 上云环境无该接口
    with_common: 是否需要公共模板
    """

    bk_biz_id = request.GET.get("bk_biz_id", None)
    with_common = request.GET.get("with_common", None) == "true"

    try:
        sops_client = BkSopsApi.get_client_by_request(request)
        
        if bk_biz_id:
            # 获取业务模板列表
            response = sops_client.get_template_list(
                path_params={"bk_biz_id": bk_biz_id}
            )
            res = response.get("data", [])
            
            if with_common:
                # 获取公共模板列表
                response_com = sops_client.get_common_template_list()
                res_com = response_com.get("data", [])
                res.extend(res_com)
        else:
            # 只获取公共模板列表
            response = sops_client.get_common_template_list()
            res = response.get("data", [])
            
        return Success(res).json()
    except APIGatewayResponseError as e:
        return Fail(str(e), "SOPS.GET_COMMON_TEMPLATE_LIST").json()


@fbv_exception_handler
def get_template_detail(request):
    """
    获取标准运维流程详情
    BLAME: 上云环境无该接口
    """

    def get_constants(data):
        return list(data["pipeline_tree"]["constants"].values())

    def get_all_ids(data):
        """
        获取标准运维某个流程下的所有节点id
        """
        all_ids = []
        for node_id, content in data["pipeline_tree"]["activities"].items():
            all_ids.append(node_id)
        return all_ids

    def get_option_ids(data):
        option_keys = []
        for node_id, content in data["pipeline_tree"]["activities"].items():
            if content["optional"]:
                option_keys.append(node_id)
        return option_keys

    bk_biz_id = request.GET.get("bk_biz_id", None)
    template_id = request.GET.get("template_id")
    if not template_id:
        return Fail("invalid template_id", "SOPS.GET_TEMPLATE_DETAIL").json()

    try:
        sops_client = BkSopsApi.get_client_by_request(request)
        
        if bk_biz_id:
            # 获取业务模板详情
            response = sops_client.get_template_info(
                path_params={"template_id": template_id, "bk_biz_id": bk_biz_id}
            )
        else:
            # 获取公共模板详情
            response = sops_client.get_common_template_info(
                path_params={"template_id": template_id}
            )
        
        res = response.get("data", {})
        result = {
            "constants": get_constants(res),
            "optional_ids": get_option_ids(res),
            "all_ids": get_all_ids(res),
        }

        return Success(result).json()

    except IamPermissionDenied as error:

        data = {
            "result": False,
            "code": ResponseCodeStatus.PERMISSION_DENIED,
            "message": error.detail,
            "data": [],
            "permission": error.data,  # 具体的权限信息
        }
        return JsonResponse(data, status=HTTP_499_IAM_FORBIDDEN)

    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_TEMPLATE_DETAIL").json()


@fbv_exception_handler
def get_unfinished_sops_tasks(request):
    try:
        bk_biz_id = request.GET.get("bk_biz_id")
        sops_client = BkSopsApi.get_client_by_request(request)
        
        response = sops_client.get_task_list(
            path_params={"bk_biz_id": bk_biz_id},
            params={"is_started": False}
        )
        res = response.get("data", [])
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_UNFINISHED_SOPS_TASKS").json()


@fbv_exception_handler
def get_sops_tasks(request):
    try:
        support_params = ["is_started", "keyword", "is_finished", "limit", "offset"]
        bool_params = ["is_started", "is_finished"]
        bk_biz_id = request.GET.get("bk_biz_id")
        query_params = {}
        
        for param in support_params:
            param_value = request.GET.get(param)
            if param_value is not None:
                if param in bool_params:
                    query_params[param] = param_value == "true"
                else:
                    query_params[param] = param_value
        
        sops_client = BkSopsApi.get_client_by_request(request)
        response = sops_client.get_task_list(
            path_params={"bk_biz_id": bk_biz_id},
            params=query_params
        )
        res = response.get("data", [])
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_SOPS_TASKS").json()


@fbv_exception_handler
def get_sops_tasks_detail(request):
    try:
        bk_biz_id = request.GET.get("bk_biz_id")
        task_id = request.GET.get("task_id")
        
        sops_client = BkSopsApi.get_client_by_request(request)
        response = sops_client.get_task_detail(
            path_params={"bk_biz_id": bk_biz_id, "task_id": task_id}
        )
        res = response.get("data", {})
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_SOPS_TASKS_DETAIL").json()


@fbv_exception_handler
def get_sops_template_schemes(request):
    try:
        bk_biz_id = request.GET.get("bk_biz_id")
        res = []
        
        if bk_biz_id:
            template_id = request.GET.get("template_id")
            sops_client = BkSopsApi.get_client_by_request(request)
            response = sops_client.get_template_schemes(
                path_params={"bk_biz_id": bk_biz_id, "template_id": template_id}
            )
            res = response.get("data", [])
            
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_SOPS_TEMPLATE_SCHEMES").json()


@fbv_exception_handler
def get_sops_preview_task_tree(request):
    try:
        data = json.loads(request.body)
        bk_biz_id = data.get("bk_biz_id")
        template_id = data.get("template_id")
        exclude_task_nodes_id = data.get("exclude_task_nodes_id", [])
        
        sops_client = BkSopsApi.get_client_by_request(request)
        response = sops_client.preview_task_tree(
            path_params={"template_id": template_id, "bk_biz_id": bk_biz_id},
            data={"exclude_task_nodes_id": exclude_task_nodes_id}
        )
        res = response.get("data", {})
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_SOPS_PREVIEW_TASK_TREE").json()


@fbv_exception_handler
def get_sops_preview_common_task_tree(request):
    try:
        data = json.loads(request.body)
        template_id = data.get("template_id")
        exclude_task_nodes_id = data.get("exclude_task_nodes_id", [])
        
        sops_client = BkSopsApi.get_client_by_request(request)
        response = sops_client.preview_common_task_tree(
            path_params={"template_id": template_id},
            data={"exclude_task_nodes_id": exclude_task_nodes_id}
        )
        res = response.get("data", {})
        
        return Success(res).json()
    except (ComponentCallError, APIGatewayResponseError) as e:
        return Fail(str(e), "SOPS.GET_COMMON_SOPS_PREVIEW_TASK_TREE").json()


@fbv_exception_handler
def get_user_pipeline_list(request):
    try:
        res = apigw_client.devops.project_pipeline_list(
            {
                "project_id": request.GET["project_id"],
                "username": request.user.username,
                "pageSize": MAX_PAGE_SIZE,
            }
        )
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_UESR_PIPELINE_LIST").json()

    pipeline_list = []
    kwarg_list = [
        {
            "project_id": request.GET["project_id"],
            "username": request.user.username,
            "page": i + 1,
            "pageSize": MAX_PAGE_SIZE,
        }
        for i in range(0, int(res["totalPages"]))
    ]
    try:
        pipeline_list.extend(batch_process(get_user_pipeline_singel_page, kwarg_list))
        return Success(pipeline_list).json()
    except Exception as e:
        return Fail(
            _("批量获取流水线出错:{}".format(str(e))), "BK_LOGIN.GET_BATCH_USERS"
        ).json()


@fbv_exception_handler
def get_user_projects(request):
    try:
        res = apigw_client.devops.projects_list(
            {"username": request.user.username, "pageSize": MAX_PAGE_SIZE}
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_UESR_PROJECTS").json()


@fbv_exception_handler
def get_pipeline_build_list(request):
    try:
        res = apigw_client.devops.pipeline_build_list(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
                "page": request.GET["page"],
                "pageSize": request.GET["page_size"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_BUILD_LIST").json()


@fbv_exception_handler
def get_pipeline_build_start_info(request):
    try:
        res = apigw_client.devops.pipeline_build_start_info(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_BUILD_START_INFO").json()


@fbv_exception_handler
def get_user_pipeline_detail(request):
    try:
        res = apigw_client.devops.project_pipeline_detail(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_DETAIL").json()


@fbv_exception_handler
def start_user_pipeline(request):
    try:
        # {
        #     "username": request.user.username,
        #     "project_id": "bkee",
        #     "pipeline_id": "p-02f36a53fa604c2ca7089544eb374354",
        #     "APP_CODE": "bk_itsm",
        #     "RUN_VER": "ce",
        #     "UI_TYPE": "pc",
        #     "BRANCH": "no_redis_iam_branch",
        #     "RELEASE": "no",
        # }
        res = apigw_client.devops.pipeline_build_start(request.POST)
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.START_USER_PIPELINE").json()


@fbv_exception_handler
def get_user_pipeline_build_status(request):
    try:
        res = apigw_client.devops.pipeline_build_status(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
                "build_id": request.GET["build_id"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_STATUS").json()


@fbv_exception_handler
def get_user_pipeline_build_detail(request):
    try:
        res = apigw_client.devops.pipeline_build_detail(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
                "build_id": request.GET["build_id"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_STATUS").json()


@fbv_exception_handler
def get_pipeline_build_artifactory(request):
    try:
        res = apigw_client.devops.pipeline_build_artifactory_list(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "pipeline_id": request.GET["pipeline_id"],
                "build_id": request.GET["build_id"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_BUILD_ARTIFACTORY").json()


@fbv_exception_handler
def get_pipeline_build_artifactory_download_url(request):
    try:
        res = apigw_client.devops.pipeline_build_artifactory_third_party_download_url(
            {
                "username": request.user.username,
                "project_id": request.GET["project_id"],
                "artifactoryType": request.GET["artifactory_type"],
                "path": request.GET["path"],
            }
        )
        return Success(res).json()
    except RemoteCallError as e:
        return Fail(str(e), "DEVOPS.GET_PIPELINE_BUILD_ARTIFACTORY_DOWNLOAD_URL").json()


@fbv_exception_handler
def get_user_pipeline_singel_page(kwargs):
    try:
        res = apigw_client.devops.project_pipeline_list(kwargs)
        return res["records"]
    except RemoteCallError as e:
        logger.warning(_("批量获取流水线出错:{}, kwargs:{}".format(str(e), kwargs)))
