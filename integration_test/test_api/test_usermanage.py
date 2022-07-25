# -*- coding: utf-8 -*-
"""
用户管理集成测试模块
"""
from unittest import TestCase

from django.conf import settings
from django.test import override_settings

adapter_api = settings.ADAPTER_API


class UserManagerApi(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_bk_users(self):
        result = adapter_api.get_all_users(["admin"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "admin")
        self.assertEqual(result[0]["bk_username"], "admin")
