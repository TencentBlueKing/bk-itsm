# -*- coding: utf-8 -*-
import re

import requests
from django.conf import settings
from django.http import JsonResponse

from common.log import logger
from config.default import CLOSE_NOTIFY
from itsm.component.constants import APPROVE_RESULT, API, RUNNING, SHOW_BY_CONDITION
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.conversion import show_conditions_validate, format_exp_value
from itsm.ticket.models import Ticket, Status, TicketField, SignTask

from itsm.ticket.utils import build_message
from platform_config.open.bkchat.aes import Aes

APPID = settings.BKCHAT_APPID
APPKEY = settings.BKCHAT_APPKEY

# 当前运行环境
RUNNING_ENV = {
    "STAGING": "(预发布)",
    "PRODUCT": "",
}

# 审批动作
APPROVE_MESSAGE = {"true": "同意", "false": "拒绝"}


def notify_fast_approval_message(
    ticket, state_id, receivers, message, action, **kwargs
):
    """
    构建快速审批通知参数
    """
    if not settings.USE_BKCHAT:
        return

    task_id = kwargs.get("task_id")

    # 如果关闭通知服务则不通知
    # CLOSE_NOTIFY 从环境变量中得到
    if CLOSE_NOTIFY == "close":
        logger.info(
            "[fast_approval({})]The current notify type: {}".format(
                ticket.sn, CLOSE_NOTIFY
            )
        )
        return

    # 不通知
    if ticket.flow.notify_rule == "NONE":
        logger.info(
            "[fast_approval({})]The notify_rule of the current flow: {}".format(
                ticket.sn, ticket.flow.notify_rule
            )
        )
        return

    # 如果通知接收人为空则不通知
    if not receivers:
        logger.info("[fast_approval({})]There is no receivers".format(ticket.sn))
        return

    # 根据流程设定的通知方式通知
    for _notify in ticket.flow.notify.all():
        # 判断通知类型如果不是微信则返回
        if _notify.type != "WEIXIN":
            logger.info(
                "[fast_approval({})]The current notify type: {}".format(
                    ticket.sn, _notify.type
                )
            )
            return

        # 从右向左删除
        # 用来处理「当前环节」后的审批人列表
        def rreplace(self, old, new, *max_length):
            count = len(self)
            if max_length and str(max_length[0]).isdigit():
                count = max_length[0]
            return new.join(self.rsplit(old, count))

        # 构造内容，标题
        content, title = build_message(
            _notify, task_id, ticket, message, action, **kwargs
        )

        # 修改「标题」，添加环境标识
        title = title.replace(
            "『ITSM』", "『ITSM{}』".format(RUNNING_ENV.get(settings.RUN_MODE, ""))
        )

        # 修改「单号」，只显示单号，去除超链接
        content = content.replace(content.split("\n")[2], " 单号：{}".format(ticket.sn))

        # 去除审批人列表
        # 例：当前环节：admin审批(admin) -> 当前环节：admin审批
        all_approver = (re.findall(r"[(](.*?)[)]", content)[-1]).split("(")[-1]
        content = rreplace(content, "({})".format(all_approver), "", 1)

        # 添加「提单人」信息
        content = "{}提单人：{}".format(content, ticket.creator)

        # 添加「提单信息」
        content = "{}\n --- 单据基本信息 ---".format(content)
        state_fields = ticket.get_state_fields(
            ticket.first_state_id, need_serialize=False
        )
        # 隐藏字段过滤
        for f in state_fields.exclude(type__in=["TABLE", "CUSTOMTABLE", "FILE"]):
            if f.show_type == SHOW_BY_CONDITION:
                key_value = {
                    "params_%s"
                    % item["key"]: format_exp_value(item["type"], item["_value"])
                    for item in f.ticket.fields.values("key", "_value", "type")
                }
                if show_conditions_validate(f.show_conditions, key_value):
                    continue

            detail = "{}：{}".format(
                f.name, ticket.display_content(f.type, f.display_value)
            )
            content = "{}\n {}".format(content, detail)
        content = "{}\n --------------------".format(content)

        # 发送微信通知
        send_fast_approval_message(title, content, receivers, ticket, state_id)


def send_fast_approval_message(title, content, receivers, ticket, state_id):
    """
    发送快速审批通知
    """

    ticket_id = ticket.id
    ticket_sn = ticket.sn

    # 更新详情url
    ticket.generate_ticket_url(state_id, receivers)

    # 构造data信息
    data = {
        "title": title,
        "summary": content,
        "approvers": str(receivers),
        "plat": settings.FRONTEND_URL,
        "key": ticket_sn,
        "clickname": "查看详情",
        "clickurl": ticket.ticket_url,
        "callback": "{}openapi/ticket/proceed_fast_approval/".format(
            settings.FRONTEND_URL
        ),
        "action": [{"name": "同意", "value": "true"}, {"name": "拒绝", "value": "false"}],
        "context": {"ticket_id": ticket_id, "state_id": state_id},
    }
    logger.info(
        "[fast_approval({})]send fast approval message data:{}".format(ticket_sn, data)
    )

    # data加密
    data = Aes(APPID, APPKEY).encrypt_dict(data)

    # 构造请求参数
    params = {"app_id": APPID, "app_key": APPKEY, "data": data}
    headers = {"Content-Type": "application/json", "IM-TOKEN": settings.IM_TOKEN}

    # 发送请求
    try:
        logger.info(
            "[tasks->notify_task] is executed, title={}, receivers={}, ticket_id={}".format(
                title, receivers, ticket_id
            )
        )
        resp_data = requests.post(url=settings.BKCHAT_URL, json=params, headers=headers)
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
        if result.get("code") != 0:
            logger.info(
                "[fast_approval({})]send fast approval message failed:{}".format(
                    ticket_sn, result.message
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
    result = Aes(APPID, APPKEY).decrypt_dict(request.body.decode("utf8"))

    # 2.对解密后的字段进行获取
    ticket_id = int(result.get("context").get("ticket_id"))
    state_id = int(result.get("context").get("state_id"))
    receiver = result.get("approver")
    approve_action = result.get("status")
    ticket = Ticket.objects.get(id=ticket_id)
    # 3.判断当前节点是否是RUNNING状态，否则通知
    current_status = Status.objects.get(state_id=state_id, ticket_id=ticket_id)
    if current_status.status != "RUNNING":
        title = "『ITSM{}』【审批失败通知】\n".format(RUNNING_ENV.get(settings.RUN_MODE, ""))
        content = "单号：{} ({})\n当前单据审批操作已被处理".format(ticket.sn, ticket.ticket_url)
        return JsonResponse(
            {
                "result": True,
                "data": None,
                "code": 0,
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
                "result": True,
                "data": None,
                "code": 0,
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
