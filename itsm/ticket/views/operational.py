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

from datetime import datetime, timedelta
from functools import reduce

from django.db import connection
from django.db.models import Count, Q, Case, When, Max
from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from dateutil.relativedelta import relativedelta
from itsm.component.constants import CLAIM_OPERATE, DISTRIBUTE_OPERATE, SERVICE_LIST, \
    TRANSITION_OPERATE, SYSTEM_OPERATE
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.drf.pagination import CustomPageNumberPagination
from itsm.component.exceptions import ParamError
from itsm.component.drf.permissions import IamAuthSystemPermit
from itsm.component.utils.basic import dictfetchall, group_by
from itsm.component.utils.client_backend_query import get_biz_names
from itsm.component.utils.misc import (
    get_days,
    get_month_list,
    transform_single_username,
)
from itsm.component.utils.user_count import user_count, get_user_statistics
from itsm.ticket.models import Ticket, TicketComment, TicketEventLog, TicketField, TicketStatus, \
    TicketOrganization
from itsm.ticket.serializers import (
    CommentSerializer,
    OperationalDataTicketSerializer,
    TicketOrganizationSerializer,
    StatisticsFilterSerializer,
    StatisticsSerializer,
    BaseFilterSerializer,
    ServiceStatisticsFilterSerializer,
)
from itsm.ticket.handlers import ProjectOperationalData
from itsm.service.models import Service, ServiceCategory
from itsm.workflow.models import Workflow
from itsm.workflow.serializers import OperationalDataWorkflowSerializer

from .sql_file import (
    response_sql,
    service_response_sql,
    service_solve_sql,
    service_ticket_score_sql,
    solve_sql,
    ticket_score_sql,
)


