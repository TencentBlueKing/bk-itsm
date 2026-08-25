"""APIGW 客户端创建入口。"""

from bkapi_client_core.apigateway.django_helper import (
    get_client_by_request as _get_client_by_request,
)
from bkapi_client_core.apigateway.django_helper import (
    get_client_by_username as _get_client_by_username,
)

from .registry import get_client_class

_DEFAULT_GATEWAY = "sops"


def get_client_by_request(request, gateway=_DEFAULT_GATEWAY, **kwargs):
    """根据 Django Request 创建指定网关客户端。"""
    client_cls = get_client_class(gateway)
    return _get_client_by_request(client_cls, request, **kwargs)


def get_client_by_username(username, gateway=_DEFAULT_GATEWAY, **kwargs):
    """根据用户名创建指定网关客户端。"""
    client_cls = get_client_class(gateway)
    return _get_client_by_username(client_cls, username, **kwargs)


__all__ = ["get_client_by_request", "get_client_by_username"]
