# -*- coding: utf-8 -*-
from unittest import mock

from django.test import RequestFactory, SimpleTestCase

from weixin.core import accounts


class GetSafeCallbackUrlTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.fallback_url = "/t/bk_itsm/weixin/"
        self.external_host = "wx.example.com"

        patch_site_url = mock.patch.object(
            accounts.weixin_settings,
            "WEIXIN_SITE_URL",
            self.fallback_url,
        )
        patch_external_host = mock.patch.object(
            accounts.weixin_settings,
            "WEIXIN_APP_EXTERNAL_HOST",
            self.external_host,
        )

        patch_site_url.start()
        patch_external_host.start()
        self.addCleanup(patch_site_url.stop)
        self.addCleanup(patch_external_host.stop)

    def make_request(self, host="wx.example.com"):
        return self.factory.get("/weixin/login/", HTTP_HOST=host)

    def test_should_fallback_when_callback_url_is_empty(self):
        request = self.make_request()
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, ""),
            self.fallback_url,
        )
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, None),
            self.fallback_url,
        )

    def test_should_allow_relative_path(self):
        request = self.make_request()
        callback_url = "/t/bk_itsm/weixin/api/ticket/receipts/"
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, callback_url),
            callback_url,
        )

    def test_should_block_protocol_relative_url(self):
        request = self.make_request()
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, "//evil.com/path"),
            self.fallback_url,
        )

    def test_should_block_non_slash_relative_value(self):
        request = self.make_request()
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, "evil.com/path"),
            self.fallback_url,
        )

    def test_should_allow_absolute_url_when_host_is_external_host(self):
        request = self.make_request()
        callback_url = "https://wx.example.com/t/bk_itsm/weixin/"
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, callback_url),
            callback_url,
        )

    def test_should_allow_absolute_url_when_host_matches_request_host_without_port(self):
        request = self.make_request(host="test.example.com:8443")
        callback_url = "https://test.example.com/t/bk_itsm/weixin/"
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(request, callback_url),
            callback_url,
        )

    def test_should_block_absolute_url_when_host_not_allowed(self):
        request = self.make_request()
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(
                request,
                "https://evil.com/t/bk_itsm/weixin/",
            ),
            self.fallback_url,
        )

    def test_should_block_non_http_scheme(self):
        request = self.make_request()
        self.assertEqual(
            accounts.WeixinAccount.get_safe_callback_url(
                request,
                "javascript:alert(1)",
            ),
            self.fallback_url,
        )
