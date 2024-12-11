# -*- coding: utf-8 -*-
import json

import requests
from django.conf import settings
from django.http import JsonResponse

from common.log import logger
from config.default import CLOSE_NOTIFY
from itsm.component.constants import APPROVE_RESULT, API, RUNNING, SHOW_BY_CONDITION
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.conversion import show_conditions_validate, format_exp_value
from itsm.meta.services.notice_filter import notice_filter_service
from itsm.ticket.models import Ticket, Status, TicketField, SignTask

# 当前运行环境
RUNNING_ENV = {
    "STAGING": "(预发布)",
    "PRODUCT": "",
}

# 审批动作
APPROVE_MESSAGE = {"true": "同意", "false": "拒绝"}


def build_bkchat_summary(ticket):
    title = "## 『ITSM-{}』{}: {}".format(
        settings.BKCHAT_ENV_FLAG, RUNNING_ENV.get(settings.RUN_MODE, ""), ticket.title
    )
    content = title + "\n"

    if ticket.tag not in ["bk_iam", "bk_ci_rbac"]:
        content += "**单号**: {}\n".format(ticket.sn)
        content += "**服务目录**: {}\n".format(ticket.catalog_service_name)
        current_steps = ",".join([step.get("name") for step in ticket.current_steps])
        content += "**当前环节**: {}\n".format(current_steps or "无")

    content += "**提单人**: {}\n".format(ticket.creator)

    processor_list = [
        processor for processor in ticket.current_processors.split(",") if processor
    ]
    if len(processor_list) > 3:
        processor_content = ",".join(processor_list[0:3]) + "..."
    else:
        processor_content = ",".join(processor_list)

    if processor_content:
        content += "**审批人**: {}".format(processor_content)

    if ticket.tag not in ["bk_iam", "bk_ci_rbac"]:
        # 添加「提单信息」
        content = "{}\n**--- 单据基本信息 ---**".format(content)

    state_fields = ticket.get_state_fields(
        ticket.first_state_id, need_serialize=False
    ).exclude(type__in=["TABLE", "CUSTOMTABLE", "FILE"])
    field_order = ticket.state(ticket.first_state_id)["fields"]
    fields_map = {f.workflow_field_id: f for f in state_fields}
    # 隐藏字段过滤
    for index in field_order:
        f = fields_map.get(index, None)
        if f is None:
            continue
        if f.show_type == SHOW_BY_CONDITION:
            key_value = {
                "params_%s"
                % item["key"]: format_exp_value(item["type"], item["_value"])
                for item in f.ticket.fields.values("key", "_value", "type")
            }
            if show_conditions_validate(f.show_conditions, key_value):
                continue

        detail = "**{}**：{}".format(
            f.name, ticket.display_content(f.type, f.display_value)
        )
        content = "{}\n{}".format(content, detail)
    return content


def notify_fast_approval_message(ticket, state_id, receivers):
    """
    构建快速审批通知参数
    """

    # 如果关闭通知服务则不通知
    # CLOSE_NOTIFY 从环境变量中得到
    if CLOSE_NOTIFY == "close":
        logger.info(
            "[fast_approval({})]The current notify type: {}".format(
                ticket.sn, CLOSE_NOTIFY
            )
        )
        return

    # 如果通知接收人为空则不通知
    if not receivers:
        logger.info("[fast_approval({})]There is no receivers".format(ticket.sn))
        return

    content = build_bkchat_summary(ticket)
    # 发送微信通知
    send_fast_approval_message(ticket.title, content, receivers, ticket, state_id)


