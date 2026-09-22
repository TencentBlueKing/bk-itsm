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
import copy
import json
import logging
import time

import jmespath
import requests
from django.conf import settings
from django.utils.translation import gettext as _
from jinja2.sandbox import SandboxedEnvironment as Environment
from pipeline.component_framework.component import Component
from pipeline.utils.boolrule import (
    BoolRule,
    MissingVariableException,
    UnknownOperatorException,
)

from itsm.component.constants import (
    FINISHED,
    LESSCODE_PROJECT_KEY,
    NODE_FAILED,
    TRANSITION_OPERATE,
)
from itsm.component.constants.trigger import SOURCE_TICKET, STATE_FAILED
from itsm.component.utils.encode import EncodeWebhook
from itsm.meta.services.webhook_url_validate_service import WebhookURLValidateService
from itsm.pipeline_plugins.components.collections.itsm_base_service import (
    ItsmBaseService,
)
from itsm.ticket.models import SYSTEM_OPERATE, Ticket, TicketGlobalVariable
from itsm.trigger.models import Trigger

logger = logging.getLogger("celery")


class ParamsBuilder:
    def __init__(self, extras, variables):
        self.extras = extras
        self.variables = variables

    def jinja_render(self, template_value):
        """
        做jinja渲染
        :param template_value:
        :return:
        """
        if isinstance(template_value, str):
            return Environment().from_string(template_value).render(self.variables)
        if isinstance(template_value, dict):
            render_value = {}
            for key, value in template_value.items():
                render_value[key] = self.jinja_render(value)
            return render_value
        if isinstance(template_value, list):
            return [self.jinja_render(value) for value in template_value]
        return template_value

    def build_query_params(self, query_params):
        params = {}
        for item in query_params:
            params[item["key"]] = item["value"]
        return params

    def result(self):
        extras_copy = copy.deepcopy(self.extras)
        data = self.jinja_render(extras_copy)
        headers = {header["key"]: header["value"] for header in data.get("headers", [])}
        encode_webhook = EncodeWebhook(headers=headers)
        content = encode_webhook.encode_body(data.get("body", {}))

        body = {
            "type": self.extras.get("body")["type"],
            "raw_type": self.extras.get("body")["raw_type"],
            "content": content,
        }
        data.update(
            {
                "headers": encode_webhook.headers,
                "body": body,
                "query_params": self.build_query_params(data.get("query_params", {})),
            }
        )

        return data


