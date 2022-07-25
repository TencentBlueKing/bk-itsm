# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from itsm.ticket.validators import (
    derive_validate,
    CreateTicketError,
    first_state_permission,
    first_state_field_validate,
)
from itsm.workflow.models import WorkflowVersion


class CreateTicketValidator(object):
    def __init__(self, request):
        self.request = request

    def __call__(self, value):
        operator = value["creator"]

        # 判断是否为新建关联单
        from_ticket_id = self.request.data.get("from_ticket_id")
        if from_ticket_id:
            derive_validate(operator, from_ticket_id)

        # 获取参数
        fields = self.request.data.get("fields", None)
        if not fields:
            raise CreateTicketError(_("fields字段未填"))

        # 验证fields参数以及提单的权限
        self.create_validate(value, fields, operator, request=self.request)

    def create_validate(self, value, fields, username, **kwargs):
        """
        用于验证proceed view中的data
        :param: fields 字段列表(API传参)
        """
        service = value.pop("service", None)
        flow_id = value.pop("flow_id", None)
        try:
            flow = WorkflowVersion.objects.get(id=flow_id)
        except WorkflowVersion.DoesNotExist:
            raise CreateTicketError(
                _("单据创建失败，flow_id 对应的流程版本不存在, flow_id={}".format(flow_id))
            )

        if flow.workflow_id != service.workflow.workflow_id:
            raise CreateTicketError(
                _("单据创建失败，flow_id对应的流程与该服务绑定的流程不一致，flow_id:{}".format(flow_id))
            )

        state_id = str(flow.first_state["id"])
        state = flow.states[str(state_id)]
        state_fields = flow.get_state_fields(state_id)

        # 必填字段校验
        field_keys = set()
        field_hash = {}

        required_fields = filter(
            lambda f: f["validate_type"] == "REQUIRE", state_fields
        )
        required_keys = {f["key"] for f in required_fields}

        for f in fields:
            field_keys.add(f["key"])
            field_hash[f["key"]] = f["value"]

        lost_keys = required_keys - field_keys
        if lost_keys:
            raise CreateTicketError(_("单据创建失败，缺少参数：{}".format(list(lost_keys))))

        first_state_permission(fields, state, username)

        # 获取提单节点字段详细信息
        state_fields_map = {}
        for f in state_fields:
            f.update(value=field_hash.get(f["key"], ""))
            state_fields_map.update({f["key"]: f})

        first_state_field_validate(
            state_fields_map, fields, service=service.key, **kwargs
        )