class OperationalDataViewSet(component_viewsets.ReadOnlyModelViewSet):
    """运营数据视图"""

    pagination_class = CustomPageNumberPagination
    queryset = Ticket.objects.all()
    permission_classes = (IamAuthSystemPermit,)
    enable_safe_method = False
    filter_fields = {
        "create_at": ["lte", "gte", "lt", "gt"],
    }
    ordering_fields = ('create_at', 'priority_order', 'current_status_order')

    @action(detail=False, methods=["get"])
    def overview_count(self, request, *args, **kwargs):
        service_id = request.query_params.get("service_id", None)
        scope = request.query_params.get("scope", None)
        project_key = request.query_params.get("project_key", None)
        project_analysis = ProjectOperationalData(service_id, scope, project_key)
        return Response(
            {
                "count": project_analysis.get_ticket_count(),
                "service_count": 1 if service_id else project_analysis.get_service_count(),
                "biz_count": project_analysis.get_biz_count(),
                "user_count": project_analysis.get_ticket_user_count() if service_id else user_count(project_key=project_key),
            }
        )

    @action(detail=False, methods=["get"])
    def compared_same_week(self, request):
        now = datetime.now()
        # 今天零点
        zero_now = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                   microseconds=now.microsecond)
        # 本周第一天和今天
        this_week_start = zero_now - timedelta(days=zero_now.weekday())
        this_week_end = now

        # 上周第一天和上周今天
        last_week_start = zero_now - timedelta(days=zero_now.weekday() + 7)
        last_week_end = now - timedelta(days=7)

        service_id = request.query_params.get("service_id", None)
        project_key = request.query_params.get("project_key", None)
        this_scope = (this_week_start, this_week_end)
        last_scope = (last_week_start, last_week_end)

        this_week_project_analysis = ProjectOperationalData(service_id, this_scope, project_key)
        last_week_project_analysis = ProjectOperationalData(service_id, last_scope, project_key)

        this_week_ticket_count = this_week_project_analysis.get_ticket_count()
        last_week_ticket_count = last_week_project_analysis.get_ticket_count()
        ticket_ratio = round(
            (this_week_ticket_count - last_week_ticket_count) / (last_week_ticket_count or 1) * 100,
            2)

        this_week_service_count = 1 if service_id else this_week_project_analysis.get_service_count()
        last_week_service_count = 1 if service_id else last_week_project_analysis.get_service_count()
        service_ratio = round(
            (this_week_service_count - last_week_service_count) / (
                    last_week_service_count or 1) * 100, 2
        )

        this_week_biz_count = this_week_project_analysis.get_biz_count()
        last_week_biz_count = last_week_project_analysis.get_biz_count()
        biz_ratio = round(
            (this_week_biz_count - last_week_biz_count) / (last_week_biz_count or 1) * 100, 2)

        this_week_user_count = (
            this_week_project_analysis.get_ticket_user_count() if service_id else user_count(
                this_week=this_scope, project_key=project_key)
        )
        last_week_user_count = (
            last_week_project_analysis.get_ticket_user_count() if service_id else user_count(
                last_week=last_scope, project_key=project_key)
        )
        user_ratio = round(
            (this_week_user_count - last_week_user_count) / (last_week_user_count or 1) * 100, 2)

        return Response(
            {
                "ticket": {
                    "this_week_count": this_week_ticket_count,
                    "last_week_count": last_week_ticket_count,
                    "ratio": "{}%".format(ticket_ratio),
                },
                "service": {
                    "this_week_count": this_week_service_count,
                    "last_week_count": last_week_service_count,
                    "ratio": "{}%".format(service_ratio),
                },
                "biz": {
                    "this_week_count": this_week_biz_count,
                    "last_week_count": last_week_biz_count,
                    "ratio": "{}%".format(biz_ratio),
                },
                "user": {
                    "this_week_count": this_week_user_count,
                    "last_week_count": last_week_user_count,
                    "ratio": "{}%".format(user_ratio),
                },
            }
        )

    @action(detail=False, methods=["get"])
    def service_statistics(self, request):
        # "select service_id, count(*) as count, count(distinct creator),  "
        # "count(distinct case when bk_biz_id>-1 then bk_biz_id else null end) "
        # "from `ticket_ticket` where create_at BETWEEN '{}' AND '{}' "
        # "group by service_id order by {} {} limit 0,10;".format(kwargs["create_at__gte"],
        #                                                         kwargs["create_at__lte"],
        #                                                         "count", "desc"))
        project_key = request.query_params.get("project_key", None)
        filter_serializer = StatisticsSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data

        services = Service.objects.filter()
        service_name = kwargs.pop("service_name", "")
        if project_key:
            services = services.filter(project_key=project_key)
        if service_name:
            services = services.filter(name__icontains=service_name)
        services = services.values("id", "name", "key")
        service_dict = {service["id"]: {"name": service["name"], "key": service["key"]} for service
                        in services}

        service_category = ServiceCategory.objects.all().values("key", "name")
        category_dict = {category["key"]: category["name"] for category in service_category}

        order = kwargs.pop("order_by")

        ticket_info = (
            self.queryset.filter(**kwargs)
                .filter(service_id__in=service_dict.keys())
                .values("service_id")
                .annotate(
                count=Count("id"),
                creator_count=Count("creator", distinct=True),
                biz_count=Count(Case(When(bk_biz_id__gt=-1, then='bk_biz_id')), distinct=True),
            )
                .order_by(order)
        )

        service_info = []
        ticket_count = sum([ticket["count"] for ticket in ticket_info])
        ticket_info = self.paginate_queryset(ticket_info)
        for ticket in ticket_info:
            service_info.append(
                {
                    "service_id": ticket["service_id"],
                    "service_name": service_dict[ticket["service_id"]]["name"],
                    "category": category_dict[service_dict[ticket["service_id"]]["key"]],
                    "count": ticket["count"],
                    "creator_count": ticket["creator_count"],
                    "biz_count": ticket["biz_count"],
                    "ratio": "{}%".format(round(ticket["count"] / ticket_count * 100, 2)),
                }
            )
        return self.get_paginated_response(service_info)

    @action(detail=False, methods=["get"])
    def biz_statistics(self, request):
        project_key = request.query_params.get("project_key", None)
        filter_serializer = StatisticsSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        biz_id = kwargs.pop("biz_id", "")
        biz_names = get_biz_names()
        order = kwargs.pop("order_by")

        queryset = self.queryset.filter(**kwargs).filter(bk_biz_id__gt=-1)
        if project_key:
            queryset = queryset.filter(project_key=project_key)
        if biz_id:
            queryset = queryset.filter(bk_biz_id__in=biz_id.split(","))

        ticket_info = (
            queryset.values("bk_biz_id")
                .annotate(count=Count("id"), service_count=Count("service_id", distinct=True))
                .order_by(order)
        )
        ticket_info = self.paginate_queryset(ticket_info)
        biz_info = []
        for ticket in ticket_info:
            biz_info.append(
                {
                    "bk_biz_id": ticket["bk_biz_id"],
                    "bk_biz_name": biz_names.get(str(ticket["bk_biz_id"]), ""),
                    "count": ticket["count"],
                    "service_count": ticket["service_count"],
                }
            )
        return self.get_paginated_response(biz_info)

    @action(detail=False, methods=["get"])
    def category_statistics(self, request):
        project_key = request.query_params.get("project_key", None)
        filter_serializer = StatisticsSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        order = kwargs.pop("order_by")
        service_category = ServiceCategory.objects.all().values("key", "name")
        category_dict = {category["key"]: category["name"] for category in service_category}

        ticket_info = self.queryset.filter(**kwargs).values("service_type").annotate(
            count=Count("id")).order_by(order)
        if project_key:
            ticket_info = ticket_info.filter(project_key=project_key)
        category_info = [
            {"service_type": category_dict[ticket["service_type"]], "count": ticket["count"]} for
            ticket in ticket_info
        ]

        return Response(category_info)

    @action(detail=False, methods=["get"])
    def status_statistics(self, request):
        project_key = request.query_params.get("project_key", None)
        filter_serializer = BaseFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        not_running_status = ["FINISHED", "TERMINATED", "REVOKED"]
        ticket_info = (
            self.queryset.filter(**kwargs).values("current_status").annotate(
                count=Count("id")).order_by("-count")
        )
        if project_key:
            ticket_info = ticket_info.filter(project_key=project_key)
        category_info = {}
        for ticket in ticket_info:
            if ticket["current_status"] in not_running_status:
                category_info[ticket["current_status"]] = {"status": ticket["current_status"],
                                                           "count": ticket["count"]}
                continue
            if "RUNNING" not in category_info:
                category_info["RUNNING"] = {"status": "RUNNING", "count": ticket["count"]}
            else:
                category_info["RUNNING"]["count"] += ticket["count"]

        return Response(list(category_info.values()))

    @action(detail=False, methods=["get"])
    def resource_count_statistics(self, request):
        project_key = request.query_params.get("project_key", None)
        filter_serializer = StatisticsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        time_delta = kwargs.pop("timedelta")
        resource_type = kwargs.pop("resource_type")
        if project_key:
            kwargs.update({"project_key": project_key})
        statistics = {
            "creator": Ticket.get_creator_statistics,
            "ticket": Ticket.get_ticket_statistics,
            "user": get_user_statistics,
            "service": Service.get_service_statistics,
        }
        dates_range = statistics[resource_type](time_delta, kwargs)
        return Response(dates_range)

    @action(detail=False, methods=["get"])
    def service_count_statistics(self, request):
        project_key = request.query_params.get("project_key", None)
        filter_serializer = ServiceStatisticsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data

        time_delta = kwargs.pop("timedelta")
        resource_type = kwargs.pop("resource_type")
        if project_key:
            kwargs.update({"project_query": project_key})

        statistics = {
            "ticket": Ticket.get_ticket_statistics,
            "biz": Ticket.get_biz_statistics,
        }
        dates_range = statistics[resource_type](time_delta, kwargs)
        return Response(dates_range)

    @action(detail=False, methods=["get"])
    def top_creator_statistics(self, request):
        # select username,first_level_name,family from ticket_ticket where id in
        # (select max( id ) from ticket_ticket group by username)
        project_key = request.query_params.get("project_key", None)
        filter_serializer = ServiceStatisticsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        kwargs.pop("timedelta")
        max_ids = (
            TicketOrganization.objects.filter(
                create_at__gte=kwargs["create_at__gte"], create_at__lte=kwargs["create_at__lte"]
            )
                .values("username", "first_level_id")
                .annotate(id=Max("id"))
                .order_by("username")
        )
        max_ids = [ticket['id'] for ticket in max_ids]
        user_organization = TicketOrganization.objects.filter(id__in=max_ids).only(
            "username", "first_level_name", "family"
        )
        user_info = {}
        for user in user_organization:
            if user.username not in user_info:
                user_info[user.username] = [{"name": user.first_level_name, "family": user.family}]
            else:
                user_info[user.username].append(
                    {"name": user.first_level_name, "family": user.family})
                
        project_query = Q(project_key=project_key) if project_key else Q()

        ticket_info = (
            self.queryset.filter(project_query).filter(**kwargs).values("creator").annotate(count=Count("id")).order_by(
                "-count")[:10]
        )
        top_creator = [
            {
                "organization": user_info.get(ticket["creator"], []),
                "count": ticket["count"],
                "creator": ticket["creator"],
            }
            for ticket in ticket_info
        ]

        return Response(top_creator)

    @action(detail=False, methods=["get"])
    def distribute_statistics(self, request):
        filter_serializer = TicketOrganizationSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        kwargs = filter_serializer.validated_data
        level_dict = {
            1: ("first_level_id", "first_level_name"),
            2: ("second_level_id", "second_level_name"),
            3: ("third_level_id", "third_level_name"),
        }

        level = kwargs.pop("level")

        ticket_info = (
            TicketOrganization.objects.filter(**kwargs)
                .values(level_dict[level][0], level_dict[level][1])
                .annotate(count=Count("id"))
                .order_by("-count")
        )
        top_creator = [
            {"organization": ticket[level_dict[level][1]], "count": ticket["count"]} for ticket in
            ticket_info[:10]
        ]

        return Response(top_creator)

    @action(detail=False, methods=["get"])
    def sync_organization(self, request):
        Ticket.sync_organization_ticket()
        return Response({})

    @staticmethod
    def get_time_params(request, params_key="create_at"):
        """获取create_at查询条件"""
        time_params = {
            key: item.replace("&nbsp;", " ")
            for key, item in request.query_params.items()
            if key.startswith(params_key + "__") and item
        }

        if not time_params:
            return time_params

        try:
            time_params[params_key + "__gte"] = time_params[params_key + "__gte"] + " 00:00:00"
            time_params[params_key + "__lte"] = time_params[params_key + "__lte"] + " 23:59:59"
            return time_params
        except KeyError:
            raise ValidationError(
                _("日期范围输入有误，请重新输入，例如：{}__gte=2019-01-01, {}__lte=2019-01-02").format(params_key,
                                                                                     params_key)
            )

    @staticmethod
    def get_month_params(queryset, request):
        """获取create_at月份信息"""
        create_at_params = {
            key: item.replace("&nbsp;", " ")
            for key, item in request.query_params.items()
            if key.startswith("create_at__") and item
        }

        try:
            if create_at_params.get("create_at__gte"):
                create_at_params["create_at__gte"] = datetime.strptime(
                    create_at_params["create_at__gte"], "%Y-%m")
            else:
                create_at_params["create_at__gte"] = queryset.first().create_at

            if create_at_params.get("create_at__lte"):
                create_at_params["create_at__lte"] = datetime.strptime(
                    create_at_params["create_at__lte"], "%Y-%m")
            else:
                create_at_params["create_at__lte"] = queryset.last().create_at

        except ValueError:
            raise ValidationError(
                _("日期范围输入有误，请重新输入，例如：create_at__gte=2019-01, create_at__lte=2019-02"))

        # 左开右闭
        create_at_params["create_at__lt"] = create_at_params.pop("create_at__lte") + relativedelta(
            months=1)

        return create_at_params

    @action(
        detail=False,
        methods=["get"],
        serializer_class=OperationalDataTicketSerializer,
        queryset=Ticket._objects.all(),
        permission_classes=(),
    )
    def get_tickets(self, request, *args, **kwargs):
        def get_queryset_by_fields(query_set, request):
            """
            根据前端给的字段信息进行过滤
            现货去符合条件的ticket的id集合，再从queryset里边获取
            """

            # 字段的过滤
            fields = {
                key.replace("field.", ""): item
                for key, item in request.query_params.items()
                if key.startswith("field.") and item
            }

            if not fields:
                return query_set

            ticket_ids = []
            valid_tickets = []
            for key, value in list(fields.items()):
                tickets = TicketField.objects.filter(key=key,
                                                     _value__in=value.split(",")).values_list(
                    "ticket_id", flat=True
                )
                ticket_ids.append(tickets)

            if ticket_ids:
                valid_tickets = list(reduce(lambda x, y: set(x) & set(y), ticket_ids))

            return query_set.filter(id__in=valid_tickets)

        def get_queryset_by_params(query_set, request):
            """构造查询条件"""

            if request.query_params.get("title"):
                title = request.query_params.get("title")
                query_set = query_set.filter(title__icontains=title)

            if request.query_params.get("creator"):
                creator = request.query_params.get("creator")
                query_set = query_set.filter(creator__icontains=creator)

            if request.query_params.get("sn"):
                sn = request.query_params.get("sn")
                query_set = query_set.filter(sn__icontains=sn)

            if request.query_params.get("update_at__gte"):
                update_at__gte = request.query_params.get("update_at__gte").replace("&nbsp;", " ")
                query_set = query_set.filter(update_at__gt=update_at__gte).order_by("-update_at")

            if request.query_params.get("is_draft"):
                is_draft = request.query_params.get("is_draft")
                query_set = query_set.filter(is_draft=is_draft)

            if request.query_params.get("service_type"):
                service_type = request.query_params.get("service_type")
                query_set = query_set.filter(service_type=service_type)

            return query_set

        ticket_id = request.query_params.get("ticket_id")
        if ticket_id:
            ticket = get_object_or_404(self.queryset, pk=ticket_id)
            ticket_serializer = self.serializer_class(ticket)
            return Response(ticket_serializer.data)

        create_at_params = self.get_time_params(request)
        queryset = self.queryset.filter(**create_at_params)

        # queryset = get_workflow_snap_ids(queryset, request)
        queryset = get_queryset_by_params(queryset, request)
        queryset = get_queryset_by_fields(queryset, request)

        paginate_queryset = self.paginate_queryset(queryset=queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        queryset=Workflow.objects.prefetch_related("notify").all(),
        serializer_class=OperationalDataWorkflowSerializer,
        permission_classes=(),
    )
    def workflows(self, request, *args, **kwargs):
        """获取流程列表"""
        workflow_id = request.query_params.get("workflow_id")
        if workflow_id:
            workflow = get_object_or_404(self.queryset, pk=workflow_id)
            workflow_serializer = self.serializer_class(workflow, context={"query_type": "detail"})
            return Response(workflow_serializer.data)

        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["get"],
        queryset=TicketComment.objects.all(),
        serializer_class=CommentSerializer,
        permission_classes=(),
    )
    def comments(self, request, *args, **kwargs):
        """获取评论"""

        queryset = self.queryset

        update_at = request.query_params.get("update_at__gte")
        if update_at:
            update_at = update_at.replace("&nbsp;", " ")
            queryset = self.queryset.filter(update_at__gt=update_at)

        paginate_queryset = self.paginate_queryset(queryset=queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"])
    def ticket_category(self, request, *args, **kwargs):
        """工单类型接口"""
        create_at_params = self.get_time_params(request)

        queryset = (
            self.queryset.filter(**create_at_params)
                .values("service_type")
                .order_by("service_type")
                .annotate(count=Count("id"))
        )
        values = {value["service_type"]: value["count"] for value in queryset}

        return Response(
            [{"service": service, "count": values.get(service, 0)} for service in SERVICE_LIST])

    @action(detail=False, methods=["get"])
    def month_ticket_category(self, request, *args, **kwargs):
        """工单按类型、按月"""
        queryset = self.queryset

        service_type = request.query_params.get("service_type")
        if service_type:
            queryset = queryset.filter(service_type=service_type)

        if not queryset.exists():
            return Response()

        create_at_params = self.get_month_params(queryset, request)
        queryset = self.queryset.filter(**create_at_params)

        filter_result = list(
            queryset.filter(service_type=service_type)
                .extra(select={"date": "date_format(create_at, '%%Y-%%m')"})
                .values("date", "service_type")
                .order_by("date")
                .annotate(count=Count("id"))
        )

        return Response(filter_result)

    @action(detail=False, methods=["get"])
    def ticket_status(self, request, *args, **kwargs):
        """工单状态"""

        create_at_params = self.get_time_params(request)
        queryset = self.queryset.filter(**create_at_params)

        service_type = request.query_params.get("service_type")
        if not service_type:
            raise ParamError(_("服务类型参数必填"))

        queryset = queryset.filter(service_type=service_type)
        ticket_status = list(
            TicketStatus.objects.filter(service_type=service_type).values_list("key", flat=True))

        filter_result = list(
            queryset.values("current_status").annotate(count=Count("current_status")).order_by(
                "current_status")
        )

        filter_result_keys = [item["current_status"] for item in filter_result]
        if set(ticket_status).difference(filter_result_keys):
            filter_result.extend(
                [
                    {"current_status": status, "count": 0}
                    for status in list(set(ticket_status).difference(filter_result_keys))
                ]
            )

        return Response(filter_result)

    @action(detail=False, methods=["get"])
    def whole_close_ratio(self, request, *args, **kwargs):
        """整体关单率"""
        create_at_params = self.get_time_params(request)
        queryset = self.queryset.filter(**create_at_params)

        total_count = queryset.count()
        finished_count = queryset.filter(current_status="FINISHED").count()
        try:
            ratio = (float(finished_count) / float(total_count)) * 100
        except ZeroDivisionError:
            ratio = 0

        return Response(
            [
                {
                    "service": "whole",
                    "finished_count": finished_count,
                    "total_count": total_count,
                    "ratio": "%.2f" % ratio,
                }
            ]
        )

    @action(detail=False, methods=["get"])
    def month_close_ratio(self, request, *args, **kwargs):
        """每月关单率"""
        queryset = self.queryset

        if not queryset.exists():
            return Response()

        create_at_params = self.get_month_params(queryset, request)
        month_list = get_month_list(create_at_params["create_at__gte"],
                                    create_at_params["create_at__lt"])

        date_ratio = [{"date": month, "ratio": 1} for month in month_list]

        queryset = self.queryset.filter(**create_at_params)

        # 每月创建的单据
        month_create_count = list(
            queryset.extra(select={"date": "date_format(create_at, '%%Y-%%m')"})
                .values("date", "service_type")
                .order_by("date", "service_type")
                .annotate(create_count=Count("create_at"))
        )

        # 每月创建且在当月结束的单据
        month_end_count = list(
            queryset.extra(
                select={"date": "date_format(create_at, '%%Y-%%m')"},
                where=['date_format(create_at, "%%Y-%%m") = date_format(end_at, "%%Y-%%m")'],
            )
                .values("date", "service_type")
                .order_by("date", "service_type")
                .annotate(end_count=Count("create_at"))
        )
        # sql:
        # SELECT (date_format(create_at, '%Y-%m')) AS `date`,
        #         `ticket_ticket`.`service_type`,
        #         COUNT(`ticket_ticket`.`create_at`) AS `end_count`
        # FROM `ticket_ticket`
        # WHERE (`ticket_ticket`.`is_deleted` = False AND
        #        `ticket_ticket`.`is_draft` = False AND
        #        `ticket_ticket`.`create_at` >= 2018-04-01 00:00:00 AND
        #        `ticket_ticket`.`create_at` < 2019-05-01 00:00:00 AND
        #        (date_format(create_at, "%Y-%m") = date_format(end_at, "%Y-%m")))
        # GROUP BY `ticket_ticket`.`service_type`, (date_format(create_at, '%Y-%m'))
        # ORDER BY `date` ASC, `ticket_ticket`.`service_type` ASC

        # 整体
        whole_month_create_count = list(
            queryset.extra(select={"date": "date_format(create_at, '%%Y-%%m')"})
                .values("date")
                .order_by("date")
                .annotate(create_count=Count("create_at"))
        )
        # sql:
        # SELECT (date_format(create_at, '%Y-%m')) AS `date`,
        #         COUNT(`ticket_ticket`.`create_at`) AS `create_count`
        # FROM `ticket_ticket`
        # WHERE (`ticket_ticket`.`is_deleted` = False AND
        #        `ticket_ticket`.`is_draft` = False AND
        #        `ticket_ticket`.`create_at` >= 2018-04-01 00:00:00 AND
        #        `ticket_ticket`.`create_at` < 2019-05-01 00:00:00)
        # GROUP BY (date_format(create_at, '%Y-%m')) ORDER BY `date` ASC

        for item in whole_month_create_count:
            item.update({"service_type": "whole"})

        # 每月创建且在当月结束的单据
        whole_month_end_count = list(
            queryset.extra(
                select={"date": "date_format(create_at, '%%Y-%%m')"},
                where=['date_format(create_at, "%%Y-%%m") = date_format(end_at, "%%Y-%%m")'],
            )
                .values("date")
                .order_by("date")
                .annotate(end_count=Count("create_at"))
        )
        for item in whole_month_end_count:
            item.update({"service_type": "whole"})
        create_count = month_create_count + whole_month_create_count
        end_count = month_end_count + whole_month_end_count
        for create in create_count:
            for end in end_count:
                if create["service_type"] == end["service_type"] and create["date"] == end["date"]:
                    try:
                        create["ratio"] = "%.2f" % (
                                (float(end["end_count"]) / float(create["create_count"])) * 100)
                    except ZeroDivisionError:
                        create["ratio"] = "%.2f" % 100

        for item in create_count:
            item["ratio"] = item.get("ratio", 0)

        filter_datas = group_by(create_count, ["service_type"], dict_result=True)
        for key, values in list(filter_datas.items()):
            if set(month_list).difference([value["date"] for value in values]):
                values.extend(
                    [
                        {"date": month, "ratio": 100, "create_count": 0, "service_type": key, }
                        for month in set(month_list).difference([value["date"] for value in values])
                    ]
                )
                values.sort(key=lambda x: x["date"])

        if set(SERVICE_LIST + ["whole"]).difference(list(filter_datas.keys())):
            filter_datas.update(
                {service: date_ratio for service in
                 set(SERVICE_LIST + ["whole"]).difference(list(filter_datas.keys()))}
            )

        return Response(filter_datas)

    @action(
        detail=False,
        methods=["get"],
        queryset=TicketEventLog.objects.all().exclude(
            Q(message__in=[u"流程结束.", u"流程开始."]) | Q(source=SYSTEM_OPERATE)),
    )
    def ticket_processor_rank(self, request, *args, **kwargs):
        """工单处理量/认领量/派单量"""

        operate_at_params = self.get_time_params(request, params_key="operate_at")

        queryset = self.queryset.filter(**operate_at_params)
        process_list = (
            queryset.filter(type=TRANSITION_OPERATE)
                .values("operator")
                .order_by("operator")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
        )
        claim_list = (
            queryset.filter(type=CLAIM_OPERATE)
                .values("operator")
                .order_by("operator")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
        )

        distribute_list = (
            queryset.filter(type=DISTRIBUTE_OPERATE)
                .values("operator")
                .order_by("operator")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
        )

        for item in process_list:
            item.update({"operator": transform_single_username(item["operator"])})

        for item in claim_list:
            item.update({"operator": transform_single_username(item["operator"])})

        for item in distribute_list:
            item.update({"operator": transform_single_username(item["operator"])})

        return Response(
            {"processors": process_list, "claimers": claim_list, "distributors": distribute_list, })

    @action(detail=False, methods=["get"])
    def ticket_score(self, request, *args, **kwargs):
        """满意度评价"""
        queryset = self.queryset

        if not queryset.exists():
            return Response()

        create_at_params = self.get_month_params(queryset, request)
        create_at_params["create_at__gte"] = create_at_params["create_at__gte"].strftime(
            "%Y-%m-%d %H:%M:%S")
        create_at_params["create_at__lt"] = create_at_params["create_at__lt"].strftime(
            "%Y-%m-%d %H:%M:%S")

        service_type = request.query_params.get("service_type", "")
        if service_type and service_type not in SERVICE_LIST:
            raise ValidationError(_("服务类型参数有误，请重新输入"))

        if service_type:
            records = dictfetchall(
                connection,
                service_ticket_score_sql,
                create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
                service_type,
            )
        else:
            records = dictfetchall(
                connection, ticket_score_sql, create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
            )

        return Response(sorted(records, key=lambda x: x["date"]))

    @action(detail=False, methods=["get"])
    def ticket_time(self, request, *args, **kwargs):
        """响应时长，解决时长"""

        queryset = self.queryset

        if not queryset.exists():
            return Response()

        create_at_params = self.get_month_params(queryset, request)
        month_list = get_month_list(create_at_params["create_at__gte"],
                                    create_at_params["create_at__lt"])
        create_at_params["create_at__gte"] = create_at_params["create_at__gte"].strftime(
            "%Y-%m-%d %H:%M:%S")
        create_at_params["create_at__lt"] = create_at_params["create_at__lt"].strftime(
            "%Y-%m-%d %H:%M:%S")

        service_type = request.query_params.get("service_type", "")
        if service_type and service_type not in SERVICE_LIST:
            raise ValidationError(_("服务类型参数有误，请重新输入"))

        if service_type:
            solve_records = dictfetchall(
                connection,
                service_solve_sql,
                create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
                service_type,
            )
            response_records = dictfetchall(
                connection,
                service_response_sql,
                create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
                service_type,
            )
        else:
            solve_records = dictfetchall(
                connection, solve_sql, create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
            )
            response_records = dictfetchall(
                connection, response_sql, create_at_params["create_at__gte"],
                create_at_params["create_at__lt"],
            )

        if set(month_list).difference([record["date"] for record in solve_records]):
            solve_records.extend(
                [
                    {"date": month, "ratio": 0, "count": 0, "total": 0}
                    for month in
                    set(month_list).difference([record["date"] for record in solve_records])
                ]
            )
        if set(month_list).difference([record["date"] for record in response_records]):
            response_records.extend(
                [
                    {"date": month, "ratio": 0, "count": 0, "total": 0}
                    for month in
                    set(month_list).difference([record["date"] for record in response_records])
                ]
            )

        solve_records.sort(key=lambda x: x["date"])
        response_records.sort(key=lambda x: x["date"])

        return Response({"solve_records": solve_records, "response_records": response_records, })

    @action(detail=False, methods=["get"])
    def new_tickets(self, request, *args, **kwargs):
        """每日新增工单量"""
        create_at_params = self.get_time_params(self.request)
        queryset = self.queryset.filter(**create_at_params)

        service_type = request.query_params.get("service_type", "")
        if service_type:
            queryset = queryset.filter(service_type=service_type)

        if not queryset.exists():
            return Response()

        filter_result = list(
            queryset.extra(select={"day": "date(create_at)"})
                .values("day")
                .distinct()
                .order_by("day")
                .annotate(count=Count("create_at"))
        )

        if not create_at_params:
            begin = filter_result[0]["day"]
            end = filter_result[-1]["day"]
            days = get_days(
                begin=datetime(begin.year, begin.month, begin.day),
                end=datetime(end.year, end.month, end.day),
            )
        else:
            days = get_days(
                begin=datetime.strptime(create_at_params["create_at__gte"].split(" ")[0],
                                        "%Y-%m-%d"),
                end=datetime.strptime(create_at_params["create_at__lte"].split(" ")[0], "%Y-%m-%d"),
            )

        filter_result_days = [item["day"] for item in filter_result]
        if set(days).difference(filter_result_days):
            filter_result.extend([{"day": day, "count": 0} for day in
                                  list(set(days).difference(filter_result_days))])

        filter_result.sort(key=lambda x: x["day"])
        return Response(filter_result)
