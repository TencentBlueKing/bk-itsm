# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

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

import jmespath
import requests
from bamboo_engine.utils.boolrule import BoolRule
from jinja2 import Template
from pipeline.component_framework.component import Component
from django.utils.translation import ugettext as _

from itsm.component.constants import TRANSITION_OPERATE, NODE_FAILED, FINISHED
from itsm.component.utils.encode import EncodeWebhook
from itsm.pipeline_plugins.components.collections.itsm_base_service import (
    ItsmBaseService,
)
from itsm.ticket.models import Ticket, TicketGlobalVariable, SYSTEM_OPERATE
from pipeline.core.flow.activity import StaticIntervalGenerator

logger = logging.getLogger("celery")


class ParamsBuilder:
    def __init__(self, extras, variables):
        self.extras = extras
        self.variables = variables

    def build_url(self):
        url_config = self.extras.get("url")
        template = Template(url_config)
        value = template.render(self.variables)
        return value

    def build_query_params(self):
        query_params = self.extras.get("query_params")
        data = {}
        for item in query_params:
            template = Template(item["value"])
            data[item["key"]] = template.render(self.variables)

        return data

    def build_headers(self):
        headers = self.extras.get("headers")
        data = {}
        for item in headers:
            template = Template(item["value"])
            data[item["key"]] = template.render(self.variables)

        content_type_headers = {
            "json": "application/json",
            "text": "text/plain",
            "javascript": "application/javascript",
            "html": "text/html",
            "xml": "application/xml",
        }

        body = self.extras.get("body")
        if body.get("type") == "raw":
            data.update(
                {
                    "Content-Type": content_type_headers.get(
                        body.get("content_type"), "text/plain"
                    )
                }
            )
        elif body.get("type") == "raw":
            data.update({"Content-Type": "multipart/form-data"})
        else:
            data.update({"Content-Type": "application/x-www-form-urlencoded"})

        return data

    def build_body(self):
        body = self.extras.get("body")
        encode_webhook = EncodeWebhook(self.variables)
        return encode_webhook.encode_body(body=body)

    def result(self):
        return {
            "url": self.build_url(),
            "body": self.build_body(),
            "headers": self.build_headers(),
            "query_params": self.build_query_params(),
        }


class WebHookService(ItsmBaseService):
    """
    {
            "method": "method",
            "url": {"key":"", value:""},
            "query_params": [{key:"", value:""}],
            "auth": "",
            "headers": {},
            "body": {
                "type": "row, json",
                "row_type": "json, "
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
    interval = StaticIntervalGenerator(1)

    def build_params(self, extras, ticket):
        """
        整体渲染 extras 所有的变量
        """
        variables = ticket.get_output_fields(return_format="dict", need_display=True)

        result = ParamsBuilder(extras=extras, variables=variables).result()

        result["timeout"] = extras.get("timeout", 10)
        result["success_exp"] = extras.get("success_exp", None)

        return result

    def update_variables(self, resp, ticket_id, variables):

        resp = {"resp": resp}
        for variable in variables:
            TicketGlobalVariable.objects.filter(
                ticket_id=ticket_id, key=variable["key"]
            ).update(
                value=jmespath.search(variable["ref_path"], resp)
            )  # 这个地方要改
        return variables

    def do_exit_plugins(
        self,
        ticket,
        state_id,
        current_node,
        error_message,
        error_message_template,
        processors,
    ):
        processors = processors
        current_node.set_failed_status(
            operator=processors,
            message=error_message_template,
            detail_message=error_message,
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
        extras = state["extras"]
        processors = ticket.current_processors[1:-1]
        current_node = ticket.node_status.get(state_id=state_id)

        error_message_template = "WebHook任务【{name}】执行失败，失败信息 {detail_message}"
        try:
            extras = self.build_params(extras, ticket)
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

        # 基本信息
        method = extras.get("method", "GET")
        url = extras.get("url")
        query_params = extras.get("query_params")
        headers = extras.get("headers")
        body = extras.get("body", {})
        timeout = extras.get("timeout", 10)
        success_exp = extras.get("success_exp")

        try:
            response = requests.request(
                method,
                url,
                data=body,
                params=query_params,
                headers=headers,
                timeout=timeout,
                verify=False,
            )
        except Exception as e:
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                str(e),
                error_message_template,
                processors,
            )
            logger.exception("[webhook]节点请求失败，失败原因 error = {}".format(e))
            return False

        # 返回code 非 200
        if response.status_code not in [200, 201]:
            err_message = "返回状态码非200"
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
            resp = response.json()
        except Exception:
            err_message = "返回值非Json"
            self.do_exit_plugins(
                ticket,
                state_id,
                current_node,
                err_message,
                error_message_template,
                processors,
            )
            return False
        if success_exp:
            try:
                rule = BoolRule(success_exp)
                if not rule.test(context={"resp": resp}):
                    err_message = "请求成功判定失败，返回值不满足条件"
                    self.do_exit_plugins(
                        ticket,
                        state_id,
                        current_node,
                        err_message,
                        error_message_template,
                        processors,
                    )
                    return False
            except Exception as e:
                err_message = "请求成功判定异常，error={}".format(e)
                self.do_exit_plugins(
                    ticket,
                    state_id,
                    current_node,
                    err_message,
                    error_message_template,
                    processors,
                )
                return False

        # 更新全局变量
        self.update_variables(resp, ticket_id, variables)
        # 设置状态
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
    name = _("自动节点")
    code = "itsm_webhook"
    bound_service = WebHookService
