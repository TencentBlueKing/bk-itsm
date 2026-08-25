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
import json
from unittest import mock

from blueapps.conf import settings
from blueapps.core.celery.celery import app
from django.test import TestCase, override_settings
import requests

from blueking.component.open.exceptions import ComponentAPIException
from itsm.pipeline_plugins.components.collections.bk_sops import BkOpsService
from itsm.service.models import CatalogService
from itsm.ticket.models import Ticket
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

    def tearDown(self):
        Ticket.objects.all().delete()
        CatalogService.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.state")
    @mock.patch(
        "itsm.pipeline_plugins.components.collections.bk_sops.Ticket.do_before_enter_state"
    )
    def test_excute(self, do_before_enter_state, state, get_client):
        do_before_enter_state.return_value = None
        state.return_value = {
            "name": "test",
            "extras": {
                "sops_info": {
                    "template_id": 1,
                    "bk_biz_id": {"name": "test", "value_type": "variable", "value": 0},
                    "constants": [
                        {
                            "value": "test",
                            "name": "bkapp_code",
                            "key": "bkapp_code",
                            "value_type": "variable",
                        }
                    ],
                }
            },
        }
        get_client.return_value.sops.create_task.return_value = {
            "result": True,
            "data": {"task_id": 1, "task_url": "http://sops/task/1"},
        }
        get_client.return_value.sops.start_task.return_value = {"result": True}

        print("ticket_id:{}".format(self.ticket_id))

        excute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        result = sops_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)
        ticket = Ticket.objects.get(pk=self.ticket_id)
        current_node = ticket.node_status.get(state_id="2")
        _, expected_operator = sops_service.resolve_operator(current_node)
        self.assertEqual(excute_data.outputs["operator"], expected_operator)
        self.assertEqual(
            get_client.call_args_list,
            [
                mock.call("sops", username=settings.SYSTEM_CALL_USER),
                mock.call("sops", username=settings.SYSTEM_CALL_USER),
            ],
        )
        self.assertEqual(get_client.return_value.sops.create_task.call_count, 1)
        self.assertEqual(get_client.return_value.sops.start_task.call_count, 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    def test_schedule_without_taskid(self, get_client):
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {
                "retry": 0,
                "name": "&lt;class 'pipeline.core.pipeline.Pipeline'&gt;",
                "finish_time": "",
                "skip": False,
                "start_time": "2018-04-26 16:08:34 +0800",
                "children": {},
                "state": "FAILED",
                "version": "",
                "id": "5a1622f9f43e3429acb604e18dbd100a",
                "loop": 1,
            },
        }
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "sops_task_id": "",
                "bk_biz_id": 123,
                "api_info": {},
                "operator": "admin",
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    def test_schedule_false(self, get_client):
        get_client.return_value.sops.get_task_status.return_value = {
            "result": False,
            "data": {},
            "message": "error",
        }
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "sops_task_id": 1,
                "bk_biz_id": 123,
                "api_info": {},
                "operator": "admin",
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    def test_schedule_succeed(self, get_client):
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {
                "retry": 0,
                "name": "&lt;class 'pipeline.core.pipeline.Pipeline'&gt;",
                "finish_time": "",
                "skip": False,
                "start_time": "2018-04-26 16:08:34 +0800",
                "children": {},
                "state": "CREATED",
                "version": "",
                "id": "5a1622f9f43e3429acb604e18dbd100a",
                "loop": 1,
            },
            "message": "error",
        }
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "sops_task_id": 1,
                "bk_biz_id": 123,
                "api_info": {},
                "operator": "admin",
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    def test_schedule_failed(self, get_client):
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {
                "retry": 0,
                "name": "&lt;class 'pipeline.core.pipeline.Pipeline'&gt;",
                "finish_time": "",
                "skip": False,
                "start_time": "2018-04-26 16:08:34 +0800",
                "children": {},
                "state": "FAILED",
                "version": "",
                "id": "5a1622f9f43e3429acb604e18dbd100a",
                "loop": 1,
            },
            "message": "error",
        }
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "sops_task_id": 1,
                "bk_biz_id": 123,
                "api_info": {},
                "operator": "admin",
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, False)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    def test_schedule_finished(self, get_client):
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {
                "retry": 0,
                "name": "&lt;class 'pipeline.core.pipeline.Pipeline'&gt;",
                "finish_time": "",
                "skip": False,
                "start_time": "2018-04-26 16:08:34 +0800",
                "children": {},
                "state": "FINISHED",
                "version": "",
                "id": "5a1622f9f43e3429acb604e18dbd100a",
                "loop": 1,
            },
            "message": "error",
        }
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={
                "sops_task_id": 1,
                "bk_biz_id": 123,
                "api_info": {},
                "operator": "admin",
            },
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )

        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_log_prefix(self):
        """结构化日志前缀：默认不带 sops_task_id，传入则追加"""
        self.assertEqual(BkOpsService._log_prefix(100, 2), "ticket_id=100, state_id=2")
        self.assertEqual(
            BkOpsService._log_prefix(100, 2, 50),
            "ticket_id=100, state_id=2, sops_task_id=50",
        )

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.get_output_fields")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.do_before_enter_state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_execute_uses_processor_operator(
        self, node_status, do_before_enter_state, state, get_output_fields, get_client
    ):
        """execute 成功：create_action_log 记录节点处理人而非 system"""
        do_before_enter_state.return_value = None
        get_output_fields.return_value = {}
        node = mock.Mock()
        node.processors_type = "PERSON"
        node.processors = ",v_ylcnyao,"
        node.name = "测试ITSM发送审批"
        node.query_params = {}
        node_status.get.return_value = node
        state.return_value = {
            "name": "test",
            "extras": {
                "sops_info": {
                    "template_id": 1,
                    "bk_biz_id": {"name": "test", "value_type": "variable", "value": 0},
                    "constants": [],
                }
            },
        }
        get_client.return_value.sops.create_task.return_value = {
            "result": True,
            "data": {"task_id": 1, "task_url": "http://sops/task/1"},
        }
        get_client.return_value.sops.start_task.return_value = {"result": True}

        execute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        execute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        result = sops_service.execute(execute_data, execute_parent_data)
        self.assertEqual(result, True)
        # 自动节点执行动作日志 operator 为 system（系统自动执行），与 ESB 时代一致
        node.create_action_log.assert_called_once()
        self.assertEqual(node.create_action_log.call_args[0][0], "system")
        # 节点执行人仍通过 processors/outputs 保留，用于失败通知
        self.assertEqual(execute_data.outputs.get("operator"), "v_ylcnyao")
        # SOPS 调用统一按系统身份（SYSTEM_CALL_USER）建 client
        get_client.assert_any_call("sops", username=settings.SYSTEM_CALL_USER)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(BkOpsService, "do_exit_plugins")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.get_output_fields")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.do_before_enter_state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_execute_no_processor(
        self, node_status, do_before_enter_state, state, get_output_fields, get_client, do_exit_plugins
    ):
        """未配置处理人：仍照常执行（admin 兜底），不进入失败流程"""
        do_before_enter_state.return_value = None
        get_output_fields.return_value = {}
        node = mock.Mock()
        node.processors_type = "PERSON"
        node.processors = ""
        node.name = "测试ITSM发送审批"
        node.query_params = {}
        node_status.get.return_value = node
        state.return_value = {
            "name": "test",
            "extras": {
                "sops_info": {
                    "template_id": 1,
                    "bk_biz_id": {"name": "test", "value_type": "variable", "value": 0},
                    "constants": [],
                }
            },
        }
        get_client.return_value.sops.create_task.return_value = {
            "result": True,
            "data": {"task_id": 1, "task_url": "http://sops/task/1"},
        }
        get_client.return_value.sops.start_task.return_value = {"result": True}

        execute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        execute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        result = sops_service.execute(execute_data, execute_parent_data)
        self.assertEqual(result, True)
        do_exit_plugins.assert_not_called()
        get_client.return_value.sops.create_task.assert_called_once()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(BkOpsService, "do_exit_plugins")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.get_output_fields")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.do_before_enter_state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_execute_processor_resolve_error(
        self, node_status, do_before_enter_state, state, get_output_fields, get_client, do_exit_plugins
    ):
        """处理人解析接口异常：降级为空仍照常执行（admin 兜底），不抛异常"""
        do_before_enter_state.return_value = None
        get_output_fields.return_value = {}
        node = mock.Mock()
        node.processors_type = "GENERAL"
        node.processors = ""
        node.name = "测试ITSM发送审批"
        node.query_params = {}
        node.get_user_list.side_effect = Exception("user api error")
        node_status.get.return_value = node
        state.return_value = {
            "name": "test",
            "extras": {
                "sops_info": {
                    "template_id": 1,
                    "bk_biz_id": {"name": "test", "value_type": "variable", "value": 0},
                    "constants": [],
                }
            },
        }
        get_client.return_value.sops.create_task.return_value = {
            "result": True,
            "data": {"task_id": 1, "task_url": "http://sops/task/1"},
        }
        get_client.return_value.sops.start_task.return_value = {"result": True}

        execute_data = DataObject(
            inputs={"state_id": "2", "_loop": 0}, outputs={"_loop": 0}
        )
        execute_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        result = sops_service.execute(execute_data, execute_parent_data)
        self.assertEqual(result, True)
        do_exit_plugins.assert_not_called()
        get_client.return_value.sops.create_task.assert_called_once()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_schedule_processor_resolve_error_degrade(self, node_status, get_client):
        """schedule 阶段处理人解析异常：降级处理，不抛异常，继续轮询"""
        node = mock.Mock()
        node.processors_type = "GENERAL"
        node.processors = ""
        node.name = "测试ITSM发送审批"
        node.get_user_list.side_effect = Exception("user api error")
        node_status.get.return_value = node
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {"children": {}, "state": "CREATED"},
        }

        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={"sops_task_id": 1, "bk_biz_id": 123, "api_info": {}},
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.get_output_fields")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.do_before_exit_state")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_schedule_operator_degrade_system(
        self, node_status, get_client, do_before_exit_state, get_output_fields
    ):
        """schedule 阶段未解析到执行人：降级为 system，成功日志正常记录、流程正常结束"""
        node = mock.Mock()
        node.processors_type = "PERSON"
        node.processors = ""
        node.name = "测试ITSM发送审批"
        node_status.get.return_value = node
        do_before_exit_state.return_value = None
        get_output_fields.return_value = []
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {"children": {}, "state": "FINISHED"},
        }

        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={"sops_task_id": 1, "bk_biz_id": 123, "api_info": {}},
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)
        # 自动节点执行成功日志 operator 为 system，流程结束不中断
        node.create_action_log.assert_called_once()
        self.assertEqual(node.create_action_log.call_args[0][0], "system")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_is_transient_error(self):
        """瞬时错误判断：429 限流与 5xx/网络异常可重试，4xx/普通异常不可重试"""
        # 网络层异常（连接错误、超时）视为瞬时错误
        self.assertTrue(BkOpsService.is_transient_error(requests.exceptions.ConnectionError()))
        self.assertTrue(BkOpsService.is_transient_error(requests.exceptions.Timeout()))

        # APIGW 网关层：429 限流与 5xx 视为瞬时错误，4xx 视为不可重试
        resp_429 = requests.Response()
        resp_429.status_code = 429
        resp_500 = requests.Response()
        resp_500.status_code = 500
        resp_404 = requests.Response()
        resp_404.status_code = 404
        self.assertTrue(
            BkOpsService.is_transient_error(requests.exceptions.HTTPError(response=resp_429))
        )
        self.assertTrue(
            BkOpsService.is_transient_error(requests.exceptions.HTTPError(response=resp_500))
        )
        self.assertFalse(
            BkOpsService.is_transient_error(requests.exceptions.HTTPError(response=resp_404))
        )

        # ESB 旧调用：ComponentAPIException 无 resp（请求阶段异常）视为瞬时错误
        self.assertTrue(BkOpsService.is_transient_error(ComponentAPIException("request failed")))

        # 普通异常非瞬时错误
        self.assertFalse(BkOpsService.is_transient_error(ValueError("boom")))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.apigw_client.get_client")
    @mock.patch("itsm.pipeline_plugins.components.collections.bk_sops.Ticket.node_status")
    def test_schedule_uses_system_call_user(self, node_status, get_client):
        """schedule 阶段 SOPS 调用统一使用 SYSTEM_CALL_USER（admin）身份"""
        node = mock.Mock()
        node.processors_type = "PERSON"
        node.processors = ",v_ylcnyao,"
        node.name = "测试ITSM发送审批"
        node_status.get.return_value = node
        get_client.return_value.sops.get_task_status.return_value = {
            "result": True,
            "data": {"children": {}, "state": "RUNNING"},
        }

        sops_service = BkOpsService(name="bk_sops")
        sops_service._runtime_attrs = {"by_flow": 1}
        schedule_data = DataObject(
            inputs={"state_id": "2", "_loop": 0},
            outputs={"sops_task_id": 1, "bk_biz_id": 123, "api_info": {}},
        )
        schedule_parent_data = DataObject(
            inputs={"ticket_id": self.ticket_id}, outputs={"is_first_execute": False}
        )
        result = sops_service.schedule(schedule_data, schedule_parent_data)
        self.assertEqual(result, True)
        # SOPS 调用按系统身份创建 client，而非节点执行人
        get_client.assert_any_call("sops", username=settings.SYSTEM_CALL_USER)
