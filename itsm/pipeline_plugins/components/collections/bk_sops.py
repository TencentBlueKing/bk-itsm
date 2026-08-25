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

import logging

from blueapps.conf import settings
import requests

from blueking.component.open.exceptions import ComponentAPIException
from itsm.component.apigw import client as apigw_client
from itsm.component.constants import NODE_FAILED, SYSTEM_OPERATE, TRANSITION_OPERATE
from itsm.ticket.models import Ticket, TicketGlobalVariable
from itsm.ticket.serializers import StatusSerializer
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import StaticIntervalGenerator

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class BkOpsService(ItsmBaseService):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(10)
    MAX_SCHEDULE_FAIL_COUNT = 10

    @staticmethod
    def _log_prefix(ticket_id, state_id, sops_task_id=None):
        """生成结构化日志前缀，便于按 ticket_id 检索 sops 执行日志"""
        prefix = f"ticket_id={ticket_id}, state_id={state_id}"
        if sops_task_id:
            prefix = f"{prefix}, sops_task_id={sops_task_id}"
        return prefix

    def prepare_task_params(self, state, ticket, sops_info):
        values = ticket.get_output_fields(return_format="dict", need_display=True)
        if sops_info["bk_biz_id"]["value_type"] == "variable":
            bk_biz_id = values.get(sops_info["bk_biz_id"]["value"], 0)
        else:
            bk_biz_id = sops_info["bk_biz_id"]["value"]

        constants = sops_info["constants"]
        for constant in constants:
            if constant["value_type"] == "variable":
                constant["value"] = values.get(constant["value"], "")
        constants = {constant["key"]: constant["value"] for constant in constants}

        exclude_task_nodes_id = sops_info.get("exclude_task_nodes_id", [])
        template_source = sops_info.get("template_source", "common")

        params = {
            "bk_biz_id": bk_biz_id,
            "template_id": str(sops_info["template_id"]),
            "flow_type": "common",
            "template_source": template_source,
            "name": "ITSM-" + state["name"],
            "constants": constants,
            "exclude_task_nodes_id": exclude_task_nodes_id,
            # return raw response data
            "__raw": True,
        }

        return params

    @staticmethod
    def resolve_operator(current_node):
        """从标准运维节点配置中解析节点执行人"""
        try:
            if current_node.processors_type == "PERSON":
                raw_processors = [
                    processor.strip()
                    for processor in current_node.processors.strip(",").split(",")
                    if processor.strip()
                ]
            else:
                # 注意不能使用 get_processors()：标准运维节点 action_type 为 SYSTEM_OPERATE，
                # get_processors() 会返回"系统自动处理"中文，导致角色类型处理人被过滤为空
                raw_processors = [
                    processor
                    for processor in current_node.get_user_list()
                    if processor and processor.isascii()
                ]
        except Exception as error:
            logger.warning(
                "[bk_sops] 处理人解析失败, %s, error=%s",
                BkOpsService._log_prefix(
                    getattr(current_node, "ticket_id", None),
                    getattr(current_node, "state_id", None),
                ),
                str(error),
            )
            raw_processors = []

        processors = ",".join(raw_processors)
        operator = next(
            (processor for processor in raw_processors if processor != "system"),
            None,
        )
        return processors, operator

    def update_info(self, current_node, sops_result, **kwargs):
        """更新任务上下文"""

        sops_result.value = kwargs.get("result", "")
        sops_result.save()

        current_node.contexts.update(**kwargs)
        current_node.save()

    def do_exit_plugins(self, result, **kwargs):
        if not result:
            current_node = kwargs.get("current_node")
            sops_result = kwargs.get("sops_result")
            error_message = kwargs.get("error")
            processors = kwargs.get("processors")
            error_message_template = kwargs.get("error_message_template")
            ticket = kwargs.get("ticket")
            state_id = kwargs.get("state_id")
            self.update_info(
                current_node, sops_result, error_message=error_message, result=result
            )
            current_node.set_failed_status(
                operator=processors,
                message=error_message_template,
                detail_message=error_message,
            )
            logger.error(
                "[bk_sops] do_exit_plugins, %s, error=%s",
                self._log_prefix(getattr(ticket, "id", None), state_id),
                error_message,
            )
            ticket.node_status.filter(state_id=state_id).update(
                action_type=TRANSITION_OPERATE
            )
            # 发送通知
            ticket.notify(
                state_id=state_id,
                receivers=processors,
                message=error_message_template,
                action=NODE_FAILED,
                retry=False,
            )

    def execute(self, data, parent_data):
        if super().execute(data, parent_data):
            return True

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)
        data.set_outputs(f"params_sops_result_{state_id}", False)
        current_node = ticket.node_status.get(state_id=state_id)

        error_message_template = "标准运维任务【{name}】执行失败，失败信息 {detail_message}"

        # 创建全局变量
        sops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="sops_result_" + str(state_id),
            name="sops_result_" + str(state_id),
            state_id=state_id,
            ticket_id=ticket_id,
            value="",
        )

        processors, operator = self.resolve_operator(current_node)

        # first step create_task
        state = ticket.state(state_id)
        sops_info = (
            current_node.query_params
            if current_node.query_params
            else state["extras"]["sops_info"]
        )
        task_params = self.prepare_task_params(state, ticket, sops_info)
        api_info = [
            {
                "key": "api_info",
                "name": "api信息",
                "value": StatusSerializer.build_sops_info(sops_info, task_params),
                "show_result": True,
            }
        ]
        current_node.create_action_log(
            "system",
            "开始执行标准运维任务【{name}】",
            source=SYSTEM_OPERATE,
            action_type=SYSTEM_OPERATE,
            fields=api_info,
        )
        self.update_info(current_node, sops_result, task_params=task_params)

        logger.info(
            "[bk_sops] create_task start, %s, api=system_create_task, template_id=%s, bk_biz_id=%s",
            self._log_prefix(ticket_id, state_id),
            task_params.get("template_id"),
            task_params.get("bk_biz_id"),
        )
        try:
            create_result = (
                apigw_client.get_client("sops", username=settings.SYSTEM_CALL_USER)
                .sops.create_task(
                    data=task_params,
                    path_params={
                        "bk_biz_id": task_params["bk_biz_id"],
                        "template_id": task_params["template_id"],
                    },
                )
            )
        except Exception as error:
            logger.error(
                "[bk_sops] create_task error, %s, api=system_create_task, error=%s, task_params=%s",
                self._log_prefix(ticket_id, state_id),
                str(error),
                task_params,
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=str(error),
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        if not create_result.get("result", False):
            detail_message = create_result.get("message") or "unknown"
            logger.error(
                "[bk_sops] create_task failed, %s, api=system_create_task, code=%s, message=%s, trace_id=%s, data=%s",
                self._log_prefix(ticket_id, state_id),
                create_result.get("code"),
                create_result.get("message"),
                create_result.get("trace_id"),
                create_result.get("data"),
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=detail_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        sops_task_id = create_result.get("data", {}).get("task_id")
        task_url = create_result.get("data", {}).get("task_url")
        # 记录节点执行人供流程/审计使用；SOPS 调用身份统一为 SYSTEM_CALL_USER
        data.set_outputs("operator", operator)

        # second_step execute
        try:
            start_result = (
                apigw_client.get_client("sops", username=settings.SYSTEM_CALL_USER)
                .sops.start_task(
                    {
                        "__raw": True,
                        "task_id": sops_task_id,
                        "bk_biz_id": task_params["bk_biz_id"],
                    }
                )
            )
            self.update_info(current_node, sops_result, task_url=task_url)
        except Exception as error:
            logger.error(
                "[bk_sops] start_task error, %s, api=system_start_task, error=%s",
                self._log_prefix(ticket_id, state_id, sops_task_id),
                str(error),
            )
            error_message = f"start task error, task id {sops_task_id}"
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        if not start_result.get("result", False):
            message = start_result.get("message", "未知错误")
            logger.error(
                "[bk_sops] start_task failed, %s, api=system_start_task, code=%s, message=%s, trace_id=%s, data=%s",
                self._log_prefix(ticket_id, state_id, sops_task_id),
                start_result.get("code"),
                start_result.get("message"),
                start_result.get("trace_id"),
                start_result.get("data"),
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            return False

        logger.info(
            "[bk_sops] start_task success, %s, sops_task_id=%s",
            self._log_prefix(ticket_id, state_id),
            sops_task_id,
        )
        data.set_outputs("sops_task_id", sops_task_id)
        data.set_outputs("bk_biz_id", task_params["bk_biz_id"])
        data.set_outputs("api_info", api_info)

        return True

    def schedule(self, data, parent_data, callback_data=None):

        error_message_template = "标准运维任务【{name}】schedule 执行失败，失败信息 {detail_message}"

        sops_task_id = data.outputs.get("sops_task_id", None)
        bk_biz_id = data.outputs.get("bk_biz_id", None)
        api_info = data.outputs.get("api_info", None)
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=parent_data.inputs.ticket_id)
        current_node = ticket.node_status.get(state_id=state_id)

        logger.info(
            "[bk_sops] schedule start, %s, sops_task_id=%s, bk_biz_id=%s",
            self._log_prefix(ticket.id, state_id, sops_task_id),
            sops_task_id,
            bk_biz_id,
        )

        # 解析节点处理人用于失败通知；处理人解析失败时已内部降级为空，不会抛异常卡死
        processors, _ = self.resolve_operator(current_node)

        sops_result, created = TicketGlobalVariable.objects.get_or_create(
            key="sops_result_" + str(state_id),
            name="sops_result_" + str(state_id),
            state_id=state_id,
            ticket_id=ticket.id,
            value="",
        )

        if not sops_task_id:
            error_message = "invalid callback_data, sops_task_id is null"
            data.outputs.ex_data = error_message
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        try:
            task_status_params = {
                "__raw": True,
                "task_id": sops_task_id,
                "bk_biz_id": bk_biz_id,
            }
            task_result = (
                apigw_client.get_client("sops", username=settings.SYSTEM_CALL_USER)
                .sops.get_task_status(task_status_params)
            )
        except Exception as error:
            fail_count = data.outputs.get("schedule_fail_count", 0) + 1
            data.set_outputs("schedule_fail_count", fail_count)
            if self.is_transient_error(error) and fail_count <= self.MAX_SCHEDULE_FAIL_COUNT:
                logger.warning(
                    "[bk_sops] get_task_status transient error, %s, sops_task_id=%s, "
                    "fail_count=%s/%s, error=%s",
                    self._log_prefix(ticket.id, state_id, sops_task_id),
                    sops_task_id,
                    fail_count,
                    self.MAX_SCHEDULE_FAIL_COUNT,
                    str(error),
                )
                return True
            else:
                data.set_outputs("schedule_fail_count", 0)
            logger.error(
                "[bk_sops] get_task_status error, %s, sops_task_id=%s, error=%s",
                self._log_prefix(ticket.id, state_id, sops_task_id),
                sops_task_id,
                str(error),
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=str(error),
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        # 接口调用成功，清零连续失败计数
        if data.outputs.get("schedule_fail_count", 0):
            data.set_outputs("schedule_fail_count", 0)

        if not task_result.get("result", False):
            error_message = task_result.get("message", "")
            logger.error(
                "[bk_sops] get_task_status failed, %s, sops_task_id=%s, code=%s, message=%s, trace_id=%s, data=%s",
                self._log_prefix(ticket.id, state_id, sops_task_id),
                sops_task_id,
                task_result.get("code"),
                task_result.get("message"),
                task_result.get("trace_id"),
                task_result.get("data"),
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        task_info = task_result.get("data", {})

        current_status = task_info.get("state")
        logger.info(
            "[bk_sops] get_task_status success, %s, sops_task_id=%s, state=%s",
            self._log_prefix(ticket.id, state_id, sops_task_id),
            sops_task_id,
            current_status,
        )

        if current_status in ["CREATED", "RUNNING", "SUSPENDED"]:
            # 还在执行过程中，继续轮询
            logger.info(
                "[bk_sops] task running, %s, sops_task_id=%s, state=%s",
                self._log_prefix(ticket.id, state_id, sops_task_id),
                sops_task_id,
                current_status,
            )
            return True
        if current_status in ["FAILED", "REVOKED"]:
            data.set_outputs(f"params_sops_result_{state_id}", False)
            error_message = self.get_detail_message(
                task_status_params, task_info, ticket.id, state_id
            )
            logger.error(
                "[bk_sops] task failed, %s, sops_task_id=%s, state=%s, detail=%s",
                self._log_prefix(ticket.id, state_id, sops_task_id),
                sops_task_id,
                current_status,
                error_message,
            )
            self.do_exit_plugins(
                result=False,
                current_node=current_node,
                sops_result=sops_result,
                error=error_message,
                processors=processors,
                error_message_template=error_message_template,
                ticket=ticket,
                state_id=state_id,
            )
            self.finish_schedule()
            return False

        if current_status in ["FINISHED"]:
            logger.info(
                "[bk_sops] task finished, %s, sops_task_id=%s, state=%s",
                self._log_prefix(ticket.id, state_id, sops_task_id),
                sops_task_id,
                current_status,
            )
            data.set_outputs(f"params_sops_result_{state_id}", True)
            self.finish_schedule()
            self.update_info(current_node, sops_result, result=True)
            current_node.set_status(status=current_status)
            current_node.create_action_log(
                "system",
                f"标准运维任务【{current_node.name}】执行成功",
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
                fields=api_info,
            )

            for field in ticket.get_output_fields(state_id):
                data.set_outputs("params_{}".format(field["key"]), field["value"])

            ticket.do_before_exit_state(state_id)

            return True

    def get_detail_message(self, task_params, task_info, ticket_id, state_id):
        failed_children = [
            child
            for child in task_info.get("children", {}).values()
            if child["state"] == "FAILED"
        ]
        error_messages = []
        for child in failed_children:
            # 构造独立参数，避免 update 污染外部 task_params 字典
            node_detail_params = {
                "__raw": True,
                "task_id": task_params["task_id"],
                "bk_biz_id": task_params["bk_biz_id"],
                "node_id": child["id"],
            }
            try:
                result = (
                    apigw_client.get_client("sops", username=settings.SYSTEM_CALL_USER)
                    .sops.get_task_node_detail(node_detail_params)
                )
            except Exception as error:
                logger.error(
                    "[bk_sops] get_task_node_detail error, %s, node_id=%s, node_name=%s, error=%s",
                    BkOpsService._log_prefix(
                        ticket_id, state_id, task_params.get("task_id")
                    ),
                    child["id"],
                    child["name"],
                    str(error),
                )
                child_error = f"获取节点详情失败: {error}"
            else:
                child_error = result.get("data", {}).get("ex_data") or "未知错误"
                logger.error(
                    "[bk_sops] task node failed, %s, node_id=%s, node_name=%s, error=%s",
                    BkOpsService._log_prefix(
                        ticket_id, state_id, task_params.get("task_id")
                    ),
                    child["id"],
                    child["name"],
                    child_error,
                )
            error_messages.append("{}:{}".format(child["name"], child_error))
        return "\n".join(error_messages)

    def outputs_format(self):
        return []

    @staticmethod
    def is_transient_error(error):
        """判断是否为可重试的瞬时错误（网关/网络类故障）"""
        # 可重试的 HTTP 状态码：429 限流 + 5xx 网关错误
        retryable_status_codes = {429, 500, 502, 503, 504}
        # requests 网络层异常（连接错误、超时等）—— ESB 与 APIGW 底层均基于 requests
        if isinstance(
            error, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
        ):
            return True
        # 组件 SDK 抛出的 ComponentAPIException（ESB 旧调用）
        if isinstance(error, ComponentAPIException):
            resp = getattr(error, "resp", None)
            if resp is None:
                # 请求阶段异常（连接超时、网络中断等），尚未生成响应对象
                return True
            status_code = getattr(resp, "status_code", None)
            if status_code in retryable_status_codes:
                # 429 限流 / 5xx 网关错误（502/503/504 等）
                return True
            return False
        # APIGW 网关层 5xx/限流：bkapi_client_core 的 ResponseError（requests.RequestException 子类）
        if isinstance(error, requests.RequestException) and not isinstance(
            error, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
        ):
            status_code = getattr(getattr(error, "response", None), "status_code", None)
            if status_code in retryable_status_codes:
                return True
            return False
        return False


class BkOpsComponent(Component):
    name = "标准运维"
    code = "bk_sops"
    bound_service = BkOpsService
