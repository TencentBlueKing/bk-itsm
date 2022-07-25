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

from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.log import logger
from itsm.component.constants import (
    ACTION_DICT,
    CLAIM_OPERATE,
    DEFAULT_BK_BIZ_ID,
    DERIVE,
    DISTRIBUTE_OPERATE,
    MASTER_SLAVE,
    RUNNING,
    TRANSITION_OPERATE,
    VIRTUAL_TICKET_ID,
    TICKET_END_STATUS,
)
from itsm.component.exceptions import CreateTicketError, ParamError
from itsm.component.utils.basic import dotted_name
from itsm.component.utils.client_backend_query import get_user_department_ids
from itsm.component.utils.conversion import format_exp_value
from itsm.role.models import UserRole
from itsm.service.models import Service
from itsm.ticket.models import Ticket, TicketGlobalVariable, TicketToTicket
from itsm.ticket_status.models import TicketStatus


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
        flow = service.workflow
        state_id = str(service.workflow.first_state["id"])
        state = service.workflow.states[str(state_id)]
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
        # create_permission_validate(service, username)

        # 获取提单节点字段详细信息
        state_fields_map = {}
        for f in state_fields:
            f.update(value=field_hash.get(f["key"], ""))
            state_fields_map.update({f["key"]: f})

        first_state_field_validate(
            state_fields_map, fields, service=service.key, **kwargs
        )


class StateOperateValidator(object):
    """认领、转单、派单"""

    def __init__(self, current_node, bk_biz_id=None):
        self.current_node = current_node
        self.action_type = None
        self.bk_biz_id = bk_biz_id

    def __call__(self, value):

        self.action_type = value["action_type"]
        action_validate_func = "%s_validate" % self.action_type.lower()
        if hasattr(self, action_validate_func):
            getattr(self, action_validate_func)(value)
        else:
            raise ParamError(_("节点暂不支持操作：{}").format(self.action_type))

    def exception_distribute_validate(self, value):
        """
        异常分配的只需要鉴权即可
        """
        return

    def distribute_validate(self, value):
        """
        分派有效性校验
        """

        if self.current_node.action_type != DISTRIBUTE_OPERATE:
            raise ParamError(
                _("当前节点无法进行【%s】操作")
                % ACTION_DICT.get(value.get("action_type", ""), _("不存在操作类型的"))
            )

        self.processor_validate(
            value, self.current_node.assignors_type, self.current_node.assignors
        )

    def claim_validate(self, value):
        """认领校验"""

        if self.current_node.action_type != CLAIM_OPERATE:
            raise ParamError(
                _("当前节点无法进行【%s】操作")
                % ACTION_DICT.get(value.get("action_type", ""), _("不存在操作类型的"))
            )

        if UserRole.is_itsm_superuser(value["processors"]):
            return

        if not self.current_node.is_operator(value["processors"]):
            raise ParamError(_("您无法认领该单据"))

    def deliver_validate(self, value):
        """转单校验"""

        if not self.current_node.can_deliver:
            raise ParamError(_("指定流程节点【{}】不支持转单操作.").format(self.current_node.name))

        if not self.current_node.status == RUNNING:
            raise ParamError(_("当前任务状态下无法转单."))

        if not value.get("action_message"):
            raise ParamError(_("转单描述信息不能为空，请重新确认."))

        self.processor_validate(
            value, self.current_node.delivers_type, self.current_node.delivers
        )

    def processor_validate(self, value, reference_processor_type, reference_processors):
        """
        操作人员的校验
        """
        processors_type = value["processors_type"]
        processors = [p for p in str(value["processors"]).split(",") if p]
        if processors_type in ["CMDB", "GENERAL"]:
            if (
                reference_processor_type != processors_type
                and reference_processor_type
                not in [
                    "OPEN",
                    "BY_ASSIGNOR",
                    "PERSON",
                ]
            ):
                # 当前的角色类型与指定不符合
                raise ParamError(_("当前分配的用户组类型不正确"))
            if (
                reference_processor_type in ["OPEN", "BY_ASSIGNOR"]
                or not reference_processors
            ):
                # 没有指定的角色或者指定了角色类型，但是没有指定角色范围
                valid_roles = [
                    str(role_id)
                    for role_id in UserRole.objects.filter(
                        role_type=processors_type
                    ).values_list("id", flat=True)
                ]
                if not set(processors).issubset(set(valid_roles)):
                    # 角色范围不在 指定的角色范围之内
                    raise ParamError(_("当前分配的用户组可能不存在"))
                return

            # 指定了角色类型和角色范围
            reference_processors = set(
                [p for p in str(reference_processors).split(",") if p]
            )
            if not set(processors).issubset(set(reference_processors)):
                # 检测当前的角色范围是否是指定范围之内
                raise ParamError(_("当前分配的部分用户组可能不存在"))

        if (
            processors_type == "PERSON"
            and reference_processor_type not in ["OPEN", "BY_ASSIGNOR"]
            and reference_processors
        ):
            # 指定了角色范围的人员信息
            valid_person = UserRole.get_users_by_type(
                self.bk_biz_id, reference_processor_type, reference_processors, self
            )

            if not set(processors).issubset(set(valid_person)):
                raise ParamError(
                    _("当前分配的部分用户可能不符合条件，请确保用户在{}中").format(",".join(set(valid_person)))
                )


