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

import codecs
import copy
import csv
import datetime
import io
import json
import base64

import xlwt
from django.conf import settings
from django.core.cache import cache
from django.db import connection, transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from mako.template import Template
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from common.log import logger
from common.redis import Cache
from config.default import OUT_LINK
from itsm.component.cache_keys import ticket_cache_key
from itsm.component.constants import (
    CACHE_5MIN,
    CACHE_10MIN,
    DEFAULT_ENGINE_VERSION,
    DERIVE,
    EMAIL,
    EXPORT_FIELDS,
    FAULT_SOURCE_CHOICES,
    FIELD_PX_URGENCY,
    FIELD_PY_IMPACT,
    INVITE_OPERATE,
    MASTER_SLAVE,
    PRIORITY,
    QUEUEING,
    RUNNING,
    FINISHED,
    SERVICE_DICT,
    SERVICE_LIST,
    SMS,
    VIRTUAL_TICKET_ID,
    WEB,
    ResponseCodeStatus,
    FIELD_TITLE,
    SOURCE_TICKET,
    SOURCE_TASK,
    ACTION_STATUS_CREATED,
    SIGN_STATE,
    APPROVAL_STATE,
    PROCESSOR_CHOICES,
    OPEN,
    GENERAL,
    ORGANIZATION,
    FAST_APPROVAL_MESSAGE,
)
from itsm.component.constants.flow import EXPORT_SUPPORTED_TYPE
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.pagination import CustomPageNumberPagination
from itsm.component.exceptions import (
    ComponentCallError,
    ComponentInvokeError,
    ParamError,
    StateNotFoundError,
)
from itsm.component.notify import EmailNotifier, SmsNotifier
from itsm.component.utils.basic import better_time_or_none, dictfetchall, group_by, now
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.iadmin.contants import (
    ACTION_CHOICES_DICT,
    SUPERVISE_MESSAGE,
    SUPERVISE_OPERATE,
)
from itsm.iadmin.models import CustomNotice
from itsm.postman.models import RemoteApiInstance
from itsm.service.models import Service, ServiceCatalog
from itsm.service.validators import service_validate
from itsm.service.serializers import ServiceSerializer
from itsm.trigger.models import Action
from itsm.trigger.serializers import ActionSerializer
from itsm.task.models import Task
from itsm.ticket.models import (
    FIELD_STATUS,
    Status,
    SysDict,
    Ticket,
    TicketCommentInvite,
    TicketEventLog,
    TicketField,
    TicketSuperviseNotifyLog,
    TicketToTicket,
    SignTask,
)
from itsm.ticket.permissions import (
    TicketPermissionValidate,
    SuperuserPermissionValidate,
)
from itsm.ticket.serializers import (
    FieldSerializer,
    MasterProxyTicketSerializer,
    OldTicketStateSerializer,
    RelatedTicketSerializer,
    SimpleStatusSerializer,
    StatusSerializer,
    TicketExportSerializer,
    TicketFilterSerializer,
    TicketLogSerializer,
    TicketRetrieveSerializer,
    TicketSerializer,
    TicketStateOperateSerializer,
    TriggerStateButtonSerializer,
    UnbindHistorySerializer,
    UnmergeTicketsSerializer,
    RecentlyTicketFilterSerializer,
    TicketList,
    TicketStateOperateExceptionSerializer,
)
from itsm.ticket.tasks import clone_pipeline, start_pipeline
from itsm.ticket.utils import (
    translate_constant_2,
    translate_constant_export_fields_dict,
)
from itsm.ticket.validators import (
    bind_derive_tickets_validate,
    days_validate,
    edit_field_validate,
    email_invite_validate,
    merge_validate,
    proceed_validate,
    sms_invite_validate,
    supervise_validate,
    terminate_validate,
    withdraw_validate,
    ticket_status_validate,
)
from itsm.ticket.views.sql_file import get_my_deal_tickets_sql
from itsm.ticket_status.models import TicketStatus
from itsm.sla_engine.serializers import SlaTaskSerializer
from itsm.sla_engine.models import SlaTask


