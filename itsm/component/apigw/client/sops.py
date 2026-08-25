"""bk-sops APIGW client for bk-itsm."""

import re
from typing import Any

from bkapi_client_core.apigateway import Operation, OperationGroup, bind_property
from bkapi_client_core.apigateway.django_helper import (
    get_client_by_request as _get_client_by_request,
)
from bkapi_client_core.apigateway.django_helper import (
    get_client_by_username as _get_client_by_username,
)

from itsm.component.apigw.client.base import APIGatewayClient
from itsm.component.constants import API_PERMISSION_ERROR_CODE
from itsm.component.exceptions import ComponentCallError, IamPermissionDenied


class SOPSOperation(Operation):
    """兼容 bk-itsm 旧版 ESB 风格参数的 APIGW Operation。"""

    def __call__(
        self,
        data: Any | None = None,
        path_params: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs
    ):
        raw = False
        ignore_err = False
        values = {}

        if isinstance(data, dict):
            values.update(data)
        elif data is not None:
            return super().__call__(
                data=data,
                path_params=path_params,
                params=params,
                **kwargs
            )

        request_kwargs = {
            key: kwargs.pop(key)
            for key in ("headers", "timeout", "proxies", "verify")
            if key in kwargs
        }
        values.update(kwargs)
        raw = values.pop("__raw", False)
        ignore_err = values.pop("__ignore_err", False)
        values.pop("username", None)

        path_params = dict(path_params or {})
        for path_name in re.findall(r"{(\w+)}", self.path):
            if path_name in values:
                path_params[path_name] = values.pop(path_name)

        if self.method.upper() in ("GET", "HEAD", "OPTIONS"):
            request_params = dict(params or {})
            request_params.update(values)
            response = super().__call__(
                path_params=path_params,
                params=request_params,
                **request_kwargs
            )
        else:
            response = super().__call__(
                data=values,
                path_params=path_params,
                params=params,
                **request_kwargs
            )

        if raw or not isinstance(response, dict) or "result" not in response:
            return response
        if not response["result"] and not ignore_err:
            if response.get("code") == API_PERMISSION_ERROR_CODE:
                raise IamPermissionDenied(data=response.get("permission", []))
            raise ComponentCallError(response)
        return response.get("data")


class Group(OperationGroup):
    """SOPS APIGW 资源定义。"""

    get_common_template_info = bind_property(
        SOPSOperation,
        name="get_common_template_info",
        method="GET",
        path="/get_common_template_info/{template_id}/",
    )
    get_common_template_list = bind_property(
        SOPSOperation,
        name="get_common_template_list",
        method="GET",
        path="/get_common_template_list/",
    )
    get_template_list = bind_property(
        SOPSOperation,
        name="get_template_list",
        method="GET",
        path="/get_template_list/{bk_biz_id}/",
    )
    get_user_project_list = bind_property(
        SOPSOperation,
        name="get_user_project_list",
        method="GET",
        path="/get_user_project_list/",
    )
    get_template_info = bind_property(
        SOPSOperation,
        name="get_template_info",
        method="GET",
        path="/get_template_info/{template_id}/{bk_biz_id}/",
    )
    get_template_schemes = bind_property(
        SOPSOperation,
        name="get_template_schemes",
        method="GET",
        path="/get_template_schemes/{bk_biz_id}/{template_id}/",
    )
    preview_task_tree = bind_property(
        SOPSOperation,
        name="preview_task_tree",
        method="POST",
        path="/preview_task_tree/{bk_biz_id}/{template_id}/",
    )
    create_task = bind_property(
        SOPSOperation,
        name="create_task",
        method="POST",
        path="/create_task/{template_id}/{bk_biz_id}/",
    )
    start_task = bind_property(
        SOPSOperation,
        name="start_task",
        method="POST",
        path="/start_task/{task_id}/{bk_biz_id}/",
    )
    get_task_detail = bind_property(
        SOPSOperation,
        name="get_task_detail",
        method="GET",
        path="/get_task_detail/{task_id}/{bk_biz_id}/",
    )

    get_task_status = bind_property(
        SOPSOperation,
        name="get_task_status",
        method="GET",
        path="/get_task_status/{task_id}/{bk_biz_id}/",
    )
    get_task_node_detail = bind_property(
        SOPSOperation,
        name="get_task_node_detail",
        method="GET",
        path="/get_task_node_detail/{task_id}/{bk_biz_id}/",
    )
    get_tasks_status = bind_property(
        SOPSOperation,
        name="get_tasks_status",
        method="POST",
        path="/get_tasks_status/{bk_biz_id}/",
    )
    get_task_list = bind_property(
        SOPSOperation,
        name="get_task_list",
        method="GET",
        path="/get_task_list/{bk_biz_id}/",
    )
    claim_functionalization_task = bind_property(
        SOPSOperation,
        name="claim_functionalization_task",
        method="POST",
        path="/claim_functionalization_task/{task_id}/{bk_biz_id}/",
    )
    modify_constants_for_task = bind_property(
        SOPSOperation,
        name="modify_constants_for_task",
        method="POST",
        path="/modify_constants_for_task/{task_id}/{bk_biz_id}/",
    )
    operate_node = bind_property(
        SOPSOperation,
        name="operate_node",
        method="POST",
        path="/operate_node/{bk_biz_id}/{task_id}/",
    )
    preview_common_task_tree = bind_property(
        SOPSOperation,
        name="preview_common_task_tree",
        method="POST",
        path="/preview_common_task_tree/{bk_biz_id}/{template_id}/",
    )

    get_functionalization_task_list = bind_property(
        SOPSOperation,
        name="get_functionalization_task_list",
        method="GET",
        path="/get_functionalization_task_list/",
    )


class Client(APIGatewayClient):
    """bk-sops APIGW client。"""

    _api_name = "bk-sops"
    sops = bind_property(Group, name="sops")


SOPSClient = Client


def get_client_by_request(request, **kwargs):
    """根据当前请求创建带用户认证信息的 SOPS client。"""
    return _get_client_by_request(Client, request, **kwargs)


def get_client_by_username(username, **kwargs):
    """根据用户名创建带认证信息的 SOPS client。"""
    return _get_client_by_username(Client, username, **kwargs)


__all__ = [
    "SOPSOperation",
    "Group",
    "Client",
    "SOPSClient",
    "get_client_by_request",
    "get_client_by_username",
]
