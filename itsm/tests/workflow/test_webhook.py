# -*- coding: utf-8 -*-
import json

import mock
from django.test import SimpleTestCase, TestCase, override_settings
from pipeline.utils.boolrule import MissingVariableException
from requests import Response
from requests.exceptions import JSONDecodeError, Timeout

from itsm.component.constants import NODE_FAILED
from itsm.component.constants.trigger import SOURCE_TICKET, STATE_FAILED
from itsm.meta.services.webhook_url_validate_service import WebhookURLValidateService
from itsm.pipeline_plugins.components.collections.webhook import (
    WebHookService,
    ParamsBuilder,
)
from itsm.service.models import CatalogService
from itsm.ticket.models import SYSTEM_OPERATE, Ticket
from itsm.trigger.models import ActionSchema, Trigger, TriggerRule
from blueapps.core.celery.celery import app
from pipeline.core.data.base import DataObject


class PipelineTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()
        self.ticket_id = self.create_ticket()
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def create_ticket(self):
        CatalogService.objects.create(
            service_id=1, is_deleted=False, catalog_id=2, creator="admin"
        )
        data = {
            "catalog_id": 3,
            "service_id": 1,
            "service_type": "request",
            "fields": [
                {
                    "type": "STRING",
                    "id": 1,
                    "key": "title",
                    "value": "test_ticket",
                    "choice": [],
                },
                {
                    "type": "STRING",
                    "id": 5,
                    "key": "apply_content",
                    "value": "测试内容",
                },
                {
                    "type": "STRING",
                    "key": "ZHIDINGSHENPIREN",
                    "value": "test",
                },
                {
                    "type": "STRING",
                    "key": "apply_reason",
                    "value": "test",
                },
            ],
            "creator": "admin",
            "attention": True,
        }
        url = "/api/ticket/receipts/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        data = json.loads(rsp.content.decode("utf-8"))
        return data["data"]["id"]

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook.WebHookService.build_params"
    )
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook.Ticket.do_before_enter_state"
    )
    @mock.patch(
        "itsm.meta.services.webhook_url_validate_service.ContextService.get_context_value"
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_excute(
        self, request, get_context_value, do_before_enter_state, build_params
    ):
        extras = {
            "method": "GET",
            "url": "https://api.example.com/",
            "query_params": [
                {"key": "bk_app_code", "value": "itsm"},
            ],
            "headers": [],
            "body": {"type": "form_data", "params": [], "raw_type": "", "content": ""},
            "settings": {"timeout": 10},
            "success_exp": "",
        }

        get_context_value.return_value = "api.example.com,*.example.com"
        build_params.return_value = extras
        do_before_enter_state.return_value = None

        response = Response()
        response.status_code = 200
        response._content = b"{}"
        response.json()
        request.return_value = response

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        auto_service = WebHookService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)
        self.assertEqual(request.call_args.kwargs["allow_redirects"], False)

    @mock.patch(
        "itsm.meta.services.webhook_url_validate_service.ContextService.get_context_value"
    )
    def test_webhook_url_validate_service_for_config(self, get_context_value):
        get_context_value.return_value = "api.example.com,*.example.com"

        WebhookURLValidateService.validate_for_config(
            "https://api.example.com/webhook"
        )
        WebhookURLValidateService.validate_for_config("{{ URL }}")

        with self.assertRaises(ValueError):
            WebhookURLValidateService.validate_for_config(
                "https://not-allowed.example.org/webhook"
            )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_params_builder(self):
        extras = {
            "method": "GET",
            "url": "{{URL}}",
            "query_params": [
                {"key": "bk_app_code", "value": "itsm"},
                {"key": "bk_app_secret", "value": "{{bk_app_secret}}"},
                {"key": "bk_username", "value": "admin"},
            ],
            "headers": [],
            "body": {"type": "form_data", "params": [], "raw_type": "", "content": ""},
            "settings": {"timeout": 10},
            "success_exp": "",
        }
        key_value = {
            "URL": "http://127.0.0.1",
            "bk_app_secret": "123456789",
        }
        result = ParamsBuilder(extras, key_value).result()
        self.assertEqual(result["url"], "http://127.0.0.1")
        self.assertEqual(result["query_params"]["bk_app_secret"], "123456789")