def first_state_permission(fields, first_state, username):
    """是否具有提单节点权限"""
    if first_state["processors_type"] == "OPEN":
        return

    if first_state["processors_type"] == "ORGANIZATION":
        user_department_ids = get_user_department_ids(username)
        state_department_id = first_state["processors"]
        if int(state_department_id) not in user_department_ids:
            raise CreateTicketError(_("【{}】没有任务【提单】的【提交】操作权限.").format(username))
        else:
            return

    # 提单节点提交的字段bk_biz_id的值
    bk_biz_id = get_bk_biz_id(fields)

    if username in set(
        UserRole.get_users_by_type(
            bk_biz_id, first_state["processors_type"], first_state["processors"]
        )
    ):
        return

    raise CreateTicketError(_("【{}】没有任务【提单】的【提交】操作权限.").format(username))


def create_permission_validate(service, username):
    if service.display_type == "OPEN":
        return

    if username in set(
        UserRole.get_users_by_type(-1, service.display_type, service.display_role)
    ):
        return

    raise CreateTicketError(_("【{}】没有任务【提单】的【提交】操作权限.").format(username))


def first_state_field_validate(state_fields, fields, **kwargs):
    """提单节点字段校验"""
    from itsm.ticket.validators.field import field_validate

    key_value = {
        "params_" + field["key"]: format_exp_value(field.get("type"), field["value"])
        for field in fields
    }
    for field in fields:
        try:
            field_validate(field, state_fields, key_value, **kwargs)
        except ValidationError as e:
            # 友好显示报错信息
            if isinstance(e.detail, list):
                raise CreateTicketError(str(",".join(e.detail)))
            else:
                raise CreateTicketError(str(e))
        except Exception as e:
            raise CreateTicketError(str(e))


def derive_validate(username, ticket_id):
    """新建关联单据合法校验"""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        raise serializers.ValidationError({_("单据"): _("单据不存在，请联系管理员！")})

    if ticket.is_over:
        raise serializers.ValidationError({_("单据"): _("单据已结束，无法新建关联单！")})

    if not ticket.has_perm(username):
        raise serializers.ValidationError({_("单据"): _("抱歉，您没有单据操作权限，请联系管理员！")})


def bind_derive_tickets_validate(from_ticket_id, to_ticket_ids):
    """
    绑定关联单校验
    :param from_ticket_id: 主单id
    :param to_ticket_ids: 关联单id列表
    :return:
    """
    # id有效性校验
    if type(to_ticket_ids) != list:
        raise serializers.ValidationError(_("参数类型错误:[to_tickets]"))

    if from_ticket_id in to_ticket_ids:
        raise serializers.ValidationError(_("关联失败，单据不能关联自身"))

    from_ticket = Ticket.objects.get(id=from_ticket_id)

    for to_ticket_id in to_ticket_ids:
        to_ticket = Ticket.objects.get(id=to_ticket_id)

        if TicketToTicket.objects.filter(
            Q(
                Q(from_ticket_id=from_ticket_id)
                & Q(to_ticket_id=to_ticket_id)
                & Q(related_type=DERIVE)
            )
            | Q(
                Q(from_ticket_id=to_ticket_id)
                & Q(to_ticket_id=from_ticket_id)
                & Q(related_type=DERIVE)
            )
        ).exists():
            raise serializers.ValidationError(
                _("单据【{}】和【{}】已存在关联关系").format(from_ticket.sn, to_ticket.sn)
            )


