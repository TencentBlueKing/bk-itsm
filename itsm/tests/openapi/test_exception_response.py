# -*- coding: utf-8 -*-
"""OpenAPI 保留已有校验异常的具体原因，不访问数据库和流程引擎。"""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from itsm.component.drf.exception import ValidationError as CustomValidationError
from itsm.component.exceptions import OperateTicketError
from itsm.openapi.decorators import catch_openapi_exception
from itsm.openapi.ticket.validators import openapi_operate_validate


@override_settings(LANGUAGE_CODE="zh-hans")
class OpenApiExceptionTest(SimpleTestCase):
    def test_native_and_custom_validation_errors_keep_their_message(self):
        for error_type in (ValidationError, CustomValidationError):
            with self.subTest(error_type=error_type):

                @catch_openapi_exception
                def endpoint(view, request):
                    raise error_type("单据已关闭，无法操作")

                with patch("itsm.openapi.decorators.logger") as logger:
                    response = endpoint(None, None)

                self.assertFalse(response.data["result"])
                self.assertEqual(response.data["code"], 3900005)
                self.assertIsNone(response.data["data"])
                self.assertIn("单据已关闭，无法操作", response.data["message"])
                logger.exception.assert_not_called()

    def test_field_validation_error_keeps_field_name_and_reason(self):
        @catch_openapi_exception
        def endpoint(view, request):
            raise ValidationError({"operator": ["该字段是必填项。"]})

        response = endpoint(None, None)
        self.assertFalse(response.data["result"])
        self.assertEqual(response.data["code"], 3900005)
        self.assertEqual(response.data["message"], "operator:该字段是必填项。")

    def test_existing_node_validation_errors_keep_their_reason(self):
        for node_status, can_operate, message in (
            ("FINISHED", False, "抱歉，当前节点：3642 已经结束"),
            ("RUNNING", False, "抱歉，alice不能操作该节点（没有权限或操作类型不支持）"),
        ):
            with self.subTest(node_status=node_status):
                status = Mock(status=node_status)
                status.can_operate.return_value = can_operate
                ticket = Mock(is_over=False, is_slave=False)
                ticket.status.return_value = status

                @catch_openapi_exception
                def endpoint(view, request):
                    openapi_operate_validate("alice", ticket, 3642, "TRANSITION")

                with patch("itsm.openapi.decorators.logger") as logger:
                    response = endpoint(None, None)

                self.assertFalse(response.data["result"])
                self.assertEqual(response.data["code"], 3900005)
                self.assertIn(message, response.data["message"])
                logger.exception.assert_not_called()

    def test_business_error_keeps_its_existing_response(self):
        error = OperateTicketError("callback failed")

        @catch_openapi_exception
        def endpoint(view, request):
            raise error

        response = endpoint(None, None)
        self.assertEqual(
            response.data,
            {"result": False, "code": error.code_int, "data": None, "message": error.message},
        )

    def test_unexpected_error_is_logged_without_exposing_details(self):
        @catch_openapi_exception
        def endpoint(view, request):
            raise RuntimeError("internal database details")

        with patch("itsm.openapi.decorators.logger") as logger:
            response = endpoint(None, None)

        self.assertEqual(
            response.data,
            {
                "result": False,
                "code": 3900004,
                "data": None,
                "message": "接口异常，请检查请求参数后重试",
            },
        )
        logger.exception.assert_called_once_with("openapi unexpected error")

    def test_success_response_is_unchanged(self):
        response = Response({"ok": True})

        @catch_openapi_exception
        def endpoint(view, request):
            return response

        self.assertIs(endpoint(None, None), response)
