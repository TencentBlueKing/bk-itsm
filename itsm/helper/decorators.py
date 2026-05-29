# -*- coding: utf-8 -*-
"""
itsm/helper/decorators.py

提供 helper 模块下高危后台运维接口（db_fix_* / export_api_system / weekly_statical 等）
所需的统一鉴权装饰器与异常处理装饰器。

设计动机
--------
原代码使用 ``django.contrib.auth.decorators.permission_required('is_superuser')``。
该装饰器实际调用 ``user.has_perms(('is_superuser',))``，
'is_superuser' 不是 ``app_label.codename`` 形式，
因此其行为依赖于认证后端对未注册权限码的处理：
  - 未登录用户被 302 重定向到 LOGIN_URL（暴露接口存在性）
  - 一旦认证后端 has_perm 在某些场景宽松返回 True（如自定义 / 第三方 backend），
    任意登录用户都可触发后台数据修复任务，构成越权 + 数据篡改。

修复策略
--------
统一改为 ``UserRole.is_itsm_superuser(username)``，与项目内
``itsm/iadmin/permissions.py``、``itsm/task/permissions.py`` 等模块保持一致；
未通过校验直接返回 403（不重定向，避免接口存在性泄露）。
"""

import functools
import logging

from django.http import HttpResponseForbidden, HttpResponse
from django.utils.translation import gettext as _

logger = logging.getLogger("root")


def itsm_superuser_required(view_func):
    """
    严格的 ITSM 超管校验装饰器。

    校验顺序：
    1. 必须为已认证用户，否则 403；
    2. 必须为 ``UserRole.is_itsm_superuser`` 返回 True 的真实业务超管，否则 403。

    任何失败一律返回 403，不重定向，避免接口枚举与存在性泄露。
    """

    @functools.wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # 延迟导入：避免在 Django app loading 阶段触发 role 模块循环依赖
        from itsm.role.models import UserRole

        user = getattr(request, "user", None)
        is_authed = bool(user and getattr(user, "is_authenticated", False))
        username = getattr(user, "username", "") or ""

        if not is_authed or not username:
            logger.warning(
                "helper admin api access denied: anonymous, path=%s, ip=%s",
                request.path,
                request.META.get("REMOTE_ADDR", "-"),
            )
            return HttpResponseForbidden(_("无权限"))

        try:
            is_admin = UserRole.is_itsm_superuser(username)
        except Exception:
            # 角色表查询异常时按"未授权"处理，避免 fail-open
            logger.exception(
                "helper admin api permission check failed, user=%s, path=%s",
                username,
                request.path,
            )
            return HttpResponseForbidden(_("无权限"))

        if not is_admin:
            logger.warning(
                "helper admin api access denied: not itsm superuser, "
                "user=%s, path=%s, ip=%s",
                username,
                request.path,
                request.META.get("REMOTE_ADDR", "-"),
            )
            return HttpResponseForbidden(_("无权限"))

        # 通过校验：在审计日志中留痕（含路径、调用人、来源 IP）
        logger.info(
            "helper admin api invoked, user=%s, path=%s, method=%s, ip=%s",
            username,
            request.path,
            request.method,
            request.META.get("REMOTE_ADDR", "-"),
        )
        return view_func(request, *args, **kwargs)

    return _wrapped


def safe_admin_response(task_name):
    """
    高危运维接口的统一异常处理装饰器。

    - 业务异常：仅日志记录完整堆栈，响应给调用方一段不可定位的中性信息；
    - 正常返回：原样透传视图返回值。

    用法::

        @itsm_superuser_required
        @safe_admin_response("db_fix_after_2_3_1")
        def db_fix_after_2_3_1(request):
            _db_fix_default_value_for_field.delay()
            return HttpResponse("任务已下发")
    """

    def _decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Exception:
                # 完整堆栈仅写日志，响应中绝不回吐 str(e) / traceback
                logger.exception(
                    "helper admin task dispatch failed, task=%s, user=%s",
                    task_name,
                    getattr(getattr(request, "user", None), "username", "-"),
                )
                return HttpResponse(
                    _("任务下发失败，请联系管理员排查"),
                    status=500,
                )

        return _wrapped

    return _decorator
