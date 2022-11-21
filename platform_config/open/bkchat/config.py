# -*- coding: utf-8 -*-
from django.conf import settings

from common.log import logger
from itsm.component.constants import TRANSITION_OPERATE, APPROVAL_STATE
from itsm.workflow.models import State


class BaseBkchatConfig:
    def notify_fast_approval(
        self, state_id, receivers, message="", action=TRANSITION_OPERATE, **kwargs
    ):
        from itsm.ticket.tasks import notify_fast_approval_task

        """
        发送快速审批通知
        """
        if not settings.USE_BKCHAT:
            return
        # 判断当前节点是否存在
        try:
            current_state = State.objects.get(id=state_id)
        except State.DoesNotExist:
            logger.info(
                "[fast_approval]Failed to get state: state_id={}".format(state_id)
            )
            return

        # 判断当前节点是否为审批节点
        if current_state.type != APPROVAL_STATE:
            logger.info(
                "[fast_approval]The current state_id: {}, type: {}".format(
                    state_id, current_state.type
                )
            )
            return

        # 异步执行发送快速审批通知操作
        notify_fast_approval_task.apply_async(
            args=[self, state_id, receivers, message, action], kwargs=kwargs
        )
        return
