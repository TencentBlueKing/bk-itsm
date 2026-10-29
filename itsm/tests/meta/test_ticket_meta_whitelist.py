# -*- coding: utf-8 -*-
"""工单 meta 白名单单元测试。

覆盖 meta 字段结构收敛的安全约束：
1. 默认键（代码实际读取的字段）通过，未知键静默丢弃，不阻断提单；
2. meta.headers 中的凭据类请求头被过滤，大小写不敏感；
3. callback_url 域名：未登记白名单时默认放行，登记了才按白名单匹配，非法协议拒绝；
4. 环境变量追加（EXTRA）与整体覆盖（OVERRIDE）两种扩展语义。
"""
from unittest import mock

import pytest
from django.test import override_settings
from rest_framework import serializers

from itsm.ticket.serializers.ticket import (
    TICKET_META_DEFAULT_ALLOWED_KEYS,
    TicketSerializer,
    get_ticket_meta_allowed_keys,
)

# 企业内域，未登记白名单时同样放行
SAFE_CALLBACK = "https://bk-itsm.woa.com/api/v1/callback"

DOMAIN_CONTEXT_PATCH = (
    "itsm.meta.services.domain_validate_service.ContextService.get_context_value"
)


@pytest.fixture
def validate_meta():
    """执行 validate_meta，域名白名单读取走 mock，避免依赖数据库。"""

    def _run(meta):
        with mock.patch(DOMAIN_CONTEXT_PATCH, return_value=None):
            return TicketSerializer().validate_meta(meta)

    return _run


class TestDefaultAllowedKeys:
    def test_default_keys_all_preserved(self, validate_meta):
        """默认键（代码实际读取）全部保留，不误伤。"""
        meta = {
            "callback_url": SAFE_CALLBACK,
            "headers": {"X-Token": "abc"},
            "ticket_agent": "tester",
            "ticket_status": {"type": "custom"},
            "notify_config": {"enable_follow_notify": False},
            "state_processors": {"1": "user1"},
            "envs": {"env": "prod"},
            "priority": {"key": "1", "name": "高"},
        }
        assert validate_meta(dict(meta)) == meta

    def test_get_allowed_keys_returns_defaults(self):
        """未配置环境变量时返回 8 个默认键。"""
        assert get_ticket_meta_allowed_keys() == tuple(TICKET_META_DEFAULT_ALLOWED_KEYS)

    def test_extra_keys_deduplicated(self):
        """追加键与默认键重复时不产生重复项。"""
        with override_settings(TICKET_META_EXTRA_ALLOWED_KEYS=("headers", "ext_key")):
            keys = get_ticket_meta_allowed_keys()
        assert len(keys) == len(set(keys))
        assert keys.count("headers") == 1
        assert "ext_key" in keys


class TestUnknownKeysDropped:
    def test_unknown_keys_dropped(self, validate_meta):
        """未知键静默丢弃：线上存在 call_back_url/token/reason 等拼错或无用键。"""
        result = validate_meta(
            {
                "callback_url": SAFE_CALLBACK,
                "call_back_url": "https://x.woa.com/cb",
                "token": "wb_session_xxx",
                "reason": "whatever",
                "task_pipeline_id": 123,
            }
        )
        assert result == {"callback_url": SAFE_CALLBACK}

    def test_unknown_key_dropped_does_not_raise(self, validate_meta):
        """丢弃未知键不抛 ValidationError：不得阻断提单主流程。"""
        result = validate_meta({"unknown_key": "v"})
        assert result == {}

    def test_empty_meta(self, validate_meta):
        """空值不报错。"""
        assert validate_meta({}) == {}
        assert validate_meta(None) == {}


class TestForbiddenHeaders:
    def test_credential_headers_filtered(self, validate_meta):
        """凭据类请求头被过滤：避免 ITSM 携带自身凭据请求外部地址。"""
        result = validate_meta(
            {
                "headers": {
                    "Authorization": "Bearer xxx",
                    "Proxy-Authorization": "Basic xxx",
                    "Cookie": "sessionid=1",
                    "Set-Cookie": "a=b",
                    "Host": "evil.com",
                    "Content-Length": "100",
                    "Transfer-Encoding": "chunked",
                    "X-Token": "keep-me",
                }
            }
        )
        assert result["headers"] == {"X-Token": "keep-me"}

    def test_header_filter_case_insensitive(self, validate_meta):
        """大小写变形不得绕过过滤。"""
        result = validate_meta(
            {"headers": {"AUTHORIZATION": "x", "authorization": "y", "CoOkIe": "z"}}
        )
        assert result["headers"] == {}

    def test_all_headers_filtered_leave_empty_dict(self, validate_meta):
        """全部被过滤时 headers 保留为空字典，不残留键。"""
        result = validate_meta({"headers": {"Authorization": "x"}})
        assert result == {"headers": {}}

    def test_headers_not_dict_no_crash(self, validate_meta):
        """headers 非字典（脏数据）时不得抛异常。"""
        assert validate_meta({"headers": "not-a-dict"}) == {"headers": "not-a-dict"}