class WebHookService(ItsmBaseService):
    """
    {
            "method": "method",
            "url": "",
            "query_params": [{key:"", value:""}],
            "auth": "",
            "headers": {},
            "body": {
                "type": "row, json",
                "raw_type": "json, "
                "value": ""
            },
            "timeout": "",
            "success_exp": "",
        }

    variables: {
        "outputs":[
                name: "阿哈哈哈"
                ref_path: "resp.result"
                type: "STRING"
            ]
        }
    """

    __need_schedule__ = False
    MAX_ERROR_DETAIL_LENGTH = 500
    MAX_RETRIES = 2

    def validate_webhook_url(self, url):
        WebhookURLValidateService.validate_for_execute(url)

    def validate_success_exp(self, success_exp):
        WebhookURLValidateService.validate_success_exp(success_exp)

    def truncate_message(self, value, max_length=None):
        max_length = max_length or self.MAX_ERROR_DETAIL_LENGTH
        if value is None:
            return ""
        value = str(value)
        if len(value) <= max_length:
            return value
        return "{}...(已截断, 共{}字符)".format(value[:max_length], len(value))

    def format_webhook_error_detail(self, method=None, url=None, query_params=None, headers=None, response=None, error=None):
        detail = {
            "method": method,
            "url": url,
            "query_params": query_params or {},
            "headers": headers or {},
        }

        if response is not None:
            detail.update(
                {
                    "status_code": response.status_code,
                    "reason": getattr(response, "reason", ""),
                    "location": response.headers.get("Location", ""),
                }
            )

        if error is not None:
            detail["error"] = self.truncate_message(error)

        return self.truncate_message(json.dumps(detail, ensure_ascii=False))

    def record_webhook_error(
        self,
        error_message,
        method=None,
        url=None,
        query_params=None,
        headers=None,
        response=None,
        error=None,
    ):
        detail = self.format_webhook_error_detail(
            method=method,
            url=url,
            query_params=query_params,
            headers=headers,
            response=response,
            error=error,
        )
        full_error_message = "{}，detail={}".format(error_message, detail)
        frontend_error_message = error_message
        if response is not None:
            frontend_error_message = "{}, status_code={}".format(
                error_message, response.status_code
            )
        logger.error("[webhook]单次请求失败：%s", full_error_message)
        return frontend_error_message

    def update_info(self, current_node, **kwargs):
        """
        更新任务上下文
        @param current_node: 当前节点状态 Type: object
        @param devops_result: 节点全局变量 Type: object
        @param kwargs: 流水线构建参数 Type: dict
        """

        current_node.contexts.update(**kwargs)
        current_node.save()

    def build_params(self, extras, ticket):
        """
        整体渲染 extras 所有的变量
        """
        variables = ticket.get_output_fields(return_format="dict", need_display=True)
        variables.update(ticket.meta.get("envs", {}))
        result = ParamsBuilder(extras=extras, variables=variables).result()

        return result

    def update_variables(self, resp, ticket_id, state_id, variables):
        resp = {"resp": resp}
        for variable in variables:
            value = jmespath.search(variable["ref_path"], resp)
            if isinstance(value, bool):
                value = json.dumps(value)
            if TicketGlobalVariable.objects.filter(
                ticket_id=ticket_id, key=variable["key"]
            ).exists():
                TicketGlobalVariable.objects.filter(
                    ticket_id=ticket_id, key=variable["key"]
                ).update(value=value)
            else:
                TicketGlobalVariable.objects.create(
                    name=variable.get("name", ""),
                    ticket_id=ticket_id,
                    key=variable["key"],
                    value=value,
                    state_id=state_id,
                )
            variable["value"] = value
        return variables

    def do_exit_plugins(
        self,
        ticket,
        state_id,
        current_node,
        error_message,
        error_message_template,
        processors,
        attempts=0,
    ):
        logger.error(
            "[webhook]节点最终执行失败：ticket_id=%s, state_id=%s, attempts=%s, error=%s",
            getattr(ticket, "id", None),
            state_id,
            attempts,
            error_message,
        )
        current_node.set_failed_status(
            operator=processors,
            message=error_message_template,
            detail_message=error_message,
        )
        ticket.node_status.filter(state_id=state_id).update(
            action_type=TRANSITION_OPERATE
        )
        # 如果启用了触发器，优先使用触发器信号，未配置、未启用，则使用默认发送通知给处理人
        if self.has_enabled_failure_trigger(ticket, state_id):
            logger.info(
                "[webhook]执行节点失败触发器：ticket_id=%s, state_id=%s",
                getattr(ticket, "id", None),
                state_id,
            )
            ticket.send_trigger_signal(
                STATE_FAILED,
                sender=state_id,
                context={
                    "webhook_attempt_count": attempts,
                    "webhook_failure_reason": error_message,
                },
            )
        else:
            notify_message = error_message_template.format(
                name=current_node.name,
                detail_message=error_message,
            )
            logger.info(
                "[webhook]执行节点失败默认通知：ticket_id=%s, state_id=%s, receivers=%s",
                getattr(ticket, "id", None),
                state_id,
                processors,
            )
            ticket.notify(
                state_id=state_id,
                receivers=processors,
                message=notify_message,
                action=NODE_FAILED,
                retry=False,
            )

    @staticmethod
    def has_enabled_failure_trigger(ticket, state_id):
        from itsm.iadmin.utils import is_trigger_switch_off

        if is_trigger_switch_off():
            return False

        return Trigger.objects.filter(
            signal=STATE_FAILED,
            sender=state_id,
            source_type=SOURCE_TICKET,
            source_id=ticket.flow.id,
            is_enabled=True,
        ).exists()

    def get_common_args(self):
        return {
            "bk_app_code": settings.APP_ID,
            "bk_app_secret": settings.APP_TOKEN,
            "bk_username": settings.SYSTEM_USE_API_ACCOUNT,
        }

    def request_once(
        self, method, url, body, query_params, headers, timeout, auth, success_exp
    ):
        """执行一次请求；中间失败只返回结果，不改变节点状态或发送通知。"""
        response = None
        failure = None
        failure_message = "Webhook请求参数构建失败"
        try:
            response = requests.request(
                method,
                url,
                data=body,
                params=query_params,
                headers=headers,
                timeout=int(timeout),
                auth=auth,
                allow_redirects=False,
            )
            if response.status_code not in (200, 201):
                failure_message = "返回状态码非200/201"
                raise requests.exceptions.HTTPError(
                    failure_message, response=response
                )
            failure_message = "返回值非Json"
            resp = response.json()
            if success_exp:
                failure_message = "请求成功判定失败，返回值不满足条件"
                if not BoolRule(success_exp).test(context={"resp": resp}):
                    raise ValueError(failure_message)
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ) as error:
            failure = ("Webhook请求失败", error, True)
        except (
            requests.exceptions.RequestException,
            TypeError,
            ValueError,
            MissingVariableException,
            UnknownOperatorException,
        ) as error:
            failure = (failure_message, error, False)

        if failure:
            error_message, error, retryable = failure
            message = self.record_webhook_error(
                error_message,
                method=method,
                url=url,
                query_params=query_params,
                headers=headers,
                response=response,
                error=error,
            )
            return False, None, message, retryable

        return True, resp, "", False

    def execute(self, data, parent_data):
        if super(WebHookService, self).execute(data, parent_data):
            return True
        logger.info(
            "AutoStateService execute: data={}, parent_data={}".format(
                data.inputs, parent_data.inputs
            )
        )

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)

        state = ticket.flow.get_state(state_id)
        variables = state["variables"].get("outputs", [])
        error_message_template = (
            "WebHook任务【{name}】执行失败，失败信息 {detail_message}"
        )

        processors = ticket.current_processors[1:-1]
        current_node = ticket.node_status.get(state_id=state_id)

        try:
            webhook_info = (
                current_node.query_params
                if current_node.query_params
                else state["extras"].get("webhook_info")
            )
        except Exception as e:
            err_message = "webhook info节点解析失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            extras = self.build_params(webhook_info, ticket)
            self.update_info(current_node, build_params=extras)
        except Exception as e:
            err_message = "Webhook节点解析失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            # 基本信息及请求参数属于配置错误，不进入自动重试
            method = extras.get("method", "GET")
            url = extras.get("url")
            query_params = extras.get("query_params")
            headers = extras.get("headers") or {}
            body = extras.get("body", {})["content"]
            timeout = extras.get("settings", {}).get("timeout", 10)
            success_exp = extras.get("success_exp")

            cleaned_headers = {}
            for key, value in headers.items():
                if key is None or value is None:
                    continue
                clean_key = str(key).strip()
                clean_value = str(value).strip()
                if not clean_key:
                    continue
                cleaned_headers[clean_key] = clean_value

            headers = cleaned_headers

            # 如果是less code的数据处理节点, 针对get or post 请求，填充认证信息
            if ticket.project_key == LESSCODE_PROJECT_KEY:
                common_args = self.get_common_args()
                headers.update({"x-bkapi-authorization": json.dumps(common_args)})
        except Exception as error:
            err_message = "Webhook请求参数构建失败, error={}".format(error)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            auth = EncodeWebhook.encode_authorization(extras.get("auth", {}))
        except Exception as e:
            err_message = "auth信息解析失败， error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            self.validate_webhook_url(url)
        except Exception as e:
            err_message = "Webhook请求地址校验失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        try:
            self.validate_success_exp(success_exp)
        except Exception as e:
            err_message = "Webhook成功判定表达式校验失败, error={}".format(e)
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False

        # MAX_RETRIES + 2 = 4,顾头不顾尾 第四次不会执行
        for attempt in range(1, self.MAX_RETRIES + 2):
            success, resp, error_message, retryable = self.request_once(
                method, url, body, query_params, headers, timeout, auth, success_exp
            )
            self.update_info(
                current_node,
                webhook_attempt_count=attempt,
                webhook_last_error=error_message,
            )
            if success:
                break
            if not retryable or attempt > self.MAX_RETRIES:
                self.do_exit_plugins(
                    ticket,
                    state_id,
                    current_node,
                    error_message,
                    error_message_template,
                    processors,
                    attempts=attempt,
                )
                return False
            current_node.create_action_log(
                "system",
                "WebHook任务【{}】第{}次重试".format(current_node.name, attempt),
                detail_message=error_message,
                source=SYSTEM_OPERATE,
                action_type=SYSTEM_OPERATE,
            )
            logger.warning(
                "[webhook]第%s次重试：ticket_id=%s, state_id=%s, error=%s",
                attempt,
                ticket_id,
                state_id,
                error_message,
            )
            time.sleep(1)

        # 更新全局变量
        variable_output = self.update_variables(resp, ticket_id, state_id, variables)

        # 设置状态
        self.update_info(current_node, variables=variable_output)

        current_node.set_status(status=FINISHED)
        # 创建任务
        current_node.create_action_log(
            "system",
            "WebHook任务【%s】执行成功" % current_node.name,
            source=SYSTEM_OPERATE,
            action_type=SYSTEM_OPERATE,
            fields=[extras],
        )

        for field in ticket.get_output_fields(state_id):
            data.set_outputs("params_%s" % field["key"], field["value"])
        ticket.do_before_exit_state(state_id)
        return True

    def outputs_format(self):
        return []


class WebHookComponent(Component):
    name = _("WEBHOOK 节点")
    code = "itsm_webhook"
    bound_service = WebHookService
