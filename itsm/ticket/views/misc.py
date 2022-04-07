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


from django.conf import settings
from django.utils.translation import ugettext as _
from mako.template import Template
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from common.log import logger
from itsm.component.constants import FOLLOW_OPERATE
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.exceptions import ComponentCallError
from itsm.component.notify import EmailNotifier
from itsm.iadmin.contants import ACTION_CHOICES_DICT
from itsm.iadmin.models import CustomNotice
from itsm.ticket.models import (
    TicketComment,
    TicketCommentInvite,
    TicketFollowerNotifyLog,
    TicketStateDraft,
    TicketTemplate,
)
from itsm.ticket.permissions import (
    CommentPermissionValidate,
    FollowersNotifyLogPermissionValidate,
)
from itsm.ticket.serializers import (
    CommentInviteSerializer,
    CommentSerializer,
    FollowerNotifyLogSerializer,
    StateDraftSerializer,
    TemplateSerializer,
)
from itsm.ticket.validators import notify_log_validate, sms_comment_validate


class TemplateViewSet(component_viewsets.NormalModelViewSet):
    """单据模板view"""

    pagination_class = None
    queryset = TicketTemplate.objects.all()
    serializer_class = TemplateSerializer

    filter_fields = {
        "name": ["exact"],
        "service": ["exact"],
    }
    ordering_fields = "__all__"

    def get_queryset(self):
        """返回个人模板"""
        return self.queryset.filter(creator=self.request.user.username)


class StateDraftViewSet(component_viewsets.NormalModelViewSet):
    """单据节点草稿"""

    pagination_class = None
    queryset = TicketStateDraft.objects.all()
    serializer_class = StateDraftSerializer

    filter_fields = {
        "ticket_id": ["exact"],
        "state_id": ["exact"],
    }
    ordering_fields = "__all__"

    def get_queryset(self):
        """返回个人草稿"""
        return self.queryset.filter(creator=self.request.user.username)


class CommentViewSet(component_viewsets.NormalModelViewSet):
    """工单评论"""

    # pagination_class = None
    queryset = TicketComment.objects.filter(is_deleted=False).select_related("ticket")
    serializer_class = CommentSerializer
    permission_classes = (CommentPermissionValidate,)

    filter_fields = {
        "ticket": ["exact"],
        "stars": ["exact"],
    }
    ordering_fields = "__all__"

    @action(detail=False, methods=["get"])
    def get_comment(self, request):
        """短信链接获取工单评论信息"""
        code = request.GET.get("code", "")
        try:
            comment = self.queryset.get(invite__code=code)
        except TicketComment.DoesNotExist:
            raise serializers.ValidationError(_("单据评论信息不存在"))
        data = {
            "sn": comment.ticket.sn,
            "title": comment.ticket.title,
            "stars": comment.stars,
            "comment": comment.comments,
            "is_rated": True if comment.stars else False,
        }
        return Response(data)

    @action(detail=False, methods=["post"])
    def post_comment(self, request):
        data = request.data

        comment, stars = sms_comment_validate(self.queryset, data)

        comment.stars = stars
        comment.comments = data.get("comment")
        comment.source = "SMS"
        comment.creator = comment.invite.get(code=data.get("code")).number
        comment.save()

        return Response()


class CommentInviteViewSet(component_viewsets.NormalModelViewSet):
    """邀请记录"""

    pagination_class = None
    queryset = TicketCommentInvite.objects.all()
    serializer_class = CommentInviteSerializer

    filter_fields = {
        "comment": ["exact"],
        "number": ["exact"],
        "code": ["exact"],
    }
    ordering_fields = "__all__"


class FollowersNotifyLogViewSet(component_viewsets.NormalModelViewSet):
    """单据通知视图"""

    pagination_class = None
    queryset = TicketFollowerNotifyLog.objects.filter(
        is_deleted=False, is_sys_sended=False
    )
    serializer_class = FollowerNotifyLogSerializer
    permission_classes = (FollowersNotifyLogPermissionValidate,)

    filter_fields = {"ticket_id": ["exact"]}
    ordering_fields = "__all__"

    @action(detail=False, methods=["post"])
    def notify(self, request, *args, **kwargs):
        """关注人邮件通知"""

        data = request.data
        ticket, receivers = notify_log_validate(data, request.user.username)
        ticket_token = TicketFollowerNotifyLog.get_unique_token()
        data.update({"ticket_token": ticket_token, "creator": request.user.username})
        notify_log = TicketFollowerNotifyLog.objects.create(**data)

        # 构建信息
        context = ticket.get_notify_context()
        context.update(
            {
                "message": notify_log.message,
                "action": ACTION_CHOICES_DICT.get(FOLLOW_OPERATE, _("待处理")),
            }
        )

        follow_link = "{site_url}#/ticket/detail?id={ticket_id}".format(
            site_url=settings.FRONTEND_URL, ticket_id=ticket.id
        )
        context["ticket_url"] = follow_link
        try:
            follow_notify_template = CustomNotice.objects.get(
                project_key=ticket.project_key,
                action=FOLLOW_OPERATE,
                notify_type="EMAIL",
            )
        except CustomNotice.DoesNotExist:
            follow_notify_template = CustomNotice.objects.get(
                action=FOLLOW_OPERATE, notify_type="EMAIL", project_key="public    "
            )

        message = Template(follow_notify_template.content_template).render(**context)
        title = Template(follow_notify_template.title_template).render(**context)

        error_message = ""
        try:
            notify = EmailNotifier(title=title, receivers=receivers, message=message)
            notify.send()
        except ComponentCallError as error:
            logger.warning("send notify failed, error: %s" % str(error))
            notify_log.delete()
            error_message = str(error).split("(")[0]
        except Exception as e:
            logger.error("send email exception: %s" % e)
            notify_log.delete()
            error_message = _("组件调用异常：发送失败，请联系管理员")

        if error_message:
            raise serializers.ValidationError(error_message)

        return Response()
