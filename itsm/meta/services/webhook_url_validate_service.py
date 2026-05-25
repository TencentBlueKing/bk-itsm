# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from pipeline.utils.boolrule import BoolRule
from pipeline.utils.boolrule.boolrule import SubstituteVal
from pyparsing import ParseResults

from itsm.meta.services.context import ContextService


class WebhookURLValidateService:
    ALLOWED_HOST_SUFFIXES_CONTEXT_KEY = "webhook_allowed_host_suffixes"
    TEMPLATE_MARKERS = ("{{", "{%")
    MAX_SUCCESS_EXP_LENGTH = 200

    @classmethod
    def get_allowed_host_suffixes(cls):
        raw_value = (
            ContextService.get_context_value(cls.ALLOWED_HOST_SUFFIXES_CONTEXT_KEY)
            or ""
        )
        normalized_value = raw_value.replace("\n", ",").replace(";", ",")
        allowed_hosts = []

        for item in normalized_value.split(","):
            item = item.strip().lower().rstrip(".")
            if not item:
                continue
            allowed_hosts.append(item)

        return list(dict.fromkeys(allowed_hosts))

    @classmethod
    def contains_template(cls, url):
        if not isinstance(url, str):
            return False
        return any(marker in url for marker in cls.TEMPLATE_MARKERS)

    @classmethod
    def is_allowed_hostname(cls, hostname):
        normalized_hostname = hostname.strip().lower().rstrip(".")
        allowed_hosts = cls.get_allowed_host_suffixes()
        if not allowed_hosts:
            raise ValueError("未配置可访问的授权域名")

        for pattern in allowed_hosts:
            if pattern.startswith("*."):
                suffix = pattern[2:]
                if suffix and normalized_hostname.endswith("." + suffix):
                    return True
                continue

            if normalized_hostname == pattern:
                return True

        return False

    @classmethod
    def validate_for_execute(cls, url):
        try:
            parsed = urlparse(url)
        except Exception as error:
            raise ValueError("URL 格式错误, error={}".format(error))

        if parsed.scheme not in ["http", "https"]:
            raise ValueError("仅支持 http/https 协议")

        if not parsed.hostname:
            raise ValueError("URL 缺少 hostname")

        if parsed.username or parsed.password:
            raise ValueError("URL 不允许携带用户名或密码")

        if not cls.is_allowed_hostname(parsed.hostname):
            raise ValueError(
                "目标域名未被授权访问, hostname={}".format(parsed.hostname)
            )

    @classmethod
    def validate_for_config(cls, url):
        if not url:
            return

        if cls.contains_template(url):
            parsed = urlparse(url)
            if parsed.scheme and parsed.scheme not in ["http", "https"]:
                raise ValueError("仅支持 http/https 协议")
            if parsed.username or parsed.password:
                raise ValueError("URL 不允许携带用户名或密码")
            return

        cls.validate_for_execute(url)

    @classmethod
    def iter_substitute_values(cls, token):
        if isinstance(token, SubstituteVal):
            yield token
            return

        if isinstance(token, ParseResults):
            for item in token.asList():
                for sub_token in cls.iter_substitute_values(item):
                    yield sub_token
            return

        if isinstance(token, list):
            for item in token:
                for sub_token in cls.iter_substitute_values(item):
                    yield sub_token

    @classmethod
    def validate_success_exp(cls, success_exp):
        if not success_exp:
            return

        if not isinstance(success_exp, str):
            raise ValueError("success_exp 必须为字符串")

        success_exp = success_exp.strip()
        if not success_exp:
            return

        if len(success_exp) > cls.MAX_SUCCESS_EXP_LENGTH:
            raise ValueError("success_exp 长度不能超过 {} 个字符".format(cls.MAX_SUCCESS_EXP_LENGTH))

        try:
            rule = BoolRule(success_exp)
        except Exception as error:
            raise ValueError("success_exp 表达式非法, error={}".format(error))

        for token in cls.iter_substitute_values(rule._tokens):
            if not token._path.startswith("resp"):
                raise ValueError("success_exp 仅允许引用 resp 返回值")