def send_fast_approval_message(title, content, receivers, ticket, state_id):
    """
    发送快速审批通知
    """

    ticket_id = ticket.id
    ticket_sn = ticket.sn

    # 更新详情url
    ticket.generate_ticket_url(state_id, receivers)

    # 如果ticket的service_id在service_approval_blacklist中，则不发送bkchat快速审批通知
    service_approval_blacklist = notice_filter_service.get_service_approval_blacklist()
    if str(ticket.service_id) in service_approval_blacklist:
        logger.info(
            f"[fast_approval]Bypass due to service id is in service_approval_blacklist, ticket_id=>{ticket_id}"
        )
        return

    # 接收人过滤
    receivers = notice_filter_service.notice_receiver_filter(receivers)
    if not receivers:
        logger.info(
            f"[fast approval] receivers is empty after filter, ticket_id=>{ticket_id}"
        )
        return

    # 构造data信息
    data = {
        "title": title,
        "summary": content,
        "approvers": str(receivers),
        "plat": settings.FRONTEND_URL,
        "key": ticket_sn,
        "clickname": "查看详情",
        "clickurl": ticket.ticket_url,
        "callback": settings.BKCHAT_CALLBACK_URL,
        "summaryback": settings.ITSM_SUMMARY_URL,
        "action": [{"name": "同意", "value": "true"}, {"name": "拒绝", "value": "false"}],
        "context": {
            "ticket_id": ticket_id,
            "state_id": state_id,
            "ticket_sn": ticket_sn,
        },
    }

    # 如果配置了的环境标示, 需要在请求参数增加这种环境标示
    if settings.BKCHAT_ENV:
        data["env"] = settings.BKCHAT_ENV

    logger.info(
        "[fast_approval({})]send fast approval message data:{}".format(ticket_sn, data)
    )
    # 构造请求参数
    headers = {
        "Content-Type": "application/json",
        "X-Bkapi-Authorization": json.dumps(
            {
                "bk_app_code": settings.BK_APP_CODE,
                "bk_app_secret": settings.BK_APP_SECRET,
                "bk_username": "admin",
            }
        ),
    }

    # 发送请求
    try:
        logger.info(
            "[tasks->notify_task] is executed, title={}, receivers={}, ticket_id={}".format(
                title, receivers, ticket_id
            )
        )
        resp_data = requests.post(url=settings.BKCHAT_URL, json=data, headers=headers)
        logger.info(
            "[fast_approval({})]send fast approval response content:{}".format(
                ticket_sn, resp_data.content
            )
        )
        # 获取请求返回信息
        result = resp_data.json()
        logger.info(
            "[fast_approval({})]send fast approval message result:{}".format(
                ticket_sn, result
            )
        )
        # 验证是否请求成功
        if not result.get("result"):
            logger.info(
                "[fast_approval({})]send fast approval message failed:{}".format(
                    ticket_sn, result.get("message")
                )
            )
    except ComponentCallError as error:
        logger.info(
            "[fast_approval({})]send fast approval message failed, error:{}".format(
                ticket_sn, str(error)
            )
        )
    except Exception as e:
        logger.info(
            "[fast_approval({})]send fast approval message exception:{}".format(
                ticket_sn, str(e)
            )
        )


def proceed_fast_approval(request):
    """
    快速审批回调
    """

    # 1.解密request变携带的加密信息
    result = request.data

    # 2.对解密后的字段进行获取
    ticket_id = int(result.get("context").get("ticket_id"))
    state_id = int(result.get("context").get("state_id"))
    receiver = result.get("approver")
    approve_action = result.get("status")

    ticket = Ticket.objects.get(id=ticket_id)

    node_status = ticket.node_status.get(state_id=state_id)
    if not node_status.can_sign_state_operate(receiver):
        return JsonResponse(
            {
                "result": False,
                "data": {
                    "approve_result": ticket.get_state_approve_result(state_id),
                    "approver": ticket.get_approver(state_id),
                },
                "code": -1,
                "message": "单据审批失败，{}不是当前节点的审批人，无法审批".format(receiver),
            }
        )

    # 3.判断当前节点是否是RUNNING状态，否则通知
    current_status = Status.objects.get(state_id=state_id, ticket_id=ticket_id)
    if current_status.status != "RUNNING":
        title = "『ITSM{}』【审批失败通知】\n".format(RUNNING_ENV.get(settings.RUN_MODE, ""))
        content = "单号：{} ({})\n当前单据审批操作已被处理".format(ticket.sn, ticket.ticket_url)
        return JsonResponse(
            {
                "result": False,
                "data": {
                    "approve_result": ticket.get_state_approve_result(state_id),
                    "approver": ticket.get_approver(state_id),
                },
                "code": -1,
                "message": "{}\n{}".format(title, content),
            }
        )

    node_fields = TicketField.objects.filter(state_id=state_id, ticket_id=ticket_id)
    fields = []
    remarked = False
    for field in node_fields:
        if field.meta.get("code") == APPROVE_RESULT:
            fields.append(
                {
                    "id": field.id,
                    "key": field.key,
                    "type": field.type,
                    "choice": field.choice,
                    "value": approve_action,
                }
            )
        else:
            if not remarked:
                fields.append(
                    {
                        "id": field.id,
                        "key": field.key,
                        "type": field.type,
                        "choice": field.choice,
                        "value": "快速审批，审批人：{}".format(receiver),
                    }
                )
                remarked = True

    logger.info("proceed_fast_approval request fields is {}".format(fields))
    node_status = ticket.node_status.get(state_id=state_id)
    SignTask.objects.update_or_create(
        status_id=node_status.id,
        processor=receiver,
        defaults={
            "status": "RUNNING",
        },
    )
    res = ticket.activity_callback(state_id, receiver, fields, API)
    if not res.result:
        logger.warning(
            "callback error， current state id %s, error message: %s"
            % (state_id, res.message)
        )
        ticket.node_status.filter(state_id=state_id).update(status=RUNNING)
        return JsonResponse(
            {
                "result": False,
                "data": None,
                "code": -1,
                "message": "快速审批异常，请联系管理员",
            }
        )

    title = "『ITSM{}』【审批成功通知】".format(RUNNING_ENV.get(settings.RUN_MODE, ""))
    approve_message = "您的审批动作为：{}".format(APPROVE_MESSAGE.get(approve_action, ""))
    callback_message = "{}\n\n单号：{} ({})\n{}".format(
        title, ticket.sn, ticket.ticket_url, approve_message
    )
    return JsonResponse(
        {
            "result": True,
            "data": None,
            "code": 0,
            "message": callback_message,
        }
    )
