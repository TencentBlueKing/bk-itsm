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

import copy
import json
import logging
import re
from datetime import datetime, timedelta

import jsonschema
from django.core.cache import cache
from django.db import transaction
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    ACTION_DICT,
    FAILED,
    FINISHED,
    SYSTEM_OPERATE,
    LEN_LONG,
    API_DICT,
    TRANSITION_OPERATE,
    NODE_FAILED,
)
from itsm.component.esb.backend_component import bk
from itsm.component.utils.basic import list_by_separator
from itsm.component.utils.conversion import (
    build_conditions_by_mako_template,
    build_params_by_mako_template,
    conditions_conversion,
    params_type_conversion,
    rsp_conversion,
)
from itsm.postman.models import RemoteApiInstance
from itsm.ticket.serializers import TaskStateApiInfoSerializer
from itsm.ticket.models import Ticket, TicketEventLog, TicketGlobalVariable
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import StaticIntervalGenerator
from pipeline.utils.boolrule import BoolRule

from .itsm_base_service import ItsmBaseService

logger = logging.getLogger("celery")


class AutoStateService(ItsmBaseService):
    """
    输入：state_id->api_instance_id
    输出：将勾选的字段（key）设置为输出（set_output + state.variables）
    轮询：
    """

    __need_schedule__ = True
    interval = StaticIntervalGenerator(1)

    @staticmethod
    def poll_proceed(api_config, success_conditions):
        rsp = bk.http(config=api_config)
        if success_conditions is None:
            return rsp.get("result", False), rsp
        # 构造带${params_}的条件
        conditions = conditions_conversion(success_conditions)
        rsp_copy = copy.deepcopy(rsp)
        rsp_conversion(rsp_copy)  # 构造带params_的返回结果
        b_result, b_conditions = build_conditions_by_mako_template(conditions, rsp_copy)
        if not b_result:
            return False, rsp
        return BoolRule(b_conditions).test(), rsp

    def update_variables(self, rsp, ticket_id, variables, data=None):
        for variable in variables:
            TicketGlobalVariable.objects.filter(
                ticket_id=ticket_id, key=variable["key"]
            ).update(value=rsp.get(variable["ref_path"], ""))
        return variables

    @staticmethod
    def update_status(ticket, state_id, status, ex_data=None):
        if ex_data:
            ticket.node_status.filter(state_id=state_id).update(
                contexts={"ex_data": ex_data},
                status=status,
            )
        else:
            ticket.node_status.filter(state_id=state_id).update(
                status=status,
            )

    @staticmethod
    def build_query_params(ticket, query_params, schema, method="POST"):
        # 引用变量，变量写入
        params = {
            "params_{}".format(key): value
            for key, value in ticket.get_output_fields(
                return_format="dict", need_display=True
            ).items()
        }

        params_list = re.findall(r"\${(.*?)}", str(query_params))
        for name in params_list:
            if name not in params:
                params[name] = ""
        logger.warning(
            "请求参数添加完成， query_params is {}, params is {}".format(query_params, params)
        )
        result, build_query_params = build_params_by_mako_template(query_params, params)
        logger.warning("请求参数构造完成， build_query_params is {}".format(build_query_params))
        if not result:
            logger.warning(
                "请求参数构造异常， query_params is {}, params is {}".format(
                    query_params, params
                )
            )
            return False, _("请求参数构造异常，详细信息： %s") % str(build_query_params)

        # 引用变量的类型转换及参数整体schema校验
        if method == "POST":
            try:
                params_type_conversion(build_query_params, schema)
            except BaseException as e:
                logger.warning(build_query_params)
                return False, _("请求参数转换异常，详细信息： %s") % str(str(e))

            try:
                jsonschema.validate(build_query_params, schema)
            except Exception as e:
                logger.warning(build_query_params)
                return False, _("请求参数校验异常，详细信息： %s") % str(str(e))

        return True, build_query_params

    def get_rsp_content(
        self, ticket, state_id, api_config, success_conditions, operate_info=None
    ):
        if operate_info and json.loads(operate_info)["action"] == "MANUAL":
            ignore_params = ticket.node_status.get(state_id=state_id).ignore_params
            logger.info("ignore_params is {}".format(ignore_params))
            return True, {"data": ignore_params}
        else:
            return self.poll_proceed(copy.deepcopy(api_config), success_conditions)

    def do_exit_plugins(
        self,
        ticket,
        state_id,
        state_status,
        ex_data,
        rsp,
        variables,
        data=None,
        operator_info=None,
    ):
        """
        退出自动节点前的清理动作
        1、结束轮询
        """
        state = ticket.state(state_id)
        data.set_outputs("service_status", state_status)
        self.finish_schedule()

        with transaction.atomic():
            self.update_variables(rsp, ticket.id, variables, data)

            # self.set_outputs(data, ticket, state_id)
            for field in ticket.get_output_fields(state_id):
                data.set_outputs("params_%s" % field["key"], field["value"])
                logger.info(
                    'do_exit_plugins::set_output: "params_{}" = {}'.format(
                        field["key"], field["value"]
                    )
                )

            if not operator_info:
                operator = "system"
                operate_type = SYSTEM_OPERATE
                action = ACTION_DICT.get(SYSTEM_OPERATE)
                log_message = (
                    "自动处理单据任务【{name}】执行失败：({detail_message})."
                    if state_status == FAILED
                    else "自动处理单据任务【{name}】执行成功."
                )
            else:
                detail = json.loads(operator_info)
                operator = detail["operator"]
                operate_type = detail["action"].upper()
                action = API_DICT.get(detail["action"].upper())
                if state_status == FAILED:
                    log_message = (
                        "{operator}{action}单据任务【{name}】执行失败：({detail_message})."
                    )
                else:
                    log_message = "{operator}{action}单据任务【{name}】执行成功."
            node_status = ticket.status(state_id)
            api_config = {}
            if node_status:
                api_config = TaskStateApiInfoSerializer(
                    node_status.api_instance,
                    many=False,
                    context={"status": node_status},
                ).data
                if node_status.query_params:
                    if api_config["method"] == "GET":
                        api_config["req_params"] = node_status.query_params
                    else:
                        api_config["req_body"] = node_status.query_params
            api_log_info = [
                {
                    "key": "api_info",
                    "name": "api信息",
                    "value": api_config,
                    "show_result": True,
                }
            ]
            tlog = TicketEventLog.objects.create_log(
                ticket=ticket,
                state_id=state_id,
                log_operator=operator,
                operate_type=operate_type,
                action=action,
                message=log_message,
                detail_message=ex_data[:LEN_LONG] if ex_data else rsp,
                from_state_name=state.get("name"),
                source=SYSTEM_OPERATE,
                fields=api_log_info,
            )

            self.update_status(ticket, state_id, state_status, ex_data)
            if state_status == FAILED:
                ticket.node_status.filter(state_id=state_id).update(
                    action_type=TRANSITION_OPERATE
                )
                # 发送通知
                ticket.notify(
                    state_id=state_id,
                    receivers=operator,
                    message=ex_data[:LEN_LONG] if ex_data else rsp,
                    action=NODE_FAILED,
                    retry=False,
                )

            # 发送通知
            if node_status:
                receivers = ",".join(list_by_separator(node_status.processors))
                ticket.notify(
                    state_id, receivers, message=tlog.translated_message, retry=False
                )

        # 失败的情况也需要进入推出节点记录信息
        ticket.do_before_exit_state(state_id)

    def execute(self, data, parent_data):
        if super(AutoStateService, self).execute(data, parent_data):
            return True

        logger.info(
            "AutoStateService execute: data={}, parent_data={}".format(
                data.inputs, parent_data.inputs
            )
        )

        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id
        ticket = Ticket.objects.get(id=ticket_id)
        state = ticket.flow.get_state(state_id)
        variables = state["variables"].get("outputs", [])
        data.set_outputs("variables", variables)
        try:
            api_instance = RemoteApiInstance.objects.get(id=state["api_instance_id"])
        except RemoteApiInstance.DoesNotExist:
            self.do_exit_plugins(
                ticket, state_id, FAILED, _("对应的api配置不存在，请查询"), {}, variables, data
            )
            return True
        # 更新单据状态
        ticket.do_before_enter_state(
            state_id, api_instance_id=api_instance.id, retry=False, by_flow=self.by_flow
        )

        all_variable_keys = [variable["key"] for variable in variables]
        existed_variable_keys = TicketGlobalVariable.objects.filter(
            state_id=state_id, ticket_id=ticket_id, key__in=all_variable_keys
        ).values_list("key", flat=True)

        objs = [
            TicketGlobalVariable(
                **{
                    "key": variable.get("key", ""),
                    "name": variable.get("name", ""),
                    "state_id": state_id,
                    "ticket_id": ticket_id,
                }
            )
            for variable in variables
            if variable["key"] not in existed_variable_keys
        ]
        if objs:
            TicketGlobalVariable.objects.bulk_create(objs)

        # 引用变量，变量写入
        api_config = api_instance.get_config()
        remote_api = api_instance.remote_api
        schema = (
            remote_api.req_params if remote_api.method == "GET" else remote_api.req_body
        )
        node_status = ticket.node_status.get(state_id=state_id)
        schedule_query_params = (
            node_status.query_params
            if node_status.query_params
            else api_config["query_params"]
        )
        result, query_params = self.build_query_params(
            ticket, schedule_query_params, schema, remote_api.method
        )
        node_status.query_params = query_params
        node_status.save()
        if not result:
            self.do_exit_plugins(
                ticket, state_id, FAILED, query_params, {}, variables, data
            )
            return True

        api_config["id"] = api_instance.id
        # 设置接口执行用户为提单人
        api_config["query_params"] = query_params
        data.set_outputs("api_config", api_config)
        data.set_outputs("need_poll", api_instance.need_poll)

        if api_instance.need_poll:
            success_conditions = api_instance.succeed_conditions
            end_conditions = api_instance.end_conditions
            data.set_outputs("success_conditions", success_conditions)
            data.set_outputs("poll_time", end_conditions.get("poll_time", 1))
            data.set_outputs("poll_interval", end_conditions.get("poll_interval", 0))
        else:
            data.set_outputs("poll_time", 1)
            data.set_outputs("poll_interval", 0)

        return True

    def schedule(self, data, parent_data, callback_data=None):
        """
        API执行和轮询逻辑
        """
        try:
            if data.outputs.get("service_status") == FAILED:
                # 当任务已经结束的时候，直接返回，不需要处理
                self.finish_schedule()
                return False
            poll_time = data.outputs.get("poll_time", 1)
            poll_interval = data.outputs.get("poll_interval", 0)
            api_config = data.outputs.get("api_config")
            success_conditions = data.outputs.get("success_conditions")
            ticket_id = parent_data.inputs.ticket_id
            state_id = data.inputs.state_id
            ticket = Ticket.objects.get(id=ticket_id)
            variables = data.outputs.get("variables")
            operate_info = cache.get("node_retry_{}_{}".format(ticket_id, state_id))
            logger.info("operate_info is {}".format(operate_info))
            # 补充ticket/state/api_instance_id信息
            api_config.update(
                ticket_id=ticket_id,
                state_id=state_id,
                api_instance_id=api_config.get("id", 0),
            )

            latest_poll_time = data.outputs.get(
                "latest_poll_time", datetime.now() - timedelta(seconds=poll_interval)
            )

            if not (
                poll_time
                and latest_poll_time
                <= datetime.now() - timedelta(seconds=poll_interval)
            ):
                return True

            logger.info(
                "\n-------  AutoStateService schedule  times: %s  latest_poll_time %s state_id %s ticket_id"
                " %s----------\n" % (poll_time, latest_poll_time, state_id, ticket_id)
            )

            # 如果为轮询并且时间超过上一次的轮询时间
            p_result, p_rsp = self.get_rsp_content(
                ticket,
                state_id,
                copy.deepcopy(api_config),
                success_conditions,
                operate_info,
            )
            poll_time -= 1
            if p_result:
                # 返回为True的时候，直接结束
                self.do_exit_plugins(
                    ticket=ticket,
                    state_id=state_id,
                    state_status=FINISHED,
                    ex_data=p_rsp.get("message", "执行成功"),
                    rsp=p_rsp.get("data") or p_rsp,
                    variables=variables,
                    data=data,
                    operator_info=operate_info,
                )
                return True
            if poll_time <= 0:
                logger.error(
                    "[AutoStateService_schedule] api_request_error, response={}".format(
                        p_rsp
                    )
                )
                self.do_exit_plugins(
                    ticket=ticket,
                    state_id=state_id,
                    state_status=FAILED,
                    ex_data=p_rsp.get("message", "API调用异常，返回结果不为True"),
                    rsp=p_rsp.get("data") or p_rsp,
                    variables=variables,
                    data=data,
                    operator_info=operate_info,
                )
                return False

            data.set_outputs("poll_time", poll_time)
            data.set_outputs("latest_poll_time", datetime.now())
            return True
        except Exception as err:
            import traceback

            logger.error(traceback.format_exc())
            logger.error(err)
            raise err

    def outputs_format(self):
        return []


class AutoStateComponent(Component):
    name = _("自动节点")
    code = "itsm_auto"
    bound_service = AutoStateService
