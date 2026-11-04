# -*- coding: utf-8 -*-
"""工单回调地址域名白名单回归测试。

覆盖 C-01 修复项：回调域名白名单未配置时默认拒绝（fail-close），
Postman 等内网场景保持原有放行语义。
"""

import mock
from django.test import TestCase

from itsm.meta.services.domain_validate_service import DomainValidateService
from itsm.ticket.models import Ticket

CONTEXT_PATCH = (
    "itsm.meta.services.domain_validate_service.ContextService.get_context_value"
)


class CallbackDomainWhitelistTest(TestCase):
    def _service(self, patterns):
        with mock.patch(CONTEXT_PATCH, return_value=patterns):
            return DomainValidateService(key="valid_callback_domain_regex_pattern")

    def test_empty_whitelist_rejects_by_default(self):
        service = self._service(None)
        self.assertFalse(
            service.is_safe_url("https://evil.example.com/cb", fail_open=False)
        )
        self.assertFalse(
            service.is_safe_url("http://127.0.0.1:8080/cb", fail_open=False)
        )
        self.assertFalse(service.is_safe_url("http://10.0.0.1/cb", fail_open=False))

    def test_empty_whitelist_keeps_fail_open_for_internal_api(self):
        service = self._service("")
        self.assertTrue(service.is_safe_url("http://10.0.0.1/api", fail_open=True))

    def test_whitelist_hit(self):
        service = self._service(r"^allowed\.example\.com$")
        self.assertTrue(
            service.is_safe_url("https://allowed.example.com/cb", fail_open=False)
        )

    def test_whitelist_miss(self):
        service = self._service(r"^allowed\.example\.com$")
        self.assertFalse(
            service.is_safe_url(
                "https://allowed.example.com.evil.com/cb", fail_open=False
            )
        )
        self.assertFalse(
            service.is_safe_url("http://127.0.0.1/cb", fail_open=False)
        )

    def test_multiple_patterns_separated_by_comma(self):
        service = self._service(r"^a\.example\.com$,^b\.example\.com$")
        self.assertTrue(service.is_safe_url("https://a.example.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://b.example.com/cb", fail_open=False))
        self.assertFalse(service.is_safe_url("https://c.example.com/cb", fail_open=False))

    def test_multiple_patterns_separated_by_semicolon(self):
        """存量配置用分号分隔，保持兼容。"""
        service = self._service(r"^a\.example\.com$;^b\.example\.com$")
        self.assertTrue(service.is_safe_url("https://a.example.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://b.example.com/cb", fail_open=False))

    def test_multiple_patterns_separated_by_newline(self):
        service = self._service("^a\\.example\\.com$\n^b\\.example\\.com$")
        self.assertTrue(service.is_safe_url("https://a.example.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://b.example.com/cb", fail_open=False))

    def test_mixed_separators_ignore_blank_items(self):
        service = self._service("^a\\.example\\.com$ , ;\n ^b\\.example\\.com$,")
        self.assertEqual(len(service.allow_patterns), 2)

    def test_comma_in_quantifier_not_split(self):
        """正则量词 {2,3} 内的逗号不得作为分隔符。"""
        service = self._service(r"^a{2,3}\.example\.com$")
        self.assertEqual([p.pattern for p in service.allow_patterns], [r"^a{2,3}\.example\.com$"])
        self.assertTrue(service.is_safe_url("https://aa.example.com/cb", fail_open=False))

    def test_comma_in_character_class_not_split(self):
        """字符类 [^,] 内的逗号不得作为分隔符。"""
        service = self._service(r"^[^,]\.example\.com$,^b\.example\.com$")
        self.assertEqual(len(service.allow_patterns), 2)
        self.assertTrue(service.is_safe_url("https://a.example.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://b.example.com/cb", fail_open=False))

    def test_wildcard_suffix_syntax(self):
        """`*.woa.com` 通配符写法自动转正则，等价放行任意子域。"""
        service = self._service(r"*.woa.com,*.oa.com")
        self.assertTrue(service.is_safe_url("https://iam.woa.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://a.b.woa.com/cb", fail_open=False))
        self.assertTrue(service.is_safe_url("https://x.y.oa.com/cb", fail_open=False))
        self.assertFalse(
            service.is_safe_url("https://woa.com.evil.com/cb", fail_open=False)
        )
        self.assertFalse(service.is_safe_url("https://www.baidu.com/cb", fail_open=False))

    def test_star_regex_not_misinterpreted_as_wildcard(self):
        """含 * 的正则写法不得被当成通配符改写。"""
        service = self._service(r"^a.*\.example\.com$")
        self.assertTrue(service.is_safe_url("https://ab.example.com/cb", fail_open=False))
        self.assertFalse(service.is_safe_url("https://x.example.com/cb", fail_open=False))

    def test_invalid_scheme_rejected(self):
        service = self._service(None)
        self.assertFalse(service.is_safe_url("file:///etc/passwd", fail_open=False))


class TicketCallbackRejectTest(TestCase):
    """白名单为空时，回调外发不应发出任何请求。"""

    def setUp(self):
        Ticket.objects.all().delete()
        self.ticket = Ticket.objects.create(
            sn="SN-CALLBACK-EMPTY-WHITELIST",
            title="callback",
            service_id=1,
            service_type="request",
            creator="admin",
            current_status="RUNNING",
            is_draft=False,
            meta={"callback_url": "https://evil.example.com/cb"},
        )

    def tearDown(self):
        Ticket.objects.all().delete()

    @mock.patch(CONTEXT_PATCH, return_value=None)
    @mock.patch("itsm.ticket.models.ticket.requests.session")
    def test_callback_blocked_when_whitelist_empty(self, session, _context):
        self.ticket.callback_request()
        session.assert_not_called()
