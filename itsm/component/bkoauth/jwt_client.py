# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings
from django.http import HttpResponse

# 非强制安装PyJWT
from common.log import logger

try:
    from jwt import exceptions as jwt_exceptions
    import jwt

    has_jwt = True
except ImportError:
    has_jwt = False

try:
    import cryptography  # noqa

    has_crypto = True
except ImportError:
    has_crypto = False

from .utils import FancyDict

LOG = logging.getLogger("component")


class JWTClient(object):
    JWT_KEY_NAME = "HTTP_X_BKAPI_JWT"
    JWT_PUBLIC_KEY_HEADER_NAME = "HTTP_X_BKAPI_PUBLIC_KEY"
    JWT_RESOURCE = "HTTP_X_BKAPI_SOURCE"

    def __init__(self, request):
        self.request = request
        self.raw_content = request.META.get(self.JWT_KEY_NAME, "")
        self.error_message = ""
        self.is_valid = False

        self.payload = {}
        self.headers = {}
        self.get_jwt_info()

        self.app = self.get_app_model()
        self.user = self.get_user_model()

    def get_app_model(self):
        return FancyDict(self.payload.get("app", {}))

    def get_user_model(self):
        return FancyDict(self.payload.get("user", {}))

    def get_jwt_info(self):
        if has_jwt is False:
            self.error_message = u"【PyJWT】SDK未安装，请在requirements.txt中添加【PyJWT】后重新提测"
            return False
        if has_crypto is False:
            self.error_message = (
                u"【cryptography】SDK未安装，请在requirements.txt中添加【cryptography】后重新提测"
            )
            return False

        if not self.raw_content:
            self.error_message = u"【X_BKAPI_JWT】不在HTTP头部或者为空，请确认请求来源是否为 API Gateway"
            return False
        try:
            self.headers = jwt.get_unverified_header(self.raw_content)

            public_key = self._get_jwt_public_key()
            self.payload = jwt.decode(
                self.raw_content, public_key, algorithms=["RS512"], issuer="APIGW"
            )

            self.is_valid = True
        except jwt_exceptions.InvalidKeyError:
            self.error_message = (
                u"公钥设置错误，请在 API Gateway 下载网关公钥，并配置到Django配置项【APIGW_PUBLIC_KEY】"
            )
        except jwt_exceptions.DecodeError:
            self.error_message = u"【X_BKAPI_JWT】不合法，请确认格式或者使用合法私钥签名"
            import traceback

            traceback.print_exc()
        except jwt_exceptions.ExpiredSignatureError:
            self.error_message = u"【X_BKAPI_JWT】不合法，已经过期"
        except jwt_exceptions.InvalidIssuerError:
            self.error_message = u"【X_BKAPI_JWT】不合法，签发者不是APIGW"
        except Exception as error:
            LOG.exception("decode jwt fail")
            self.error_message = error.message

    def _get_jwt_public_key(self):
        """
        首先从请求 Header X-Bkapi-Public-Key 获取 JWT Public-Key，
        若 Header 中不存在，或者解析失败，则使用默认值
        """
        jwt_resource = self.request.META.get(self.JWT_RESOURCE, "ESB")
        logger.info("the api resource is {}".format(jwt_resource))
        if jwt_resource == "APIGW":
            return settings.APIGW_PUBLIC_KEY
        else:
            return settings.ESB_PUBLIC_KEY

    def __unicode__(self):
        return "<%s, %s>" % (self.headers, self.payload)


def jwt_invalid_view(request):
    """无效jwt返回"""
    LOG.warning("jwt_invalid %s" % request.jwt.error_message)
    data = {"result": False, "data": None, "message": request.jwt.error_message}
    return HttpResponse(json.dumps(data), content_type="application/json")
