# -*- coding: utf-8 -*-
"""openapi 鉴权覆盖测试。

背景：/openapi/** 被 ApiIgnoreCheck 豁免登录、被 ApiGenericMixin 放行 DRF 权限，
唯一防线是方法级的 @custom_apigw_required。历史上存在"漏覆写即匿名可达"的问题，
这里用两层回归把它钉住：

1. 覆盖率基线：/openapi/** 所有业务端点必须带网关鉴权装饰器；
2. 装饰器行为：无 JWT 拦截 403；有 JWT 放行；ieod 内部信任环境与应急开关按设计豁免。
"""
import inspect

import pytest
from django.test import override_settings
from django.urls import get_resolver
from rest_framework.response import Response

from itsm.component.decorators import custom_apigw_required

# DefaultRouter 生成的 APIRootView 只列举路由名，不含业务数据，不做鉴权要求
EXEMPT_VIEW_NAMES = {"APIRootView"}


def iter_openapi_handlers():
    """遍历 /openapi/** 路由，产出 (http方法, 路径, 视图名, handler)。"""
    def walk(patterns, prefix=""):
        for p in patterns:
            if hasattr(p, "url_patterns"):
                for item in walk(p.url_patterns, prefix + str(p.pattern)):
                    yield item
            else:
                path = prefix + str(p.pattern)
                if "/openapi/" not in "/" + path.lstrip("^"):
                    continue
                if "(?P<format>" in path:
                    # 格式后缀是同一 handler 的重复路由，跳过
                    continue
                callback = p.callback
                cls = getattr(callback, "cls", None)
                actions = getattr(callback, "actions", {})
                if cls is not None and actions:
                    for method, action in actions.items():
                        yield (
                            method.upper(),
                            "/" + path.lstrip("^"),
                            "{}.{}".format(cls.__name__, action),
                            getattr(cls, action, None),
                        )
                else:
                    yield (
                        "-",
                        "/" + path.lstrip("^"),
                        getattr(getattr(callback, "cls", callback), "__name__", str(callback)),
                        callback,
                    )

    for item in walk(get_resolver().url_patterns):
        yield item


def is_protected(handler):
    """handler 是否带网关鉴权装饰器。"""
    if handler is None:
        return False
    source = getattr(handler, "__wrapped__", handler)
    try:
        code = inspect.getsource(source)
    except (TypeError, OSError):
        return False
    return "apigw_required" in code


class FakeRequest(object):
    """最小请求替身：只提供 jwt 属性的有无。"""

    def __init__(self, has_jwt=False):
        if has_jwt:
            self.jwt = object()


class TestOpenApiAuthCoverage:
    def test_all_business_endpoints_protected(self):
        """/openapi/** 业务端点必须全部带网关鉴权装饰器。"""
        missing = []
        for method, path, name, handler in iter_openapi_handlers():
            if handler is None or name in EXEMPT_VIEW_NAMES:
                continue
            if not is_protected(handler):
                missing.append("{} {} -> {}".format(method, path, name))

        assert not missing, "以下端点缺少网关鉴权装饰器:\n" + "\n".join(missing)

    def test_openapi_endpoints_exists(self):
        """守卫：确保路由枚举真的扫到了端点，避免断言空跑通过。"""
        assert len(list(iter_openapi_handlers())) > 20


class TestCustomApigwRequired:
    @staticmethod
    def call_decorated(request):
        @custom_apigw_required
        def _view(self, request, *args, **kwargs):
            return Response("ok")

        return _view(None, request)

    @override_settings(RUN_VER="open", BK_APIGW_REQUIRE_EXEMPT=False)
    def test_without_jwt_rejected(self):
        """无 JWT：拦截，403。"""
        assert self.call_decorated(FakeRequest(has_jwt=False)).status_code == 403

    @override_settings(RUN_VER="open", BK_APIGW_REQUIRE_EXEMPT=False)
    def test_with_jwt_allowed(self):
        """有 JWT：放行。"""
        assert self.call_decorated(FakeRequest(has_jwt=True)).status_code == 200

    @override_settings(RUN_VER="ieod", BK_APIGW_REQUIRE_EXEMPT=False)
    def test_ieod_bypass_as_designed(self):
        """ieod 内部信任环境：按设计豁免（接入层收敛），不得误改成拦截。"""
        assert self.call_decorated(FakeRequest(has_jwt=False)).status_code == 200

    @override_settings(RUN_VER="open", BK_APIGW_REQUIRE_EXEMPT=True)
    def test_emergency_exempt_switch(self):
        """应急开关打开时放行。"""
        assert self.call_decorated(FakeRequest(has_jwt=False)).status_code == 200
