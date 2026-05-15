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

import logging

from bkapi_client_core.base import Operation

from bkapi_client_core.django_helper import _get_client_by_settings
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
from bkapi_client_core.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.django_helper import get_client_by_username as _get_client_by_username
from bkapi_client_core.property import bind_property
from bkapi_client_core.utils import generic_type_partial as _partial

from blueking.apigw.base import ApiProtocol, TenantBaseClient
from blueking.apigw.utils import get_endpoint


class Client(TenantBaseClient):
    """蓝鲸标准运维 API 客户端"""

    # 通过流程模板新建周期任务
    create_periodic_task = bind_property(
        Operation,
        name="create_periodic_task",
        method="POST",
        path="/create_periodic_task/{template_id}/{bk_biz_id}/",
    )

    # 通过流程模板新建任务
    create_task = bind_property(
        Operation,
        name="create_task",
        method="POST",
        path="/create_task/{template_id}/{bk_biz_id}/",
    )
    
    system_create_task = bind_property(
        Operation,
        name="system_create_task",
        method="POST",
        path="/system/create_task/{template_id}/{bk_biz_id}/",
    )

    # 查询单个公共流程模板详情
    get_common_template_info = bind_property(
        Operation,
        name="get_common_template_info",
        method="GET",
        path="/get_common_template_info/{template_id}/",
    )

    # 查询公共模板列表
    get_common_template_list = bind_property(
        Operation,
        name="get_common_template_list",
        method="GET",
        path="/get_common_template_list/",
    )

    # 查询业务下的某个周期任务详情
    get_periodic_task_info = bind_property(
        Operation,
        name="get_periodic_task_info",
        method="GET",
        path="/get_periodic_task_info/{task_id}/{bk_biz_id}/",
    )

    # 查询业务下的周期任务列表
    get_periodic_task_list = bind_property(
        Operation,
        name="get_periodic_task_list",
        method="GET",
        path="/get_periodic_task_list/{bk_biz_id}/",
    )

    # 查询任务执行详情
    get_task_detail = bind_property(
        Operation,
        name="get_task_detail",
        method="GET",
        path="/get_task_detail/{task_id}/{bk_biz_id}/",
    )

    # 查询任务节点执行详情
    get_task_node_detail = bind_property(
        Operation,
        name="get_task_node_detail",
        method="GET",
        path="/get_task_node_detail/{task_id}/{bk_biz_id}/",
    )
    
    system_get_task_node_detail = bind_property(
        Operation,
        name="system_get_task_node_detail",
        method="GET",
        path="/system/get_task_node_detail/{task_id}/{bk_biz_id}/",
    )

    # 查询任务或任务节点执行状态
    get_task_status = bind_property(
        Operation,
        name="get_task_status",
        method="GET",
        path="/get_task_status/{task_id}/{bk_biz_id}/",
    )
    
    system_get_task_status = bind_property(
        Operation,
        name="system_get_task_status",
        method="GET",
        path="/system/get_task_status/{task_id}/{bk_biz_id}/",
    )

    # 批量查询任务执行状态
    get_tasks_status = bind_property(
        Operation,
        name="get_tasks_status",
        method="POST",
        path="/get_tasks_status/{bk_biz_id}/",
    )

    # 查询单个模板详情
    get_template_info = bind_property(
        Operation,
        name="get_template_info",
        method="GET",
        path="/get_template_info/{template_id}/{bk_biz_id}/",
    )

    # 查询模板列表
    get_template_list = bind_property(
        Operation,
        name="get_template_list",
        method="GET",
        path="/get_template_list/{bk_biz_id}/",
    )

    # 导入公共流程
    import_common_template = bind_property(
        Operation,
        name="import_common_template",
        method="POST",
        path="/import_common_template/",
    )

    # 修改周期任务的全局参数
    modify_constants_for_periodic_task = bind_property(
        Operation,
        name="modify_constants_for_periodic_task",
        method="POST",
        path="/modify_constants_for_periodic_task/{task_id}/{bk_biz_id}/",
    )

    # 修改周期任务的调度策略
    modify_cron_for_periodic_task = bind_property(
        Operation,
        name="modify_cron_for_periodic_task",
        method="POST",
        path="/modify_cron_for_periodic_task/{task_id}/{bk_biz_id}/",
    )

    # 回调任务节点
    node_callback = bind_property(
        Operation,
        name="node_callback",
        method="POST",
        path="/node_callback/{task_id}/{bk_biz_id}/",
    )

    # 操作任务
    operate_task = bind_property(
        Operation,
        name="operate_task",
        method="POST",
        path="/operate_task/{task_id}/{bk_biz_id}/",
    )

    # 查询任务分类统计总数
    query_task_count = bind_property(
        Operation,
        name="query_task_count",
        method="POST",
        path="/query_task_count/{bk_biz_id}/",
    )

    # 设置周期任务是否激活
    set_periodic_task_enabled = bind_property(
        Operation,
        name="set_periodic_task_enabled",
        method="POST",
        path="/set_periodic_task_enabled/{task_id}/{bk_biz_id}/",
    )

    # 开始执行任务
    start_task = bind_property(
        Operation,
        name="start_task",
        method="POST",
        path="/start_task/{task_id}/{bk_biz_id}/",
    )
    
    system_start_task = bind_property(
        Operation,
        name="start_task",
        method="POST",
        path="/system/start_task/{task_id}/{bk_biz_id}/",
    )

    # 操作任务节点
    operate_node = bind_property(
        Operation,
        name="operate_node",
        method="POST",
        path="/operate_node/{task_id}/{bk_biz_id}/",
    )

    # 获取任务列表
    get_task_list = bind_property(
        Operation,
        name="get_task_list",
        method="GET",
        path="/get_task_list/{bk_biz_id}/",
    )

    # 获取模版执行方案列表
    get_template_schemes = bind_property(
        Operation,
        name="get_template_schemes",
        method="GET",
        path="/get_template_schemes/{template_id}/{bk_biz_id}/",
    )

    # 修改任务参数
    modify_constants_for_task = bind_property(
        Operation,
        name="modify_constants_for_task",
        method="POST",
        path="/modify_constants_for_task/{task_id}/{bk_biz_id}/",
    )

    # 认领职能化任务
    claim_functionalization_task = bind_property(
        Operation,
        name="claim_functionalization_task",
        method="POST",
        path="/claim_functionalization_task/{task_id}/{bk_biz_id}/",
    )

    # 获取节点选择后新的任务树
    preview_task_tree = bind_property(
        Operation,
        name="preview_task_tree",
        method="POST",
        path="/preview_task_tree/{template_id}/{bk_biz_id}/",
    )

    # 获取公共流程节点选择后新的任务树
    preview_common_task_tree = bind_property(
        Operation,
        name="preview_common_task_tree",
        method="POST",
        path="/preview_common_task_tree/{template_id}/",
    )

    # 获取用户有权限的项目列表
    get_user_project_list = bind_property(
        Operation,
        name="get_user_project_list",
        method="GET",
        path="/get_user_project_list/",
    )