class WebHookServiceUnitTest(SimpleTestCase):
    def setUp(self):
        self.service = WebHookService(name="itsm")
        self.service._runtime_attrs = {"by_flow": 1}
        self.service.build_params = mock.Mock(return_value=self.webhook_extras())
        self.service.update_info = mock.Mock()
        self.service.validate_webhook_url = mock.Mock()
        self.service.validate_success_exp = mock.Mock()
        self.service.update_variables = mock.Mock(return_value=[])
        sleep_patcher = mock.patch(
            "itsm.pipeline_plugins.components.collections.webhook.time.sleep"
        )
        self.sleep = sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)

        self.current_node = mock.MagicMock()
        self.current_node.query_params = {"url": "https://api.example.com/"}
        self.current_node.name = "test webhook"

        self.ticket = mock.MagicMock()
        self.ticket.current_processors = "[admin]"
        self.ticket.flow.get_state.return_value = {
            "variables": {"outputs": []},
            "extras": {},
        }
        self.ticket.node_status.get.return_value = self.current_node
        self.ticket.get_output_fields.return_value = []

        self.execute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        self.execute_parent_data = DataObject(
            inputs={"ticket_id": 1}, outputs={"is_first_execute": False}
        )

    @staticmethod
    def webhook_extras():
        return {
            "method": "GET",
            "url": "https://api.example.com/",
            "query_params": {},
            "headers": {},
            "body": {"content": ""},
            "settings": {"timeout": 10},
            "success_exp": "",
            "auth": {},
        }

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_marks_timeout_as_retryable(self, request):
        request.side_effect = Timeout("request timeout")
        self.service.record_webhook_error = mock.Mock(
            return_value="Webhook请求失败"
        )

        result = self.service.request_once(
            "GET",
            "https://api.example.com/",
            "",
            {},
            {},
            10,
            None,
            "",
        )

        self.assertEqual(result[:4], (False, None, "Webhook请求失败", True))
        self.assertTrue(result[4])

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_marks_timeout_as_retryable_for_post(self, request):
        """当前口径：不区分请求方法，POST 的网络层异常同样可重试。"""
        request.side_effect = Timeout("request timeout")
        self.service.record_webhook_error = mock.Mock(
            return_value="Webhook请求失败"
        )

        result = self.service.request_once(
            "POST", "https://api.example.com/", "", {}, {}, 10, None, ""
        )

        self.assertEqual(result[:4], (False, None, "Webhook请求失败", True))
        self.assertTrue(result[4])

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_rejects_non_success_status(self, request):
        response = mock.Mock(status_code=400)
        request.return_value = response
        self.service.record_webhook_error = mock.Mock(
            return_value="返回状态码非200/201, status_code=400"
        )

        result = self.service.request_once(
            "GET", "https://api.example.com/", "", {}, {}, 10, None, ""
        )

        self.assertEqual(
            result[:4],
            (False, None, "返回状态码非200/201, status_code=400", False),
        )

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_rejects_non_json_response(self, request):
        response = mock.Mock(status_code=200)
        response.json.side_effect = JSONDecodeError("invalid json", "", 0)
        request.return_value = response
        self.service.record_webhook_error = mock.Mock(return_value="返回值非Json")

        result = self.service.request_once(
            "GET", "https://api.example.com/", "", {}, {}, 10, None, ""
        )

        self.assertEqual(result[:4], (False, None, "返回值非Json", False))

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_rejects_invalid_request_params(self, request):
        self.service.record_webhook_error = mock.Mock(return_value="x")

        result = self.service.request_once(
            "GET", "https://api.example.com/", "", {}, {}, "invalid", None, ""
        )

        # 非法的 timeout 应被准确归因，而不是笼统的“参数构建失败”
        self.assertEqual(
            self.service.record_webhook_error.call_args[0][0],
            "Webhook超时时间参数非法：invalid",
        )
        self.assertFalse(result[3])
        request.assert_not_called()

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.BoolRule")
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_rejects_failed_success_condition(self, request, bool_rule):
        response = mock.Mock(status_code=200)
        response.json.return_value = {"result": False}
        request.return_value = response
        bool_rule.return_value.test.return_value = False
        self.service.record_webhook_error = mock.Mock(
            return_value="请求成功判定失败，返回值不满足条件"
        )

        result = self.service.request_once(
            "GET",
            "https://api.example.com/",
            "",
            {},
            {},
            10,
            None,
            "resp.result == true",
        )

        self.assertEqual(
            result[:4],
            (False, None, "请求成功判定失败，返回值不满足条件", False),
        )

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.BoolRule")
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_rejects_missing_success_field(self, request, bool_rule):
        response = mock.Mock(status_code=200)
        response.json.return_value = {}
        request.return_value = response
        bool_rule.return_value.test.side_effect = MissingVariableException(
            "missing resp.result"
        )
        self.service.record_webhook_error = mock.Mock(
            return_value="请求成功判定失败，返回值不满足条件"
        )

        result = self.service.request_once(
            "GET",
            "https://api.example.com/",
            "",
            {},
            {},
            10,
            None,
            "resp.result == true",
        )

        self.assertEqual(
            result[:4],
            (False, None, "请求成功判定失败，返回值不满足条件", False),
        )

    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.BoolRule")
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.requests.request")
    def test_request_once_catches_unexpected_exception(self, request, bool_rule):
        """未预期异常不允许逃逸 request_once，统一按不可重试失败处理。"""
        response = mock.Mock(status_code=200)
        response.json.return_value = {"result": True}
        request.return_value = response
        bool_rule.return_value.test.side_effect = RuntimeError("boom")
        self.service.record_webhook_error = mock.Mock(return_value="x")

        result = self.service.request_once(
            "GET",
            "https://api.example.com/",
            "",
            {},
            {},
            10,
            None,
            "resp.result == true",
        )

        self.assertFalse(result[0])
        self.assertFalse(result[3])
        self.assertTrue(result[4])

    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_base_service."
        "ItsmBaseService.execute",
        return_value=False,
    )
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook."
        "EncodeWebhook.encode_authorization",
        return_value=None,
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.Ticket.objects.get")
    def test_execute_retries_on_retryable_error_then_succeeds(
        self, ticket_get, encode_authorization, base_execute
    ):
        ticket_get.return_value = self.ticket
        self.service.request_once = mock.Mock(
            side_effect=[
                (False, None, "first timeout", True, "traceback-1"),
                (False, None, "second timeout", True, "traceback-2"),
                (True, {}, "", False, ""),
            ]
        )
        self.service.do_exit_plugins = mock.Mock()

        result = self.service.execute(self.execute_data, self.execute_parent_data)

        self.assertTrue(result)
        self.assertEqual(self.service.request_once.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [mock.call(1), mock.call(1)])
        self.service.do_exit_plugins.assert_not_called()
        self.current_node.create_action_log.assert_has_calls(
            [
                mock.call(
                    "system",
                    "WebHook任务【test webhook】第1次重试",
                    detail_message="first timeout",
                    source=SYSTEM_OPERATE,
                    action_type=SYSTEM_OPERATE,
                ),
                mock.call(
                    "system",
                    "WebHook任务【test webhook】第2次重试",
                    detail_message="second timeout",
                    source=SYSTEM_OPERATE,
                    action_type=SYSTEM_OPERATE,
                ),
            ]
        )
        # 成功轮不再用空值覆盖 webhook_last_error，保留"曾失败过"的痕迹
        self.assertIn(
            mock.call(self.current_node, webhook_attempt_count=3),
            self.service.update_info.call_args_list,
        )
        self.assertNotIn(
            mock.call(
                self.current_node, webhook_attempt_count=3, webhook_last_error=""
            ),
            self.service.update_info.call_args_list,
        )

    @mock.patch(
        "itsm.pipeline_plugins.components.collections.itsm_base_service."
        "ItsmBaseService.execute",
        return_value=False,
    )
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.webhook."
        "EncodeWebhook.encode_authorization",
        return_value=None,
    )
    @mock.patch("itsm.pipeline_plugins.components.collections.webhook.Ticket.objects.get")
    def test_execute_sends_failed_signal_after_retries_exhausted(
        self, ticket_get, encode_authorization, base_execute
    ):
        ticket_get.return_value = self.ticket
        self.service.has_enabled_failure_trigger = mock.Mock(return_value=True)
        self.service.request_once = mock.Mock(
            return_value=(False, None, "Webhook请求失败", True, "traceback-text")
        )

        result = self.service.execute(self.execute_data, self.execute_parent_data)

        self.assertFalse(result)
        self.assertEqual(self.service.request_once.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [mock.call(1), mock.call(1)])
        self.ticket.send_trigger_signal.assert_called_once_with(
            STATE_FAILED,
            sender="2",
            context={
                "webhook_attempt_count": 3,
                "webhook_failure_reason": "Webhook请求失败",
            },
        )
        self.ticket.notify.assert_not_called()
        self.current_node.set_failed_status.assert_called_once_with(
            operator="admin",
            message="WebHook任务【{name}】执行失败，失败信息 {detail_message}",
            detail_message="Webhook请求失败",
        )

    def test_failure_uses_default_notification_without_trigger(self):
        self.service.has_enabled_failure_trigger = mock.Mock(return_value=False)

        self.service.do_exit_plugins(
            self.ticket,
            "2",
            self.current_node,
            "Webhook请求失败",
            "WebHook任务【{name}】执行失败，失败信息 {detail_message}",
            "admin",
            attempts=3,
        )

        self.ticket.send_trigger_signal.assert_not_called()
        self.ticket.notify.assert_called_once_with(
            state_id="2",
            receivers="admin",
            message="WebHook任务【test webhook】执行失败，失败信息 Webhook请求失败",
            action=NODE_FAILED,
            retry=False,
        )