class ModelViewSet(component_viewsets.ModelViewSet):
    """按需改造DRF默认的ModelViewSet类"""

    def perform_create(self, serializer):
        """创建时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        return serializer.save(creator=username, updated_by=username)

    def perform_update(self, serializer):
        """更新时补充基础Model中的字段"""
        user = serializer.context.get("request").user
        username = getattr(user, "username", "guest")
        serializer.save(updated_by=username)


class TicketOrderingFilter(object):
    """工单自定义排序规则"""

    @staticmethod
    def current_status_order(reverse, request):
        """单据状态排序"""
        service_type = request.query_params.get("service_type")
        order_name = "-order" if reverse else "order"
        if service_type:
            ticket_status_keys = (
                TicketStatus.objects.filter(service_type=service_type)
                .order_by(order_name)
                .values_list("key", flat=True)
            )
        else:
            ticket_status_keys = (
                TicketStatus.objects.all()
                .order_by(order_name)
                .values_list("key", flat=True)
            )
        ordering = "FIELD(`current_status`, {})".format(
            ",".join(["'{}'".format(key) for key in ticket_status_keys])
        )

        return ordering

    @staticmethod
    def priority_order(reverse, request):
        """优先级自定义排序"""
        priorities = SysDict.get_data_by_key(PRIORITY)
        if reverse:
            priorities.reverse()

        ordering = "FIELD(`priority_key`, {})".format(
            ",".join(["'{}'".format(priority["key"]) for priority in priorities])
        )
        return ordering


class TicketModelViewSet(ModelViewSet):
    """工单序列化"""

    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
    permission_classes = (TicketPermissionValidate,)
    ordering_class = TicketOrderingFilter
    filter_fields = {
        "service_type": ["exact", "in"],
        "creator": ["exact", "in"],
        "title": ["exact", "contains"],
        "sn": ["exact", "contains"],
        "is_draft": ["exact"],
        "current_status": ["exact", "in"],
        "service_id": ["exact", "in"],
        "create_at": ["lte", "gte"],
        "bk_biz_id": ["exact", "in"],
    }
    ordering_fields = ("create_at", "priority_order", "current_status_order")

    def get_object(self):
        ticket = super(TicketModelViewSet, self).get_object()
        master_ticket = ticket.get_master_ticket()
        if master_ticket:
            # 母单代理单据
            master_ticket.is_master_proxy = True
            return master_ticket

        return ticket

    @action(detail=False, methods=["GET"])
    def total_count(self, request, *args, **kwargs):
        my_todo_queryset = Ticket.objects.get_todo_tickets(
            self.filter_queryset(self.get_queryset()), request.user.username
        )
        my_todo_total_count = my_todo_queryset.count()

        my_approval_queryset = Ticket.objects.get_approval_tickets(
            self.filter_queryset(self.get_queryset()), request.user.username
        )
        my_approval_total_count = my_approval_queryset.count()

        my_created_queryset = Ticket.objects.get_created_tickets(
            self.filter_queryset(self.get_queryset()), request.user.username
        )
        my_created_total_count = my_created_queryset.count()
        return Response(
            {
                "my_todo": my_todo_total_count,
                "my_approval": my_approval_total_count,
                "my_created": my_created_total_count,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """单据详情"""
        instance = self.get_object()
        is_master_proxy = getattr(instance, "is_master_proxy", False)

        # 初始化serializer的上下文
        context = self.get_serializer_context()

        # 判断是否由母单代理
        if is_master_proxy:
            serializer = MasterProxyTicketSerializer(instance, context=context)
        else:
            serializer = TicketRetrieveSerializer(instance, context=context)

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """列表查询视图
        {
            u'create_at__lte': [u'2019-08-14 00:00:00'],
            u'keyword': [u'test'],
            u'creator__in': [u'poc_admin,admin'],
            u'create_at__gte': [u'2019-07-17 00:00:00'],
            u'current_status__in': [u'RUNNING,FINISHED,'],
            u'view_type': [u'my_todo'],
            u'service_type__in': [u'request,']
        }
        """

        # 初始化serializer的上下文
        queryset = self.custom_filter_queryset(request)

        project_key = request.query_params.get("project_key", None)
        if project_key is not None:
            queryset = queryset.filter(project_key=project_key)

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = TicketList(
                page,
                username=request.user.username,
                token=request.query_params.get("token", ""),
            ).to_client_representation()
            return self.get_paginated_response(data)

        # BEP: get_serializer instead of serializer class directly
        data = TicketList(
            queryset,
            username=request.user.username,
            token=request.query_params.get("token", ""),
        ).to_client_representation()
        return Response(data)

    def custom_filter_queryset(self, request):
        """构造查询结果"""
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.exists():
            filter_serializer = TicketFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            kwargs = filter_serializer.validated_data
            queryset = Ticket.objects.get_tickets(
                request.user.username, queryset, **kwargs
            )
        return queryset

    def create(self, request, *args, **kwargs):
        # 创建单据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service = Service.objects.get(id=data["service_id"])
        print("----- create ticket get service")

        # 是否开启代提单
        meta = data.get("meta", {})
        if service.can_ticket_agency:
            username = getattr(request.user, "username", "guest")
            if username != data.get("creator"):
                meta = dict(meta, ticket_agent=username)

        # creator(实际提单人)和updated_by在serializer.to_internal_value(data)中获取
        instance = serializer.save(meta=meta)
        print("----- create ticket do_after_create begin")
        instance.do_after_create(
            request.data["fields"], request.data.get("from_ticket_id", None)
        )
        print("----- create ticket do_after_create end")
        start_pipeline.apply_async([instance])
        print("----- create ticket start_pipeline end")
        return Response({"sn": instance.sn, "id": instance.id}, status=201)

    @action(detail=True, methods=["get"])
    def get_ticket_output(self, request, *args, **kwargs):
        """
        获取单据输出
        """
        instance = self.get_object()
        return Response(instance.get_ticket_global_output(display_type="list"))

    @action(detail=False, methods=["get"])
    def get_first_state_fields(self, request, *args, **kwargs):
        """
        获取提单节点字段
        """
        service_id = request.query_params.get("service_id", None)
        if not service_id:
            raise ValidationError(_("请输入service_id"))

        # 获取对应的流程版本
        service, catalog_services = service_validate(service_id)
        field_ids = service.workflow.first_state["fields"]
        state_id = service.workflow.first_state["id"]

        fields = []
        for field_id in field_ids:
            version_field = service.workflow.get_field(field_id)
            # 忽略错误的id
            if version_field is None:
                continue

            field = copy.deepcopy(version_field)
            default = field.get("default")
            old_value = field.get("value")
            field.update(
                state_id=state_id,
                version_id=service.workflow.id,
                value=default if old_value is None else old_value,
            )
            fields.append(field)

        return Response(fields)

    @action(detail=False, methods=["post"])
    def api_field_choices(self, request):
        """
        提单节点获取api选项，保持与单据相同权限
        """
        try:
            api_instance = RemoteApiInstance._objects.get(
                id=request.data.get("api_instance_id")
            )
        except RemoteApiInstance.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": ResponseCodeStatus.OK,
                    "message": _("对应的api配置不存在，请查询"),
                    "data": [],
                }
            )
        kv_relation = request.data.pop("kv_relation", None)
        params = {
            "params_%s" % key: value
            for key, value in list(request.data.get("fields", {}).items())
        }

        return Response(api_instance.get_api_choice(kv_relation, params))

    @action(detail=False, methods=["get"])
    @cache_response(CACHE_5MIN, key_func=ticket_cache_key)
    def get_my_ticket_status(self, request, *args, **kwargs):
        """我的当前单据（我的待办+我的历史+我的申请单）的状态分布"""

        service_type = request.query_params.get("service_type")
        if not service_type:
            raise ParamError(_("服务类型参数必填"))

        ticket_status = list(
            TicketStatus.objects.filter(service_type=service_type).values_list(
                "key", flat=True
            )
        )

        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(service_type=service_type)
        if not queryset.exists():
            return Response({status: 0 for status in ticket_status})

        queryset = Ticket.objects.get_tickets(
            request.user.username, queryset=queryset, ignore_superuser=True, **kwargs
        )

        queryset = (
            queryset.values("current_status")
            .annotate(cnt=Count("current_status"))
            .order_by("current_status")
        )

        data = {item["current_status"]: item["cnt"] for item in queryset}

        return Response(data)

    @action(detail=False, methods=["get"])
    @cache_response(CACHE_5MIN, key_func=ticket_cache_key)
    def get_my_deal_tickets(self, request):
        """我处理过的单据统计视图"""

        days = request.query_params.get("days", 1)
        days = days_validate(days)

        operate_at__gte = (
            (datetime.datetime.now() - datetime.timedelta(days=days))
            .date()
            .strftime("%Y-%m-%d %H:%M:%S")
        )
        data = dictfetchall(
            connection, get_my_deal_tickets_sql, request.user.username, operate_at__gte
        )
        exist_services = map(lambda x: x["service"], data)
        for service in SERVICE_LIST:
            if service in exist_services:
                continue
            data.append({"service": service, "count": 0})

        return Response(data)

    @action(detail=True, methods=["post"])
    def send_sms(self, request, *args, **kwargs):
        """通过电话号码发送短信"""

        ticket = self.get_object()
        invitor = request.user.username
        receiver = request.data.get("receiver", "")
        numbers = receiver.split(",")

        sms_invite_validate(ticket, numbers, invitor)

        try:
            # 发送逻辑
            custom_notify = CustomNotice.objects.get(
                project_key=ticket.project_key, action=INVITE_OPERATE, notify_type=SMS
            )
        except CustomNotice.DoesNotExist:
            custom_notify = CustomNotice.objects.get(
                action=INVITE_OPERATE, notify_type=SMS, project_key="public"
            )

        content_template = (
            custom_notify.title_template + "：" + custom_notify.content_template
        )
        context = ticket.get_notify_context()
        context.update(action=ACTION_CHOICES_DICT.get(INVITE_OPERATE))

        # 发送前创建邀请记录
        links = []
        fail_numbers = []
        title = Template(custom_notify.title_template).render(**context)
        for number in numbers:
            code = TicketCommentInvite.get_unique_code()
            ticket_url = "{}{}".format(OUT_LINK, code)
            context.update(ticket_url=ticket_url)
            links.append(ticket_url)

            notifier = SmsNotifier(
                title=title,
                receivers=receiver,
                message=Template(content_template).render(**context),
                receiver_nums=number,
            )

            try:
                notifier.send()
                TicketCommentInvite.objects.create(
                    receiver=number, comment_id=ticket.comment_id, code=code
                )
            except ComponentCallError as e:
                fail_numbers.append(number)
                logger.warning("send_sms[{}] exception: {}".format(number, e))

        return Response(
            {
                "result": len(fail_numbers) == 0,
                "message": _("【{}】发送短信失败，请检查电话号码是否正确或联系管理员！").format(
                    ",".join(fail_numbers)
                )
                if fail_numbers
                else "success",
                "data": links,
                "code": "SEND_SMS_FAILED",
            }
        )

    @action(detail=True, methods=["post"])
    def send_email(self, request, *args, **kwargs):
        """通过邮件邀请评价"""

        ticket = self.get_object()
        invitor = request.user.username
        receiver = request.data.get("receiver", "")

        email_invite_validate(ticket, invitor, receiver)

        code = TicketCommentInvite.get_unique_code()

        # 构建信息
        context = ticket.get_notify_context()
        context.update(
            service_type_name=ticket.service_type_name,
            action=ACTION_CHOICES_DICT.get(INVITE_OPERATE),
            today_date=datetime.datetime.today(),
        )
        try:
            # 发送逻辑
            custom_notify = CustomNotice.objects.get(
                action=INVITE_OPERATE, notify_type=EMAIL, project_key=ticket.project_key
            )
        except CustomNotice.DoesNotExist:
            custom_notify = CustomNotice.objects.get(
                action=INVITE_OPERATE, notify_type=EMAIL, project_key="public"
            )

        ticket_url = ticket.ticket_url + "&token={token}&invite=email".format(
            token=code
        )
        context.update(ticket_url=ticket_url)
        notifier = EmailNotifier(
            title=Template(custom_notify.title_template).render(**context),
            receivers=receiver,
            message=Template(custom_notify.content_template).render(**context),
        )
        try:
            notifier.send()
            TicketCommentInvite.objects.create(
                receiver=receiver, comment_id=ticket.comment_id, code=code
            )
            return Response(
                {
                    "result": True,
                    "message": "success",
                    "data": ticket_url,
                    "code": ResponseCodeStatus.OK,
                }
            )
        except ComponentCallError as error:
            logger.warning("send email execption: %s" % error)
            return Response(
                {
                    "result": False,
                    "message": _("【{}】发送邮件失败，请检查用户邮件配置是否正确或联系管理员！").format(receiver),
                    "data": ticket_url,
                    "code": "SEND_EMAIL_FAILED",
                }
            )

    @action(detail=False, methods=["get"])
    def export_excel(self, request, *args, **kwargs):
        from itsm.ticket.serializers import FieldExportSerializer

        export_fields = request.query_params.get("export_fields")
        if not export_fields:
            raise ValidationError(_("请选择需要导出的字段"))

        export_fields = export_fields.split(",")

        queryset = self.custom_filter_queryset(request)

        fields = copy.deepcopy(EXPORT_FIELDS)
        head_fields = [field for field in fields if field["id"] in export_fields]
        ticket_fields = FieldExportSerializer(
            TicketField.objects.filter(
                ticket_id__in=queryset.values_list("id", flat=True)
            )
            .exclude(key__in=["bk_biz_id", "title"])
            .order_by("-create_at"),
            many=True,
        ).data
        ticket_releate_fields = group_by(ticket_fields, ["ticket_id"], dict_result=True)
        field_filter_conditions = set(
            [
                "{}({})".format(field_obj["name"], field_obj["state_name"])
                if field_obj["state_name"]
                else field_obj["name"]
                for field_obj in ticket_fields
            ]
        )
        relate_head_fields = [
            {"id": item, "name": item} for item in field_filter_conditions
        ]
        head_fields.extend(sorted(relate_head_fields, key=lambda x: x.get("name")))

        ticket_values_list = TicketExportSerializer(queryset, many=True).data
        for ticket_values in ticket_values_list:
            fields = ticket_releate_fields.get(ticket_values["id"], [])
            for field in fields:
                field_name = (
                    "{}({})".format(field["name"], field["state_name"])
                    if field["state_name"]
                    else field["name"]
                )
                ticket_values[field_name] = field["display_value"]

        # 构造xls并返回
        return self.generate_csv(head_fields, ticket_values_list)

    @action(detail=False, methods=["get"])
    def export_group_by_service(self, request, *args, **kwargs):
        from itsm.ticket.serializers import FieldExportSerializer

        # 单据的公共字段设置内容
        export_fields = request.query_params.get("export_fields")
        if not export_fields:
            raise ValidationError(_("请选择需要导出的字段"))

        export_fields = export_fields.split(",")

        fields = copy.deepcopy(EXPORT_FIELDS)
        head_fields = [field for field in fields if field["id"] in export_fields]

        queryset = self.custom_filter_queryset(request)

        # 这里建议用base64编码

        service_fields = request.query_params.get("service_fields")
        try:
            service_fields = (
                json.loads(base64.b64decode(service_fields)) if service_fields else {}
            )
        except BaseException:
            raise ValidationError(_("解析导出的提单字段异常：请检查请求参数内容，提单字段需要通过base64编码。"))

        # 获取字段的展示title，先将所有的字段混合起来
        all_service_field_keys = []
        for service_fields_key in service_fields.values():
            all_service_field_keys.extend(service_fields_key)

        def get_service_ticket_fields():
            """根据用户制定的字段获取提单内容"""
            if not service_fields:
                return []

            # started_states = [
            #     service_inst.first_state_id
            #     for service_inst in Service.objects.filter(id__in=service_fields.keys())
            # ]

            # 获取导出的所有字段内容 -- 当前的id如果较多，这里大量拉取，估计有点问题
            all_service_field_keys.append("bk_biz_id")
            return FieldExportSerializer(
                TicketField.objects.filter(
                    ticket_id__in=queryset.filter(
                        service_id__in=service_fields.keys()
                    ).values_list("id", flat=True),
                    type__in=EXPORT_SUPPORTED_TYPE,
                    # state_id__in=started_states,
                    key__in=all_service_field_keys,
                ),
                many=True,
            ).data

        ticket_fields = get_service_ticket_fields()
        # 按照ticket_id分组
        ticket_relate_fields = group_by(ticket_fields, ["ticket_id"], dict_result=True)

        field_filter_conditions = set(
            [
                field_obj["name"]
                for field_obj in ticket_fields
                if field_obj["key"] in all_service_field_keys
            ]
        )

        relate_head_fields = [
            {"id": item, "name": item} for item in field_filter_conditions
        ]
        head_fields.extend(sorted(relate_head_fields, key=lambda x: x.get("name")))

        ticket_values_list = TicketExportSerializer(queryset, many=True).data

        for ticket_values in ticket_values_list:
            fields = ticket_relate_fields.get(ticket_values["id"], [])
            for field in fields:
                ticket_values[field["name"]] = field["display_value"]

        # 构造csv并返回
        return self.generate_csv(head_fields, ticket_values_list)

    @staticmethod
    def generate_xls(head_fields, ticket_values_list, service_type):

        """生成文档"""
        service_type_name = SERVICE_DICT.get(service_type) or "ALL"
        sheet_name = (
            service_type_name + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M")
        )
        work_book = xlwt.Workbook(encoding="utf-8")
        work_sheet = work_book.add_sheet(sheet_name)

        for index, value in enumerate(head_fields):
            work_sheet.col(index).width = 256 * 20
            work_sheet.write(0, index, value["name"])

        for row, ticket_values in enumerate(ticket_values_list):
            for index, key in enumerate([value["id"] for value in head_fields]):
                work_sheet.write(row + 1, index, ticket_values.get(key, "--"))

        output = io.BytesIO()
        work_book.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(), content_type="application/vnd.ms-excel"
        )
        response["Content-Disposition"] = 'attachment;filename="{}.xls"'.format(
            settings.APP_CODE
        )
        return response

    @staticmethod
    def generate_csv(head_fields, ticket_values_list):
        # 新增csv导出方式

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment;filename={}.csv".format(
            settings.APP_CODE
        )
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        head = [f["name"] for f in head_fields]
        head.insert(0, "序号")
        writer.writerow(head)

        for row, ticket_values in enumerate(ticket_values_list):
            fields = [row + 1]
            for index, key in enumerate([value["id"] for value in head_fields]):
                fields.append(ticket_values.get(key, "--"))
            writer.writerow(fields)

        return response

    @action(detail=True, methods=["get"])
    def print_ticket(self, request, *args, **kwargs):
        """
        返回单据打印信息，默认到从提单节点到当前节点
        """

        ticket = self.get_object()
        if ticket.flow.engine_version == DEFAULT_ENGINE_VERSION:
            state_list = ticket.get_printable_states(request.user.username)
        else:
            state_list = ticket.get_old_ticket_state_list()

        print_data = {
            "sn": ticket.sn,
            "print_date": datetime.date.today(),
            "print_person": request.user.username,
            "type": ticket.service_type_name,
            "status": ticket.current_status_display,
            "state": state_list,
            "cata_log": ticket.catalog_fullname,
            "service": "{}工单".format(ticket.service_type_name),
            "create_at": ticket.create_at,
        }

        return Response(print_data)

    @action(detail=False, methods=["get"])
    def get_global_choices(self, request):
        """查询全局选项列表信息"""

        ticket_status = TicketStatus.objects.all().values("service_type", "key", "name")
        return Response(
            {
                "export_fields": translate_constant_export_fields_dict(EXPORT_FIELDS),
                "ticket_status": group_by(
                    ticket_status,
                    key_or_index_tuple=("service_type",),
                    dict_result=True,
                ),
                "processor_type": translate_constant_2(PROCESSOR_CHOICES),
                "fault_source": [
                    {"key": choices[0], "pk_value": _(choices[1])}
                    for choices in translate_constant_2(FAULT_SOURCE_CHOICES)
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def proceed(self, request, *args, **kwargs):
        """单据处理：节点间的处理
        处理路径操作分类介绍：
            1.节点间的处理：需要推进流程状态到下一个节点的
        """

        ticket = self.get_object()

        fields = request.data.get("fields")
        state_id = str(request.data.get("state_id", ""))

        proceed_validate(
            request.user.username,
            ticket,
            copy.deepcopy(fields),
            state_id,
            request=request,
        )
        node_status = ticket.node_status.get(state_id=state_id)
        node_status.set_history_operators(request.user.username)

        # 单据审批新增事务控制
        if node_status.type in [SIGN_STATE, APPROVAL_STATE]:
            SignTask.objects.update_or_create(
                status_id=node_status.id,
                processor=request.user.username,
                defaults={"status": "RUNNING"},
            )
        else:
            node_status.status = QUEUEING
            node_status.save()

        res = ticket.activity_callback(
            state_id, request.user.username, fields, request.source
        )
        if not res.result:
            logger.warning(
                "callback error， current state id %s, error message: %s"
                % (state_id, res.message)
            )
            ticket.node_status.filter(state_id=state_id).update(status=RUNNING)

        return Response(
            {
                "code": ResponseCodeStatus.OK
                if res.result
                else ResponseCodeStatus.FAILED,
                "message": res.message,
                "result": res.result,
            }
        )

    @action(detail=True, methods=["post"])
    def retry(self, request, *args, **kwargs):
        """
        失败的节点可以在此进行重试
        """

        ticket = self.get_object()

        inputs = request.data.get("inputs")
        state_id = str(request.data.get("state_id", ""))

        ticket_status_validate(ticket, state_id)

        ticket.node_status.filter(state_id=state_id).update(status=QUEUEING)

        res = ticket.retry_node(state_id, inputs, operator=request.user.username)

        return Response(
            {
                "code": ResponseCodeStatus.OK
                if res.result
                else ResponseCodeStatus.FAILED,
                "message": res.message,
                "result": res.result,
            }
        )

    @action(detail=True, methods=["post"])
    def ignore(self, request, *args, **kwargs):
        """
        失败的节点可以在此进行重试
        """

        ticket = self.get_object()

        ignore_data = request.data.get("inputs")
        state_id = str(request.data.get("state_id", ""))
        is_direct = request.data.get("is_direct")

        ticket_status_validate(ticket, state_id)
        if is_direct:
            res = ticket.skip_node(state_id, operator=request.user.username)
            ticket.node_status.filter(state_id=state_id).update(status=FINISHED)
        else:
            ticket.node_status.filter(state_id=state_id).update(status=QUEUEING)
            res = ticket.retry_node(
                state_id, ignore_data, action="MANUAL", operator=request.user.username
            )
        return Response(
            {
                "code": ResponseCodeStatus.OK
                if res.result
                else ResponseCodeStatus.FAILED,
                "message": res.message,
                "result": res.result,
            }
        )

    @action(
        detail=True, methods=["GET"], permission_classes=[SuperuserPermissionValidate]
    )
    def skip_node(self, request, *args, **kwargs):
        instance = self.get_object()
        transition_id = request.query_params.get("transition_id")
        state_id = request.query_params.get("state_id")
        action_result = (
            instance.skip_gateway_node(state_id, transition_id)
            if transition_id
            else instance.skip_node(state_id)
        )
        return Response(
            {"result": action_result.result, "message": action_result.message}
        )

    @action(detail=True, methods=["post"])
    def trigger_state_button(self, request, *args, **kwargs):
        """Trigger state custom button"""
        ticket = self.get_object()
        serializer = TriggerStateButtonSerializer(
            data=request.data, context={"username": request.user.username}
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        component_cls = ComponentLibrary.get_component_class(
            "trigger", validated_data["component_key"]
        )
        component = component_cls(
            context={"ticket_id": ticket.id, "state_id": validated_data["state_id"]}
        )

        # Convert inputs to key/value dicts
        input_data = {}
        inputs = validated_data.get("inputs", {})
        for key, item in inputs.items():
            input_data.update(**{key: item.get("value")})

        result = component.invoke(input_data)
        if result:
            TicketEventLog.objects.create_trigger_action_log(
                ticket,
                validated_data["status"],
                request.user.username,
                component_cls,
                input_data,
            )
            return Response()
        else:
            raise ComponentInvokeError(component.data.get_one_of_outputs("message"))

    @action(detail=True, methods=["get"])
    def trigger_actions(self, request, *args, **kwargs):
        """获取工单对应的触发器响应事件"""
        instance = self.get_object()
        operate_type = request.query_params.get("operate_type", "")

        if operate_type != "all":
            # 手动执行的，直接返回手动按钮
            return Response(
                ActionSerializer(
                    Action.objects.get_manual_trigger_actions(
                        instance.id, SOURCE_TICKET
                    ),
                    many=True,
                ).data
            )

        # 所有的内容
        task_ids = Task.objects.filter(ticket_id=instance.id).values_list("id")
        action_query_set = Action.objects.filter(
            Q(Q(source_id=instance.id) & Q(source_type=SOURCE_TICKET))
            | Q(Q(source_id__in=task_ids) & Q(source_type=SOURCE_TASK))
        ).exclude(status=ACTION_STATUS_CREATED)

        return Response(ActionSerializer(action_query_set, many=True).data)

    @action(detail=True, methods=["get"])
    def trigger_actions_group(self, request, *args, **kwargs):
        """获取工单对应的触发器响应事件"""
        instance = self.get_object()
        # 所有的内容
        task_ids = Task.objects.filter(ticket_id=instance.id).values_list("id")
        action_query_set = Action.objects.filter(
            Q(Q(source_id=instance.id) & Q(source_type=SOURCE_TICKET))
            | Q(Q(source_id__in=task_ids) & Q(source_type=SOURCE_TASK))
        ).exclude(status=ACTION_STATUS_CREATED)
        actions = ActionSerializer(action_query_set, many=True).data
        # 分组
        ticket_actions = []
        state_actions = {}
        state_map = {}
        for item in actions:
            if item["signal_type"] == "STATE":
                state_actions.setdefault(item["sender"], []).append(item)
            if item["signal_type"] == "FLOW":
                ticket_actions.append(item)

        for state_id in state_actions.keys():
            state_map[state_id] = instance.state(state_id)["name"]

        return Response(
            {
                "state": state_actions,
                "ticket_actions": ticket_actions,
                "state_map": state_map,
            }
        )

    @action(detail=True, methods=["post"])
    def terminate(self, request, *args, **kwargs):
        """单据终止"""

        ticket = self.get_object()
        state_id = request.data.get("state_id")
        terminate_message = request.data.get("terminate_message")

        terminate_validate(request.user.username, ticket, state_id, terminate_message)

        res = ticket.terminate(
            state_id,
            terminate_message=terminate_message,
            operator=request.user.username,
            source=request.source,
        )

        return Response(res)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, *args, **kwargs):
        """撤单"""

        ticket = self.get_object()

        withdraw_validate(request.user.username, ticket)
        ticket.withdraw(operator=request.user.username, source=WEB)

        return Response()

    @action(detail=True, methods=["post"])
    def supervise(self, request, *args, **kwargs):
        """督办"""

        username = request.user.username

        ticket = self.get_object()
        supervise_validate(ticket, username)

        message = request.data.get("message") or Template(SUPERVISE_MESSAGE).render(
            **{"title": ticket.title}
        )
        # 构造快速审批通知信息
        fast_approval_message = FAST_APPROVAL_MESSAGE.format(
            **ticket.get_fast_approval_message_params()
        )
        for step in ticket.current_steps:
            # 快速审批通知
            ticket.notify_fast_approval(
                step["state_id"],
                step["processors"],
                fast_approval_message,
                action=SUPERVISE_OPERATE,
                kwargs=kwargs,
            )
            ticket.notify(
                state_id=step["state_id"],
                receivers=step["processors"],
                message=message,
                action=SUPERVISE_OPERATE,
                retry=False,
            )

            for _notify in ticket.flow.notify.all():
                TicketSuperviseNotifyLog.objects.create(
                    ticket=ticket,
                    supervised=step["processors"],
                    state_id=step["state_id"],
                    state_name=step["name"],
                    creator=username,
                    message=message,
                    notify_type=_notify.type,
                )

        return Response()

    @action(detail=True, methods=["post"])
    def operate(self, request, *args, **kwargs):
        """节点操作"""

        ticket = self.get_object()

        operate_serializer = TicketStateOperateSerializer(
            request=request, ticket=ticket, operator=request.user.username
        )
        operate_serializer.is_valid(raise_exception=True)
        data = operate_serializer.data

        data["source"] = request.source
        current_node = data["current_node"]
        data["ticket"] = ticket
        current_node.set_next_action(operator=request.user.username, **data)

        return Response()

    @action(detail=True, methods=["post"])
    def exception_distribute(self, request, *args, **kwargs):
        """
        异常分派
        """
        ticket = self.get_object()

        operate_serializer = TicketStateOperateExceptionSerializer(
            request=request, ticket=ticket, operator=request.user.username
        )
        operate_serializer.is_valid(raise_exception=True)
        data = operate_serializer.data

        data["source"] = request.source
        current_node = data["current_node"]
        data["ticket"] = ticket
        current_node.set_next_action(operator=request.user.username, **data)

        return Response()

    @action(detail=True, methods=["post"])
    def suspend(self, request, *args, **kwargs):
        # 挂起操作
        ticket = self.get_object()
        if ticket.current_status == "SUSPENDED":
            raise ValidationError(_("该单据已经是挂起状态, 请勿重复操作"))

        suspend_message = request.data.get("desc", _("无"))
        ticket.suspend(suspend_message, operator=request.user.username)
        return Response()

    @action(detail=True, methods=["post"])
    def unsuspend(self, request, *args, **kwargs):
        # 恢复操作
        ticket = self.get_object()
        if ticket.current_status != "SUSPENDED":
            raise ValidationError(_("该单据不是挂起状态, 请勿重复操作"))

        ticket.unsuspend(operator=request.user.username)
        return Response()

    @action(detail=True, methods=["post"])
    def close(self, request, *args, **kwargs):
        ticket = self.get_object()
        # TODO close校验
        close_status = request.data.get("current_status")
        if close_status not in ticket.status_instance.to_over_status_keys:
            raise ValidationError(_("设置的关闭状态不在正确状态范围之内"))

        ticket.close(
            close_status=close_status,
            desc=request.data.get("desc"),
            operator=request.user.username,
        )
        return Response()

    @action(detail=True, methods=["get"])
    def fields(self, request, *args, **kwargs):
        """
        根据ticket状态id获取fields信息
        """

        state_id = self.request.query_params.get("state_id")

        # 从TicketField中获取字段
        fields = self.get_object().fields.filter(state_id=state_id)
        # BEP: 充分利用序列化类
        fields = FieldSerializer(fields, many=True).data

        return Response(fields)

    @action(detail=True, methods=["get"])
    def all_fields(self, request, *args, **kwargs):
        """获取ticket的所有fields信息"""
        # 从TicketField中获取字段
        fields = self.get_object().fields
        # BEP: 充分利用序列化类
        fields = FieldSerializer(fields, many=True).data

        return Response(fields)

    @action(detail=True, methods=["get"])
    def derive_tickets(self, request, *args, **kwargs):
        """
        获取ticket的所有新建关联单据
        来源关联单+目标关联单
        """
        # 该请求不进行母单代理
        ticket = super().get_object()

        derive_ticket_objs = TicketToTicket.objects.filter(related_type=DERIVE).filter(
            Q(from_ticket_id=ticket.id) | Q(to_ticket_id=ticket.id)
        )

        derive_ticket_ids = []
        for derive_ticket in derive_ticket_objs:
            # 目标关联单
            if derive_ticket.from_ticket_id == ticket.id:
                derive_ticket_ids.append(derive_ticket.to_ticket_id)

            # 来源关联单
            else:
                derive_ticket_ids.append(derive_ticket.from_ticket_id)

        # 初始化serializer的上下文
        context = self.get_serializer_context()

        data = TicketRetrieveSerializer(
            Ticket.objects.filter(id__in=derive_ticket_ids), many=True, context=context
        ).data

        return Response(data)

    @action(detail=True, methods=["get"])
    def master_or_slave(self, request, *args, **kwargs):
        """
        获取ticket的关联母单或者子单列表
        该单据
            若为母单, 获取子单列表
            若为子单, 获取母单列表
        """
        ticket = super().get_object()
        ret = RelatedTicketSerializer(instance=ticket).data

        master_slaves = TicketToTicket.objects.filter(related_type=MASTER_SLAVE).filter(
            Q(from_ticket_id=ticket.id) | Q(to_ticket_id=ticket.id)
        )

        if master_slaves:
            # 判断当前单据是母单还是子单
            related_type = (
                "slave"
                if master_slaves.last().from_ticket_id == ticket.id
                else "master"
            )
            master_slave_dict = {}
            for master_slave in master_slaves:
                if related_type == "slave":
                    master_slave_dict.update(
                        **{
                            str(master_slave.to_ticket_id): {
                                "bind_at": better_time_or_none(master_slave.create_at),
                                "related_status": master_slave.related_status,
                            }
                        }
                    )
                else:
                    master_slave_dict.update(
                        **{
                            str(master_slave.from_ticket_id): {
                                "bind_at": better_time_or_none(master_slave.create_at),
                                "related_status": master_slave.related_status,
                            }
                        }
                    )

            tickets = Ticket.objects.filter(id__in=master_slave_dict.keys())
            data_list = RelatedTicketSerializer(
                instance=tickets,
                context={"username": request.user.username},
                many=True,
            ).data

            for data in data_list:
                data.update(**master_slave_dict[str(data["id"])])

            ret.update(related_type=related_type, master_slave_tickets=data_list)
        # 未关联母子单
        else:
            ret.update(related_type=None, master_slave_tickets=[])

        return Response(ret)

    @action(detail=False, methods=["post"])
    def bind_derive_tickets(self, request, *args, **kwargs):
        """绑定关联单"""
        from_ticket_id = request.data.get("from_ticket")
        to_ticket_ids = request.data.get("to_tickets")

        if not Ticket.objects.get(pk=from_ticket_id).can_derive(request.user.username):
            raise ValidationError(_("无操作权限"))
        ticket_to_tickets = []

        bind_derive_tickets_validate(from_ticket_id, to_ticket_ids)

        for to_ticket_id in to_ticket_ids:
            ticket_to_tickets.append(
                TicketToTicket(
                    from_ticket_id=from_ticket_id,
                    to_ticket_id=to_ticket_id,
                    related_type=DERIVE,
                    creator=request.user.username,
                )
            )
        TicketToTicket.objects.bulk_create(ticket_to_tickets)

        return Response()

    @action(detail=False, methods=["post"])
    def unbind_derive_ticket(self, request, *args, **kwargs):
        """解绑关联单"""
        from_ticket = request.data.get("from_ticket")
        to_ticket = request.data.get("to_ticket")

        if not Ticket.objects.get(pk=from_ticket).can_derive(request.user.username):
            raise ValidationError(_("无操作权限"))

        ticket_to_ticket = TicketToTicket.objects.filter(
            Q(
                Q(from_ticket_id=from_ticket)
                & Q(to_ticket_id=to_ticket)
                & Q(related_type=DERIVE)
            )
            | Q(
                Q(from_ticket_id=to_ticket)
                & Q(to_ticket_id=from_ticket)
                & Q(related_type=DERIVE)
            )
        ).all()
        if not ticket_to_ticket:
            raise ValidationError(_("无效的关联关系"))

        ticket_to_ticket.update(
            is_deleted=True, related_status="UNBIND_SUCCESS", end_at=now()
        )

        return Response()

    def states_response(self, ticket, request, detail=False):
        state_id = request.query_params.get("state_id")

        if ticket.flow.engine_version == DEFAULT_ENGINE_VERSION:
            status = ticket.node_status

            if state_id:
                try:
                    status = status.get(state_id=state_id)
                except Status.DoesNotExist:
                    raise StateNotFoundError("state_id=%s" % state_id)

            many = not state_id

            if many and detail:
                status = status.filter(
                    ~Q(status__in=["FINISHED", "TERMINATED"])
                    | Q(state_id=ticket.first_state_id)
                )
            show_all_fields = many or status.status != "FINISHED"
            ticket_status = StatusSerializer(
                status,
                many=many,
                context={
                    "username": request.user.username,
                    "bk_biz_id": ticket.bk_biz_id,
                    "show_all_fields": show_all_fields,
                    "is_master_proxy": getattr(ticket, "is_master_proxy", False),
                },
            )
            return Response(ticket_status.data)

        # old tickets
        if state_id:
            for state in list(ticket.flow.states.values()):
                if str(state["id"]) == state_id:
                    return Response(
                        OldTicketStateSerializer(
                            state, many=False, context={"ticket": ticket}
                        ).data
                    )
        return Response(
            OldTicketStateSerializer(
                list(ticket.flow.states.values()), many=True, context={"ticket": ticket}
            ).data
        )

    @action(detail=True, methods=["get"])
    def states(self, request, *args, **kwargs):
        """
        单据节点查询
        参数：state_id，可选，若为空则返回所有当前状态
        """
        ticket = self.get_object()
        return self.states_response(ticket, request)

    @action(detail=True, methods=["get"])
    def details_states(self, request, *args, **kwargs):
        """
        单据节点查询只返回部分字段
        参数：state_id，可选，若为空则返回所有当前状态
        """
        ticket = self.get_object()
        return self.states_response(ticket, request, detail=True)

    @action(detail=True, methods=["get"])
    def states_status(self, request, *args, **kwargs):
        # 返回所有节点的from_transition_id, state_id, status 字段

        ticket = self.get_object()
        transitions_map = ticket.pipeline_data.get("transitions_map", {})
        if ticket.flow.engine_version == DEFAULT_ENGINE_VERSION:
            status_list = ticket.node_status.values(
                "id", "state_id", "status", "by_flow"
            )
            for status in status_list:
                status["from_transition_id"] = transitions_map.get(status["by_flow"])

        return Response(list(status_list))

    @action(detail=True, methods=["get"])
    def transitions(self, request, *args, **kwargs):
        """
        单据流转经过的连线列表查询
        """

        ticket = self.get_object()
        if ticket.flow.engine_version == DEFAULT_ENGINE_VERSION:
            return Response(ticket.active_transitions)

        # old tickets
        t_ids = [
            int(id)
            for id, t in list(ticket.flow.transitions.items())
            if t.get("direction") == "FORWARD"
        ]
        try:
            router_extras = [
                json.loads(state.get("extras"))
                for state in list(ticket.flow.states.values())
                if state.get("type") == "ROUTER"
            ]
        except Exception as e:
            logger.error("get active_transitions error: %s" % str(e))
            router_extras = []
        unselected = []
        for extras in router_extras:
            for transition in extras.get("transitions", []):
                if transition.get("selected") is not True:
                    unselected.append(transition.get("id"))
        return Response(list(set(t_ids).difference(unselected)))

    @action(
        detail=False,
        methods=["get"],
        pagination_class=CustomPageNumberPagination,
        serializer_class=TicketLogSerializer,
        queryset=Ticket.objects.filter(is_draft=False),
        permission_classes=(),
    )
    def get_ticket_log(self, request, *args, **kwargs):

        ticket_id = request.query_params.get("ticket_id")
        if ticket_id:
            ticket = get_object_or_404(self.queryset, pk=ticket_id)
            ticket_serializer = self.serializer_class(ticket)
            return Response(ticket_serializer.data)

        queryset = self.queryset

        if self.request.query_params.get("catalog_id"):
            catalog_ids = ServiceCatalog.get_descendant_ids(
                self.request.query_params.get("catalog_id")
            )
            queryset = queryset.filter(catalog_id__in=catalog_ids)

        start_time = self.request.query_params.get("create_at__gte")
        if start_time:
            queryset = queryset.filter(create_at__gte=start_time)

        end_time = self.request.query_params.get("create_at__lte")
        if end_time:
            queryset = queryset.filter(create_at__lte=end_time)

        field_key = self.request.query_params.get("field_key", "")
        paginate_queryset = self.paginate_queryset(queryset=queryset)
        serializer = self.serializer_class(
            paginate_queryset, many=True, context={"field_key": field_key}
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["post"])
    def merge_tickets(self, request, *args, **kwargs):
        """绑定母子单"""

        data = request.data
        from_ticket_ids = [int(x) for x in data.get("from_ticket_ids", [])]
        to_ticket_id = int(data.get("to_ticket_id", VIRTUAL_TICKET_ID))
        merge_validate(from_ticket_ids, to_ticket_id, request.user.username)

        with transaction.atomic():
            # 若重复关联母子单，则先清空旧的母子单关联关系
            TicketToTicket.objects.filter(
                from_ticket_id__in=from_ticket_ids, related_type=MASTER_SLAVE
            ).delete()

            bulk_list = []
            for from_ticket_id in from_ticket_ids:
                bulk_list.append(
                    TicketToTicket(
                        from_ticket_id=from_ticket_id,
                        to_ticket_id=to_ticket_id,
                        related_type=MASTER_SLAVE,
                        creator=request.user.username,
                    )
                )
            TicketToTicket.objects.bulk_create(bulk_list)

        return Response()

    @action(detail=False, methods=["post"])
    def unmerge_tickets(self, request, *args, **kwargs):
        """解绑母子单"""
        data = request.data
        # 参数校验
        serializer = UnmergeTicketsSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        master_ticket = Ticket.objects.get(id=validated_data["master_ticket_id"])
        slave_tickets = Ticket.objects.filter(id__in=validated_data["slave_ticket_ids"])

        for slave_ticket in slave_tickets:
            TicketToTicket.raw_objects.filter(
                from_ticket_id=slave_ticket.id,
                to_ticket_id=validated_data["master_ticket_id"],
            ).update(related_status="RUNNING")
            clone_pipeline.apply_async(args=(slave_ticket, master_ticket))

        return Response()

    @action(detail=True, methods=["get"])
    def unbind_history(self, request, *args, **kwargs):
        """解绑历史"""
        # 参数校验
        ticket = super().get_object()
        serializer = UnbindHistorySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        unbind_histories = (
            TicketToTicket.raw_objects.filter(
                related_type=validated_data["related_type"],
                related_status="UNBIND_SUCCESS",
            )
            .filter(Q(from_ticket_id=ticket.id) | Q(to_ticket_id=ticket.id))
            .values(
                "from_ticket_id",
                "to_ticket_id",
                "from_ticket__sn",
                "to_ticket__sn",
                "create_at",
                "end_at",
            )
        )

        ret = []
        for unbind_history in unbind_histories:
            data = {}
            if unbind_history["from_ticket_id"] == ticket.id:
                # 母子单关联, 额外判断关联单据是母单还是子单
                if validated_data["related_type"] == MASTER_SLAVE:
                    data.update(related_type="master")
                ticket_id = unbind_history["to_ticket_id"]
                sn = unbind_history["to_ticket__sn"]
            else:
                if validated_data["related_type"] == MASTER_SLAVE:
                    data.update(related_type="slave")
                ticket_id = unbind_history["from_ticket_id"]
                sn = unbind_history["from_ticket__sn"]

            data.update(
                id=ticket_id,
                sn=sn,
                create_at=better_time_or_none(unbind_history["create_at"]),
                end_at=better_time_or_none(unbind_history["end_at"]),
            )
            ret.append(data)

        return Response(ret)

    @action(detail=True, methods=["get"])
    def table_fields(self, request, *args, **kwargs):
        """获取公共字段"""
        ticket = self.get_object()
        return Response(FieldSerializer(ticket.table_fields(), many=True).data)

    @action(detail=True, methods=["get"])
    def is_processor(self, request, *args, **kwargs):
        ticket = self.get_object()
        step_id = request.query_params.get("step_id", None)
        processed_user = ""
        is_processor = False
        if step_id:
            step_ids = step_id.split(",")
            status_list = ticket.node_status.filter(id__in=step_ids)
            for status in status_list:
                if request.user.username in status.get_processors():
                    is_processor = True
                    processed_user = status.processed_user
                    break

        return Response(
            {"is_processor": is_processor, "processed_user": processed_user}
        )

    @action(detail=True, methods=["post"])
    def edit_field(self, request, *args, **kwargs):
        """单个修改字段值"""

        form_data = []

        def edit_field_tracker(field_instance, old):
            """基础字段修改日志记录"""

            new_data = copy.deepcopy(FieldSerializer(field_instance).data)
            old_field_instance = copy.deepcopy(field_instance)
            old_field_instance._value = old
            old_data = copy.deepcopy(FieldSerializer(old_field_instance).data)
            old_data.update({"value_status": "before"})
            new_data.update({"value_status": "after"})

            form_data.extend([old_data, new_data])

        field = request.data.get("field")
        ticket = self.get_object()
        validate_data, field_obj = edit_field_validate(
            field, service=ticket.service_type
        )
        field_value = validate_data["value"]

        update_data = {"_value": field_value}
        if validate_data.get("choice"):
            update_data.update(choice=validate_data["choice"])

        old_value = field_obj.value

        ticket.fields.filter(key=field_obj.key).update(**update_data)

        field_obj.refresh_from_db()

        # 公共字段修改记录
        edit_field_tracker(field_obj, old_value)

        # 修改了紧急程度或影响范围，重新计算优先级
        if field_obj.key in [FIELD_PX_URGENCY, FIELD_PY_IMPACT]:
            impact = urgency = None
            if field_obj.key == FIELD_PX_URGENCY:
                urgency = field_value
            elif field_obj.key == FIELD_PY_IMPACT:
                impact = field_value

            priority_data = ticket.update_priority(urgency, impact)
            if priority_data:
                # 存在优先级修改记录的时候才进行跟踪
                edit_field_tracker(
                    priority_data["instance"], priority_data["old_value"]
                )

            ticket.refresh_sla_task()

        # 修改了工单状态
        if field_obj.key == FIELD_STATUS and ticket.current_status != field_value:
            if field_value in ticket.status_instance.to_over_status_keys:
                # 如果是结束状态，直接结束
                ticket.close(
                    close_status=field_value,
                    desc=request.data.get("desc"),
                    operator=request.user.username,
                )
                return Response()
            ticket.update_current_status(field_value)

        # 修改了title，同步修改工单title
        if field_obj.key == FIELD_TITLE:
            ticket.title = field_value
            ticket.save()

        TicketEventLog.objects.create_log(
            ticket,
            0,
            request.user.username,
            "EDIT_FIELD",
            message="{operator} 修改字段【{detail_message}】.",
            detail_message=field_obj.name,
            fields=form_data,
            to_state_id=0,
        )

        return Response()

    @action(detail=False, methods=["post"])
    def batch_approval(self, request, *args, **kwargs):
        """批量审批"""
        result = request.data.get("result")
        opinion = request.data.get("opinion")
        approval_list = request.data.get("approval_list", [])
        user = request.user.username
        for ticket_info in approval_list:
            ticket = Ticket.objects.get(id=ticket_info["ticket_id"])
            running_approval_status = ticket.node_status.filter(
                status=RUNNING, type=APPROVAL_STATE
            )
            for node_status in running_approval_status:
                if user in node_status.get_processor_in_sign_state():
                    SignTask.objects.update_or_create(
                        status_id=node_status.id,
                        processor=user,
                        defaults={"status": "RUNNING"},
                    )
                    cache.set(
                        "approval_status_{}_{}_{}".format(
                            user, ticket_info["ticket_id"], node_status.state_id
                        ),
                        "RUNNING",
                        CACHE_10MIN,
                    )
                    res = ticket.activity_callback(
                        node_status.state_id,
                        request.user.username,
                        node_status.approval_result(result, opinion),
                        request.source,
                    )
                    if not res.result:
                        logger.warning(
                            "callback error， current state id %s, error message: %s"
                            % (node_status.state_id, res.message)
                        )
                        cache.delete(
                            "approval_status_{}_{}_{}".format(
                                user, ticket_info["ticket_id"], node_status.state_id
                            )
                        )
        return Response()

    @action(detail=True, methods=["post"])
    def add_follower(self, request, *args, **kwargs):
        """关注or取关"""
        ticket = self.get_object()
        attention = request.data.get("attention")
        if attention:
            ticket.add_follower(request.user.username)
        else:
            ticket.delete_follower(request.user.username)
        return Response()

    @action(detail=True, methods=["get"], serializer_class=SlaTaskSerializer)
    def sla_task(self, request, *args, **kwargs):
        """工单sla任务查询"""
        ticket_id = kwargs.get("pk")
        sla_tasks = SlaTask.objects.filter(ticket_id=ticket_id)
        serializer = self.serializer_class(sla_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reply(self, request, *args, **kwargs):
        ticket = self.get_object()
        state_id = request.data.get("state_id")
        ticket.reply(state_id)
        return Response()

    @action(detail=True, methods=["get"])
    def ticket_base_info(self, request, *args, **kwargs):
        """提单信息"""
        ticket = self.get_object()
        return Response(ticket.base_info())

    @action(detail=False, methods=["get"])
    def recently_used_service(self, request, *args, **kwargs):
        filter_serializer = RecentlyTicketFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filter_kwargs = filter_serializer.validated_data
        tickets = self.queryset.filter(
            creator=self.request.user.username, **filter_kwargs
        ).values_list("service_id")
        service_ids = set([ticket[0] for ticket in tickets])
        services = Service.objects.filter(
            id__in=service_ids,
            display_type__in=[OPEN, GENERAL, ORGANIZATION],
            is_valid=True,
        )
        serializer = ServiceSerializer(
            services, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_approval_ticket(self, request, *args, **kwargs):
        tickets = Ticket.objects.get_approval_tickets(
            self.queryset, request.user.username
        )
        context = self.get_serializer_context()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(tickets, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def operate_check(self, request, *args, **kwargs):
        user = request.user.username
        content = Cache().get(request.query_params.get("cache_key"))
        processed_user = ""
        if content:
            content = json.loads(content)
            status = Status.objects.get(
                ticket_id=content["ticket_id"], state_id=content["state_id"]
            )
            if (
                user not in status.ticket.real_current_processors
                and user in status.get_processors()
            ):
                processed_user = status.processed_user
                if user not in processed_user.split(","):
                    return Response(
                        {"is_processed": True, "processed_user": processed_user}
                    )
        return Response({"is_processed": False, "processed_user": processed_user})

    @action(detail=False, methods=["get"])
    def tickets_processors(self, request, *args, **kwargs):
        ticket_ids = request.query_params.get("ids", "").split(",")
        processors = Ticket.get_ticket_current_processors(ticket_ids)
        return Response(
            {
                ticket_id: ",".join(processors.get(int(ticket_id), []))
                for ticket_id in ticket_ids
            }
        )

    @action(detail=False, methods=["get"])
    def tickets_creator(self, request, *args, **kwargs):
        ticket_ids = request.query_params.get("ids", "").split(",")
        ticket_list = self.queryset.filter(id__in=ticket_ids)
        creator = get_bk_users(
            format="dict", users=list(set([ticket.creator for ticket in ticket_list]))
        )
        return Response(creator)

    @action(detail=False, methods=["get"])
    def tickets_can_operate(self, request, *args, **kwargs):
        ticket_ids = request.query_params.get("ids", "").split(",")
        ticket_list = self.queryset.filter(id__in=ticket_ids)
        can_operate = {
            ticket.id: ticket.can_operate(request.user.username)
            for ticket in ticket_list
        }
        return Response(can_operate)

    @action(detail=False, methods=["get"])
    def batch_waiting_approve(self, request, *args, **kwargs):
        ticket_ids = request.query_params.get("ticket_ids", "").split(",")
        count = Ticket.get_batch_waiting_count(ticket_ids, request.user.username)
        return Response({"count": count})

    @action(detail=False, methods=["post"])
    def get_filter_tickets(self, request, *args, **kwargs):
        """
        url: "/api/ticket/receipts/get_filter_tickets/?page_size=10&page=1&ordering=-create_at"
        data: {
            "project_key": "0",
            "tab_conditions": {},
            "extra_conditions": {}
        }
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 1.按项目key进行筛选
        project_key = request.data.get("project_key", None)
        if project_key:
            queryset = queryset.filter(project_key=project_key)

        # 2.按tab自定义条件进行筛选
        tab_filter = TicketFilterSerializer(data=request.data.get("tab_conditions"))
        tab_filter.is_valid(raise_exception=True)
        kwargs = tab_filter.validated_data
        queryset = Ticket.objects.get_tickets(request.user.username, queryset, **kwargs)

        # 3.在tab筛选的queryset基础上进行额外条件的筛选
        extra_filter = TicketFilterSerializer(data=request.data.get("extra_conditions"))
        extra_filter.is_valid(raise_exception=True)
        extra_kwargs = extra_filter.validated_data
        queryset = Ticket.objects.get_tickets(
            request.user.username, queryset, **extra_kwargs
        )

        # 4.获取分页数据
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = TicketList(
                page,
                username=request.user.username,
                token=request.query_params.get("token", ""),
            ).to_client_representation()
            return self.get_paginated_response(data)

        data = TicketList(
            queryset,
            username=request.user.username,
            token=request.query_params.get("token", ""),
        ).to_client_representation()
        return Response(data)


class TicketStatusModelViewSet(component_viewsets.ReadOnlyModelViewSet):
    serializer_class = SimpleStatusSerializer
    queryset = Status.objects.all()
