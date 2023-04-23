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

import os
import traceback
from functools import wraps

from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as RrfValidationError
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext as _

from itsm.component.bkoauth.jwt_client import JWTClient, jwt_invalid_view
from itsm.component.exceptions import ServerError, ParamError
from itsm.component.utils.response import Fail

from itsm.component.utils.basic import ComplexRegexField, size_mapper

from common.log import logger


def no_args_template(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        """
        无参装饰器（视图函数）
        """

        return view_func(request, *args, **kwargs)

    return __wrapper


def with_args_template(param1, param2=None):
    """
    带参装饰器（视图函数）
    """

    def decorator(view_func):
        # @wraps(view_func, assigned=available_attrs(view_func))
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def log_decorators(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        logger.info("%s is running" % view_func.__name__)
        result = view_func(request, *args, **kwargs)
        logger.info("%s is finished" % view_func.__name__)
        return result

    return __wrapper


def logs(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(*args, **kwargs):
        logger.info("%s is running" % view_func.__name__)
        result = view_func(*args, **kwargs)
        logger.info("%s is finished" % view_func.__name__)
        return result

    return __wrapper


def is_file_name_valid(file_name):
    """
    校验文件名称的有效性
    :param file_name: 文件名称
    """
    file_name_validator = ComplexRegexField(
        validate_type=["en", "ch", "num", "special"], special_char="()_ .-"
    )
    file_name_validator.validate(file_name)


def validate_file_name(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        """
        无参装饰器（视图函数）
        """

        file_name = request.GET.get("file_name")

        try:
            is_file_name_valid(file_name)
        except ValidationError as error:
            return Fail(_("文件上传失败：{}").format(str(error)), "FILE_NAME_INVALID").json()
        except RrfValidationError as error:
            return Fail(
                _("文件上传失败：{}").format(error.detail[0]), "FILE_NAME_INVALID"
            ).json()

        return view_func(request, *args, **kwargs)

    return __wrapper


def validate_files_name(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        """
        无参装饰器（视图函数）
        """

        file_list = request.FILES.getlist("field_file")
        if not file_list:
            return Fail(_("文件上传失败：列表不能为空"), "FILE_LIST_EMPTY").json()

        for upload_file in file_list:
            try:
                is_file_name_valid(upload_file.name)
            except ValidationError as error:
                return Fail(
                    _("文件上传失败：{}").format(str(error)), "FILE_NAME_INVALID"
                ).json()
            except RrfValidationError as error:
                return Fail(
                    _("文件上传失败：{}").format(error.detail[0]), "FILE_NAME_INVALID"
                ).json()

        return view_func(request, *args, **kwargs)

    return __wrapper


def validate_file_upload(max_size, content_types=None, file_exts=None):
    """
    文件上传校验，带参装饰器
        max_size: 单位G/M/K
    """

    def decorator(view_func):
        # @wraps(view_func, assigned=available_attrs(view_func))
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            upload_file = request.FILES.get("files[]")
            max_upload_size = size_mapper(max_size)

            # 文件大小校验
            if upload_file.size == 0:
                return JsonResponse(
                    {
                        "code": "FILE_NOT_ALLOWED",
                        "result": False,
                        "message": _("禁止上传空文件."),
                    }
                )
            elif upload_file.size > max_upload_size:
                return JsonResponse(
                    {
                        "code": "FILE_NOT_ALLOWED",
                        "result": False,
                        "message": _("上传文件大小不得超过%s.") % max_size,
                    }
                )

            # application/type， 对type进行白名单校验
            if (
                content_types
                and upload_file.content_type.split("/")[-1] not in content_types
            ):
                return JsonResponse(
                    {
                        "code": "FILE_NOT_ALLOWED",
                        "result": False,
                        "message": _("上传文件类型仅支持：%s") % ", ".join(content_types),
                    }
                )

            # 对文件后缀进行白名单校验
            if file_exts and os.path.splitext(upload_file.name)[-1] not in file_exts:
                return JsonResponse(
                    {
                        "code": "FILE_NOT_ALLOWED",
                        "result": False,
                        "message": _("上传文件类型仅支持：%s") % ", ".join(file_exts),
                    }
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def validate_filepath_settings(view_func):
    # @wraps(view_func, assigned=available_attrs(view_func))
    @wraps(view_func)
    def __wrapper(request, *args, **kwargs):
        """
        系统配置校验装饰器：附件目录
        """

        from itsm.iadmin.models import SystemSettings

        try:
            system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value
            if not os.path.exists(system_file_path):
                return Fail(_("请检查系统配置：附件存储目录不存在"), "SYS_FILE_PATH_INVALID").json()
        except SystemSettings.DoesNotExist:
            return Fail(_("请检查系统配置：附件存储的目录配置无效"), "SYS_FILE_PATH_EMPTY").json()
        except Exception as e:
            return Fail(_("附件路径生成异常：%s") % e, "FILE_PATH_EXCEPTION").json()

        return view_func(request, *args, **kwargs)

    return __wrapper


def fbv_exception_handler(view_func):
    @wraps(view_func)
    def _exception_handler(request, *args, **kw):
        try:
            response = view_func(request, *args, **kw)
        except ServerError as e:
            # 捕捉常见的异常
            return JsonResponse(
                {
                    "result": False,
                    "code": e.code_int,
                    "data": None,
                    "message": e.message,
                }
            )
        except KeyError as e:
            return JsonResponse(
                {
                    "result": False,
                    "code": ParamError.ERROR_CODE_INT,
                    "data": None,
                    "message": _("接口异常，缺少请求参数: {}").format(e),
                }
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse(
                {
                    "result": False,
                    "code": ServerError.ERROR_CODE_INT,
                    "data": None,
                    "message": _("接口异常: {}").format(e),
                }
            )
        return response

    return _exception_handler


# def custom_apigw_required(view_func):
#     """apigw装饰器"""
#
#     @wraps(view_func)
#     def _wrapped_view(self, request, *args, **kwargs):
#         request.jwt = JWTClient(request)
#         if not request.jwt.is_valid:
#             return jwt_invalid_view(request)
#         return view_func(self, request, *args, **kwargs)
#
#     return _wrapped_view


def custom_apigw_required(view_func):
    """apigw装饰器"""

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):

        exempt = getattr(settings, "BK_APIGW_REQUIRE_EXEMPT", False)
        if exempt:
            return view_func(self, request, *args, **kwargs)

        if not hasattr(request, "jwt"):
            logger.warning(
                "can not found jwt in request, "
                "make sure ApiGatewayJWTGenericMiddleware is config in middlewares or receive jwt is valid"
                # noqa
            )
            return HttpResponse(
                status=403, content="This API can only be accessed through API gateway"
            )

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


def apigw_required(view_func):
    """apigw装饰器"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.jwt = JWTClient(request)
        if not request.jwt.is_valid:
            return jwt_invalid_view(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