class HasEnabledFailureTriggerTest(SimpleTestCase):
    """第 1 项：只有恒真条件 + 后台动作的触发器才视为会通知。

    否则回退默认通知给处理人。
    """

    def setUp(self):
        self.ticket = mock.MagicMock()
        self.ticket.id = 1
        self.ticket.flow.id = 99
        switch_patcher = mock.patch(
            "itsm.iadmin.utils.is_trigger_switch_off", return_value=False
        )
        self.switch = switch_patcher.start()
        self.addCleanup(switch_patcher.stop)

    @staticmethod
    def _rule(by_condition, action_schemas):
        return mock.Mock(by_condition=by_condition, action_schemas=action_schemas)

    def _check(self, trigger_ids, rules, has_backend_action):
        trigger_queryset = mock.MagicMock()
        trigger_queryset.values_list.return_value = trigger_ids

        trigger_manager = mock.MagicMock()
        trigger_manager.filter.return_value = trigger_queryset

        # 模拟 ORM 的 by_condition 过滤，避免桩把所有规则都返回
        def rule_filter(**kwargs):
            by_condition = kwargs.get("by_condition")
            if by_condition is None:
                return rules
            return [rule for rule in rules if rule.by_condition == by_condition]

        rule_manager = mock.MagicMock()
        rule_manager.filter.side_effect = rule_filter

        action_manager = mock.MagicMock()
        action_manager.filter.return_value.exists.return_value = has_backend_action

        self.trigger_manager = trigger_manager
        self.rule_manager = rule_manager

        with mock.patch.object(Trigger, "objects", trigger_manager), mock.patch.object(
            TriggerRule, "objects", rule_manager
        ), mock.patch.object(ActionSchema, "objects", action_manager):
            return WebHookService.has_enabled_failure_trigger(self.ticket, "2")

    def test_returns_false_without_trigger(self):
        self.assertFalse(self._check([], [], True))

    def test_returns_true_with_unconditional_backend_rule(self):
        self.assertTrue(self._check([7], [self._rule(False, [11])], True))

    def test_returns_false_when_rule_has_condition(self):
        # 触发器存在但规则带条件，不保证触发，必须回退默认通知
        self.assertFalse(self._check([7], [self._rule(True, [11])], True))

    def test_queries_only_unconditional_rules(self):
        # 契约：只查询恒真条件（by_condition=False）的规则
        self._check([7], [self._rule(False, [11])], True)
        self.rule_manager.filter.assert_called_once_with(
            trigger_id__in=[7], by_condition=False
        )

    def test_trigger_query_scope(self):
        # 契约：只匹配当前版本、当前节点、启用且非草稿的 STATE_FAILED 触发器
        self._check([7], [self._rule(False, [11])], True)
        self.trigger_manager.filter.assert_called_once_with(
            signal=STATE_FAILED,
            sender="2",
            source_type=SOURCE_TICKET,
            source_id=99,
            is_enabled=True,
            is_draft=False,
        )

    def test_returns_false_without_backend_action(self):
        # 动作是手动执行，不会自动通知，必须回退默认通知
        self.assertFalse(self._check([7], [self._rule(False, [11])], False))

    def test_returns_false_without_any_rule(self):
        self.assertFalse(self._check([7], [], True))

    def test_returns_false_when_rule_has_no_action(self):
        self.assertFalse(self._check([7], [self._rule(False, [])], True))

    def test_returns_false_when_trigger_switch_off(self):
        self.switch.return_value = True
        self.assertFalse(self._check([7], [self._rule(False, [11])], True))
