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

# """
#     框架补充相关代码
# """
import traceback

from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from django.conf import settings
from rest_framework.response import Response

from common.log import logger
from iam.exceptions import AuthFailedException
from itsm.component.constants import ResponseCodeStatus
from itsm.component.constants.iam import HTTP_499_IAM_FORBIDDEN
from itsm.component.utils.drf import format_validation_message
from .exceptions import ServerError, IamPermissionDenied


def exception_handler(exc, context):
    """

    分类：
        rest_framework框架内异常
        app自定义异常
    """
    data = {"result": False, "data": None}
    if isinstance(exc, AuthFailedException):
        # 权限中心校验异常, 直接抛出
        raise exc

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        data = {
            "result": False,
            "code": ResponseCodeStatus.UNAUTHORIZED,
            "detail": _("用户未登录或登录态失效，请使用登录链接重新登录"),
            "login_url": "",
        }
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, IamPermissionDenied):
        data = {
            "result": False,
            "code": ResponseCodeStatus.PERMISSION_DENIED,
            "message": exc.detail,
            "data": [],
            "permission": exc.data,  # 具体的权限信息
        }
        return Response(data, status=HTTP_499_IAM_FORBIDDEN)

    if isinstance(exc, PermissionDenied):
        data = {
            "result": False,
            "code": ResponseCodeStatus.PERMISSION_DENIED,
            "message": exc.detail,
        }
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    else:
        if isinstance(exc, ValidationError):
            data.update(
                {
                    "code": ResponseCodeStatus.VALIDATE_ERROR,
                    "messages": exc.detail,
                    "message": format_validation_message(exc),
                }
            )

        elif isinstance(exc, MethodNotAllowed):
            data.update(
                {
                    "code": ResponseCodeStatus.METHOD_NOT_ALLOWED,
                    "message": exc.detail,
                }
            )
        elif isinstance(exc, PermissionDenied):
            data.update(
                {
                    "code": ResponseCodeStatus.PERMISSION_DENIED,
                    "message": exc.detail,
                }
            )

        elif isinstance(exc, ServerError):
            # 更改返回的状态为为自定义错误类型的状态码
            data.update(
                {
                    "code": exc.code,
                    "message": exc.message,
                }
            )
        elif isinstance(exc, Http404):
            # 更改返回的状态为为自定义错误类型的状态码
            data.update(
                {
                    "code": ResponseCodeStatus.OBJECT_NOT_EXIST,
                    "message": _("当前操作的对象不存在"),
                }
            )
        else:
            # 全局兜底分支：未被识别的异常一律视为 5xx
            # 生产环境必须屏蔽 str(exc) / traceback，避免 SQL 报错、字段名、
            # 文件路径、KeyError 键名等敏感信息回吐至前端。
            # 仅当 settings.DEBUG=True 时才把异常细节带给调用方，便于本地排错。
            logger.error(traceback.format_exc())

            # 仅信任"已注册业务异常类（ServerError 子类）"的 message 字段；
            # 其它异常一律使用中性提示。
            if isinstance(exc, ServerError):
                safe_message = exc.message
            elif getattr(settings, "DEBUG", False):
                safe_message = getattr(exc, "message", str(exc))
            else:
                safe_message = _("系统繁忙，请稍后重试")

            data.update(
                {
                    "code": ResponseCodeStatus.SERVER_500_ERROR,
                    "message": safe_message,
                }
            )

        return Response(data, status=status.HTTP_200_OK)
