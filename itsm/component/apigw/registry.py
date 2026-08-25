"""APIGW 客户端注册中心。"""

import importlib
import os
from threading import RLock

from itsm.component.apigw.client.base import APIGatewayClient

_CLIENT_REGISTRY: dict[str, type[APIGatewayClient]] = {}
_CLIENT_MODULES_LOCK = RLock()
_CLIENT_MODULES_LOADED = False

# 自动发现 client/ 目录下所有非框架模块（排除 __init__、base 及遗留直连模块）
_CLIENT_DIR = os.path.join(os.path.dirname(__file__), "client")
_REGISTERED_CLIENT_MODULES = tuple(
    fname[:-3]
    for fname in os.listdir(_CLIENT_DIR)
    if fname.endswith(".py")
    and fname not in ("__init__.py", "base.py", "devops.py", "monitor.py")
)


def _load_registered_client_modules() -> None:
    """导入 client/ 目录下自动发现的客户端模块，并注册其中约定的 Client 类。"""
    global _CLIENT_MODULES_LOADED

    if _CLIENT_MODULES_LOADED:
        return

    with _CLIENT_MODULES_LOCK:
        if _CLIENT_MODULES_LOADED:
            return

        for module_name in _REGISTERED_CLIENT_MODULES:
            module = importlib.import_module(f"{__package__}.client.{module_name}")
            client_cls = getattr(module, "Client", None)
            if client_cls is None:
                raise TypeError(
                    f"APIGW client module {module_name!r} must define a Client class"
                )
            _register_gateway(module_name, client_cls)

        _CLIENT_MODULES_LOADED = True


def _normalize_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("APIGW client name must be a non-empty string")
    return name.strip().lower()


def _register_gateway(name: str, client_cls: type[APIGatewayClient]) -> None:
    """注册一个 APIGW 客户端类型。"""
    normalized_name = _normalize_name(name)
    if not isinstance(client_cls, type) or not issubclass(
        client_cls, APIGatewayClient
    ):
        raise TypeError(
            f"APIGW client {client_cls!r} must inherit from APIGatewayClient"
        )

    registered_cls = _CLIENT_REGISTRY.get(normalized_name)
    if registered_cls is not None and registered_cls is not client_cls:
        raise RuntimeError(f"APIGW client already registered: {normalized_name}")

    _CLIENT_REGISTRY[normalized_name] = client_cls


def get_client_class(name: str) -> type[APIGatewayClient]:
    """根据注册名获取 APIGW 客户端类型。"""
    normalized_name = _normalize_name(name)
    _load_registered_client_modules()
    try:
        return _CLIENT_REGISTRY[normalized_name]
    except KeyError:
        available = ", ".join(sorted(_CLIENT_REGISTRY)) or "<none>"
        raise ValueError(
            f"Unknown APIGW client: {normalized_name}, available clients: {available}"
        ) from None


def is_gateway_registered(name: str) -> bool:
    """判断指定网关是否已经注册。"""
    normalized_name = _normalize_name(name)
    _load_registered_client_modules()
    return normalized_name in _CLIENT_REGISTRY


def get_registered_gateways():
    """返回当前已注册的网关名称。"""
    _load_registered_client_modules()
    return tuple(sorted(_CLIENT_REGISTRY))


__all__ = [
    "get_client_class",
    "get_registered_gateways",
    "is_gateway_registered",
]