class BkSopsApi(ApiProtocol):
    """蓝鲸标准运维 API 协议类"""

    _api_name = "bk-sops"

    @staticmethod
    def _is_token_expired(token_obj) -> bool:
        """判断 token 是否已过期。"""
        expires = getattr(token_obj, "expires", None)
        if not expires:
            logger.warning("[BkSopsApi] access_token 缺少 expires 字段，无法判断是否过期")
            return False

        now = timezone.now()
        try:
            return now >= expires
        except TypeError:
            if timezone.is_naive(expires):
                expires = timezone.make_aware(expires, timezone.get_current_timezone())
            else:
                expires = timezone.localtime(expires, timezone.get_current_timezone())
            return now >= expires

    @classmethod
    def _refresh_token_if_needed(cls, token_obj, username):
        """token 已过期或即将过期时尝试刷新，失败则返回 None。"""
        token_expired = cls._is_token_expired(token_obj)
        token_expires_soon = getattr(token_obj, "expires_soon", False)

        if not (token_expired or token_expires_soon):
            return token_obj

        refresh_token = getattr(token_obj, "refresh_token", "")
        if not refresh_token:
            logger.warning(
                "[BkSopsApi] access_token 已过期或即将过期但无 refresh_token, username=%s, expired=%s, expires_soon=%s",
                username,
                token_expired,
                token_expires_soon,
            )
            return None

        try:
            from bkoauth.client import oauth_client

            refreshed_token_obj = oauth_client.refresh_token(token_obj)
            logger.info(
                "[BkSopsApi] access_token 刷新成功, username=%s, expired=%s, expires_soon=%s",
                username,
                token_expired,
                token_expires_soon,
            )
        except Exception as refresh_err:
            logger.warning(
                "[BkSopsApi] 刷新 access_token 失败, username=%s, expired=%s, expires_soon=%s, error=%s",
                username,
                token_expired,
                token_expires_soon,
                refresh_err,
            )
            return None

        if cls._is_token_expired(refreshed_token_obj):
            logger.warning("[BkSopsApi] 刷新后 access_token 仍已过期, username=%s", username)
            return None

        return refreshed_token_obj

    @classmethod
    def get_client(cls) -> Client:
        """通过 settings 配置获取客户端（无用户上下文）"""
        return _get_client_by_settings(Client, endpoint=get_endpoint(cls._api_name, "prod"))

    @classmethod
    def get_client_by_request(cls, request):
        """通过 request 对象获取客户端（有用户上下文，推荐在视图中使用）"""
        return (_partial(Client, _get_client_by_request)
                (request, endpoint=get_endpoint(cls._api_name, "prod")))

    @classmethod
    def get_client_by_username(cls, username):
        """通过用户名获取客户端（有用户上下文，推荐在后台任务中使用）"""
        return (_partial(Client, _get_client_by_username)
                (username, endpoint=get_endpoint(cls._api_name, "prod")))

    @classmethod
    def call_api_with_auth(
        cls,
        api_name,
        bk_username,
        path_params=None,
        params=None,
        data=None,
        app_code=None,
        app_secret=None,
    ):
        """使用 app_code、app_secret、bk_username 鉴权并调用 API。"""
        client = cls.get_client()
        client.update_bkapi_authorization(
            bk_app_code=app_code or settings.BK_APP_CODE,
            bk_app_secret=app_secret or settings.BK_APP_SECRET,
            bk_username=bk_username,
        )

        call_kwargs = {}
        if path_params is not None:
            call_kwargs["path_params"] = path_params
        if params is not None:
            call_kwargs["params"] = params
        if data is not None:
            call_kwargs["data"] = data

        return getattr(client, api_name)(**call_kwargs)

    @classmethod
    def get_client_with_token(cls, username) -> Client:
        client = _get_client_by_settings(Client, endpoint=get_endpoint(cls._api_name, "prod"))
        access_token = None

        try:
            from bkoauth.models import AccessToken
            from bkoauth.django_conf import ENV_NAME

            token_obj = AccessToken.objects.filter(env_name=ENV_NAME, user_id=username).first()
            if not token_obj:
                logger.warning("[BkSopsApi] 数据库中未找到 access_token, username=%s", username)
            else:
                token_obj = cls._refresh_token_if_needed(token_obj, username)
                if token_obj is not None and not cls._is_token_expired(token_obj):
                    access_token = token_obj.access_token
                    logger.info("[BkSopsApi] 从数据库获取有效 access_token 成功, username=%s", username)
                else:
                    logger.warning(
                        "[BkSopsApi] access_token 已过期或刷新失败，回退到 bk_username, username=%s",
                        username,
                    )
        except Exception as e:
            logger.warning("[BkSopsApi] 从数据库获取 access_token 失败, username=%s, error=%s", username, e)

        if access_token:
            client.update_bkapi_authorization(access_token=access_token)
            logger.info("[BkSopsApi] get_client_with_token 完成（携带 access_token）, username=%s", username)
        else:
            client.update_bkapi_authorization(bk_username=username)
            logger.info("[BkSopsApi] get_client_with_token 完成（回退为 bk_username）, username=%s", username)
        return client