def merge_validate(from_ticket_ids, to_ticket_id, operator):
    """
    母子单关联校验
    规则：1) 母子单的属于是同一个服务
         2) 关联操作的人为服务负责人或者ITSM超级管理员
    :param from_ticket_ids: 子单, 支持多个
    :param to_ticket_id: 母单
    :param operator: 操作者
    """
    if to_ticket_id == VIRTUAL_TICKET_ID:
        raise serializers.ValidationError(_("母单为必填项"))

    # 能否成为母单
    ticket_can_be_master(to_ticket_id)
    # 能否成为子单
    tickets_can_be_slave(from_ticket_ids)

    from_ticket_ids = copy.deepcopy(from_ticket_ids)
    from_ticket_ids.append(to_ticket_id)
    tickets = list(
        Ticket.objects.filter(id__in=from_ticket_ids).values(
            "id", "service_id", "flow_id"
        )
    )

    to_ticket = None
    for index, ticket in enumerate(tickets):
        if ticket["id"] == int(to_ticket_id):
            # 将母单从列表中剔除
            from_ticket_ids.pop()
            to_ticket = tickets.pop(index)
            break

    if to_ticket is None:
        raise serializers.ValidationError(_("母单不存在，请联系管理员"))

    # 关联操作的人为服务负责人或者ITSM超级管理员
    service = Service.objects.get(id=to_ticket["service_id"])
    if not (
        UserRole.is_itsm_superuser(operator) or dotted_name(operator) in service.owners
    ):
        raise serializers.ValidationError(_("抱歉，您没有关联母子单的权限"))

    for ticket in tickets:

        if ticket["flow_id"] != to_ticket["flow_id"]:
            raise serializers.ValidationError(_("母子单必须属于同一个流程版本，无法关联"))

        from_ticket_ids.pop(from_ticket_ids.index(ticket["id"]))

    if from_ticket_ids:
        logger.error("子单不存在, from_ticket_ids非法: %s" % from_ticket_ids)
        raise serializers.ValidationError(_("子单不存在，请联系管理员"))


def ticket_can_be_master(ticket_id):
    """
    是否可以成为母单
    """
    ticket = Ticket.objects.get(id=ticket_id)
    if ticket.is_slave:
        raise serializers.ValidationError(_("单据 [{}] 已经是子单，无法成为母单".format(ticket.sn)))


def tickets_can_be_slave(ticket_ids):
    """
    单据能否成为子单
    """
    # 找出其中已是母单的单据
    master_tickets = TicketToTicket.objects.filter(
        Q(related_type=MASTER_SLAVE) & Q(to_ticket_id__in=ticket_ids)
    ).all()

    if master_tickets:
        to_ticket_ids = [master_ticket.to_ticket_id for master_ticket in master_tickets]

        tickets = Ticket.objects.filter(id__in=to_ticket_ids)
        # 友好地提示那些单据是母单，无法绑定
        raise serializers.ValidationError(
            _(
                "单据 [{}] 已经是母单，无法成为子单".format(
                    ",".join([ticket.sn for ticket in tickets])
                )
            )
        )


def withdraw_validate(operator, ticket):
    """
    校验规则：提单本人，且提单后续节点尚未处理过
    """

    if not ticket.flow.is_revocable:
        # 不可撤销或者已经结束的单，直接返回
        raise serializers.ValidationError(_("抱歉，当前流程配置无法撤单，请联系服务负责人"))

    if operator != ticket.creator:
        raise serializers.ValidationError(_("抱歉，你无权撤销单据，请联系提单人"))

    if ticket.is_over:
        raise serializers.ValidationError(_("抱歉，单据已经结束，无法撤销"))

    if ticket.can_withdraw(operator):
        return

    raise serializers.ValidationError(_("抱歉，单据执行中，无法撤销"))


def supervise_validate(ticket, username):
    """督办校验"""

    if not ticket.can_supervise(username):
        raise serializers.ValidationError(_("抱歉，您无权督办"))