class TestCallbackUrlWellformed:
    """URL 规范性防护：只校验 URL 本身，不限制 host（内网 IP 同样放行）。"""

    @pytest.mark.parametrize(
        "url,desc",
        [
            ("https://a.com/cb?x=1\r\nX-Injected: 1", "CRLF 注入"),
            ("https://a.com/cb?x=1\nSet-Cookie: a=b", "换行注入"),
            ("https://a.com/c b", "含空格"),
            ("http://user:pwd@a.com/cb", "携带凭据"),
            ("file:///etc/passwd", "非法协议"),
            ("javascript:alert(1)", "脚本协议"),
            ("http://", "空 host"),
            ("https://" + "a" * 2048 + ".com/cb", "超长 URL"),
        ],
    )
    def test_malformed_url_rejected(self, validate_meta, url, desc):
        with pytest.raises(serializers.ValidationError):
            validate_meta({"callback_url": url})

    @pytest.mark.parametrize(
        "url",
        [
            "http://10.12.34.56/callback",
            "http://127.0.0.1:8080/callback",
            "http://169.254.169.254/latest/meta-data/",
        ],
    )
    def test_host_not_restricted(self, validate_meta, url):
        """host 不做限制：内网/回环/元数据地址同样放行（仅记录，由网络侧管控）。"""
        assert validate_meta({"callback_url": url}) == {"callback_url": url}

    def test_normal_url_passed(self, validate_meta):
        assert validate_meta({"callback_url": SAFE_CALLBACK}) == {
            "callback_url": SAFE_CALLBACK
        }


class TestCallbackUrlDomain:
    """域名不做限制：未登记白名单时默认放行，登记了才按白名单匹配。"""

    def test_unregistered_domain_allowed_by_default(self, validate_meta):
        """未配置白名单：任意 http(s) 域名放行。"""
        url = "https://partner.example.com/callback"
        assert validate_meta({"callback_url": url}) == {"callback_url": url}

    def test_non_http_scheme_rejected(self, validate_meta):
        """非 http/https 协议仍然拒绝。"""
        with pytest.raises(serializers.ValidationError):
            validate_meta({"callback_url": "file:///etc/passwd"})

    def test_safe_domain_kept(self, validate_meta):
        """企业内域回调保留。"""
        assert validate_meta({"callback_url": SAFE_CALLBACK}) == {
            "callback_url": SAFE_CALLBACK
        }

    def test_whitelist_still_enforced_when_configured(self):
        """登记了白名单时仍按白名单匹配（既有能力不受影响）。"""

        def _run(meta):
            with mock.patch(DOMAIN_CONTEXT_PATCH, return_value=r"partner\.example\.com"):
                return TicketSerializer().validate_meta(meta)

        url = "https://partner.example.com/callback"
        assert _run({"callback_url": url}) == {"callback_url": url}
        with pytest.raises(serializers.ValidationError):
            _run({"callback_url": "https://evil.com/callback"})


class TestEnvVarExtension:
    def test_extra_appends_to_defaults(self, validate_meta):
        """EXTRA 追加：默认键依然生效。"""
        with override_settings(TICKET_META_EXTRA_ALLOWED_KEYS=("ext_key",)):
            result = validate_meta({"ext_key": "v", "notify_config": {"a": 1}})
        assert result == {"ext_key": "v", "notify_config": {"a": 1}}

    def test_override_replaces_defaults(self, validate_meta):
        """OVERRIDE 覆盖：默认键不在新白名单内时同样被丢弃。"""
        with override_settings(TICKET_META_ALLOWED_KEYS_OVERRIDE=("only_a",)):
            result = validate_meta({"only_a": "v", "notify_config": {"a": 1}})
        assert result == {"only_a": "v"}

    def test_override_takes_precedence_over_extra(self, validate_meta):
        """两个变量同时配置时 OVERRIDE 优先。"""
        with override_settings(
            TICKET_META_ALLOWED_KEYS_OVERRIDE=("only_a",),
            TICKET_META_EXTRA_ALLOWED_KEYS=("ext_key",),
        ):
            result = validate_meta({"only_a": "v", "ext_key": "v"})
        assert result == {"only_a": "v"}