def terminate_validate(username, ticket, state_id, terminate_message):
    """终止单据校验"""

    status = ticket.status(state_id)

    if not status:
        raise serializers.ValidationError(_("流程节点(%s)不存在，请联系管理员.") % state_id)

    if ticket.is_slave:
        raise serializers.ValidationError(_("抱歉，子单为只读状态，无法操作"))

    if not status.is_running:
        raise serializers.ValidationError(
            _("任务处于【{}】状态，无法操作.").format(
                ",".join(
                    TicketStatus.objects.filter(
                        service_type=ticket.service, key=status.status
                    ).values_list("name", flat=True)
                )
            )
        )

    if not status.can_terminate:
        raise serializers.ValidationError(_("指定流程节点【{}】不支持终止操作.").format(status.name))

    if not status.can_operate(username):
        raise serializers.ValidationError(
            _("【{}】没有任务【{}】的操作权限.").format(username, status.name)
        )

    if not terminate_message:
        raise serializers.ValidationError(_("请输入终止原因！"))


def proceed_validate(username, ticket, fields, state_id, **kwargs):
    """
    用于验证proceed view中的data
    不适用于提单节点校验
    校验过长中会更新数据字典、API字段的choice
    """

    ticket_operate_validate(fields, state_id, ticket, username)
    ticket_fields_validate(fields, state_id, ticket, **kwargs)


def ticket_fields_validate(fields, state_id, ticket, **kwargs):
    """
    单据字段校验
    """
    from itsm.ticket.validators.field import field_validate

    # 获取处理节点字段的详细信息
    state = ticket.flow.states[str(state_id)]
    state_fields = {}
    for field_id in state["fields"]:
        field = ticket.flow.get_field(field_id)
        state_fields.update(**{field["key"]: field})

    # 单据字段用于表达式的键值对
    key_value = {
        "params_%s" % field["key"]: format_exp_value(field["type"], field["_value"])
        for field in ticket.fields.all().values("key", "type", "_value")
    }

    key_value.update(
        {
            "params_%s" % item["key"]: item["value"]
            for item in TicketGlobalVariable.objects.filter(ticket_id=ticket.id).values(
                "key", "value"
            )
        }
    )

    key_value.update(
        {
            "params_" + field["key"]: format_exp_value(field["type"], field["value"])
            for field in fields
        }
    )

    for field in fields:
        field_validate(field, state_fields, key_value, ticket=ticket, **kwargs)


def ticket_operate_validate(fields, state_id, ticket, username):
    """
    单据能否操作校验
    """
    ticket_status_validate(ticket, state_id)

    status = ticket.status(state_id)

    # TODO 暂时这样处理，等待状态功能明确
    if not status.is_running:
        raise serializers.ValidationError(
            _("任务处于【{}】状态，无法操作.").format(
                ",".join(
                    TicketStatus.objects.filter(
                        service_type=ticket.service, key=status.status
                    ).values_list("name", flat=True)
                )
            )
        )

    # 区别提单节点：1、open类型，2、业务相关，未提单成功不更新业务id
    if ticket.first_state_id == state_id:
        bk_biz_id = get_bk_biz_id(fields)
        if not status.can_first_state_operate(username, bk_biz_id):
            raise serializers.ValidationError(
                _("【{}】没有任务【{}】的【提交】操作权限.").format(username, status.name)
            )

    elif not status.can_operate(username, TRANSITION_OPERATE):
        raise serializers.ValidationError(
            _("【{}】没有任务【{}】的【提交】操作权限.").format(username, status.name)
        )


def ticket_status_validate(ticket, state_id):
    if ticket.is_slave:
        raise serializers.ValidationError(_("抱歉，子单为只读状态，无法操作"))

    if not ticket.status(state_id):
        raise serializers.ValidationError(_("流程节点(%s)不存在，请联系管理员.") % state_id)

    if ticket.current_status in TICKET_END_STATUS:
        raise serializers.ValidationError(_("单据状态为结束状态，无法继续转换"))


def get_bk_biz_id(fields):
    """提单节点提交的字段bk_biz_id的值"""
    bk_biz_id = DEFAULT_BK_BIZ_ID
    for f in fields:
        if f.get("key") == "bk_biz_id":
            bk_biz_id = f.get("value")
            return bk_biz_id

    return bk_biz_id
