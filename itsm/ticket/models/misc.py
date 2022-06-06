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

import time
import uuid

import jsonfield
from django.conf import settings
from django.db import models, transaction
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from mptt.fields import TreeForeignKey

from itsm.component.constants import (
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_LIST,
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    PROCESSOR_CHOICES,
    FIRST_ORDER,
)
from itsm.component.db.models import BaseMpttModel
from itsm.ticket import managers


class TicketTemplate(models.Model):
    """单据模板，方便提单"""

    name = models.CharField(_("模板名称"), max_length=LEN_NORMAL)
    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    service = models.CharField(_("对应服务主键"), default=EMPTY_STRING, max_length=LEN_NORMAL)
    template = jsonfield.JSONField(
        _("单据模板字段"), default=EMPTY_LIST, null=True, blank=True
    )

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据模板")
        verbose_name_plural = _("单据模板")

    def __unicode__(self):
        return "{}({})".format(self.name, self.service)


class TicketStateDraft(models.Model):
    """单据节点草稿"""

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    ticket_id = models.IntegerField(_("单据id"))
    state_id = models.IntegerField(_("节点id"))
    draft = jsonfield.JSONField(
        _("单据节点草稿字段"), default=EMPTY_LIST, null=True, blank=True
    )

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据节点草稿")
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{}-{}({})".format(self.ticket_id, self.state_id, self.creator)


class TicketComment(models.Model):
    """工单满意度表"""

    SOURCE_CHOICE = [
        ("WEB", "蓝鲸平台"),
        ("SMS", "短信邀请"),
        ("SYS", "系统自评"),
        ("API", "OPENAPI"),
    ]

    ticket = models.OneToOneField(
        "ticket.Ticket",
        help_text=_("关联工单"),
        related_name="comments",
        on_delete=models.CASCADE,
    )
    stars = models.IntegerField("评价等级1~5，5星为最好", default=0)
    comments = models.CharField(_("评价信息"), max_length=LEN_LONG, null=True, blank=True)
    source = models.CharField(
        _("评价来源"), choices=SOURCE_CHOICE, default="SYS", max_length=LEN_NORMAL
    )
    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL, null=True, blank=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    class Meta:
        app_label = "ticket"
        verbose_name = _("工单评价")
        verbose_name_plural = _("工单评价")

    def __unicode__(self):
        return "{}({})".format(self.ticket.sn, self.stars)

    @classmethod
    def fix_comments(cls, *args, **kwargs):
        """为之前结束的单据创建评论数据，未做迁移前只执行一次"""

        from itsm.ticket.models import Ticket

        start = time.time()
        try:
            uncommented_finished = (
                Ticket.objects.filter(
                    is_deleted=False, is_draft=False, current_status="FINISHED"
                )
                .exclude(
                    id__in=TicketComment.objects.values_list("ticket_id", flat=True)
                )
                .values_list("id", flat=True)
            )

            TicketComment.objects.bulk_create(
                [
                    TicketComment(ticket_id=ticket_id)
                    for ticket_id in uncommented_finished
                ]
            )
            print(
                "fix history ticket comments: %s, elapsed: %ss"
                % (len(uncommented_finished), time.time() - start)
            )
        except Exception as e:
            print("fix history ticket comments exception: %s" % e)

    @classmethod
    def ticket_comments(cls, ticket_ids):
        comments = cls.objects.filter(ticket_id__in=ticket_ids).values(
            "ticket_id", "id", "stars"
        )
        info = {
            comment["ticket_id"]: {"id": comment["id"], "stars": comment["stars"]}
            for comment in comments
        }
        return info


class TicketCommentInvite(models.Model):
    """邀请途径记录表"""

    comment = models.ForeignKey(
        TicketComment,
        help_text=_("关联评论"),
        related_name="invite",
        on_delete=models.CASCADE,
    )
    notify_type = models.CharField(_("通知方式"), max_length=LEN_SHORT, default="SMS")
    receiver = models.CharField(_("联系人/联系方式"), max_length=LEN_NORMAL, default="")
    code = models.CharField(_("短码"), max_length=10, default="", unique=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        app_label = "ticket"
        verbose_name = _("邀请途径记录")
        verbose_name_plural = _("邀请途径记录")

    def __unicode__(self):
        return "{}({})".format(self.number, self.comment.id)

    @classmethod
    def get_unique_code(cls):
        """生成唯一的短码，7位，3x62^6种"""

        code = get_random_string(6)
        retry = 0

        while retry < 60:
            # 满足条件，退出循环，且retry<60
            if not cls.objects.filter(code=code).exists():
                break

            code = get_random_string(6)
            retry += 1
        else:
            # 尝试60次一直重复，则放弃生成code
            return "##Err##"

        # [T|P|D][6c] = 7c
        return "{}{}".format(settings.RUN_MODE[0], code)

    @classmethod
    def get_user_comments_invites(cls, user):
        comments_invites = {}
        invites = TicketCommentInvite.objects.filter(receiver=user).values(
            "comment_id", "code"
        )
        for invite in invites:
            comments_invites.setdefault(invite["comment_id"], []).append(invite["code"])
        return comments_invites


class NotifyLogModel(models.Model):
    """通知日志公共字段"""

    state_id = models.IntegerField(_("发送节点ID"), default=EMPTY_INT)
    state_name = models.CharField(
        _("节点名称"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True
    )
    creator = models.CharField(
        _("创建人"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True
    )
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    message = models.TextField(_("通知信息"), default=EMPTY_STRING, null=True, blank=True)
    notify_type = models.CharField(_("通知方式"), max_length=LEN_SHORT, default="EMAIL")
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    objects = managers.Manager()

    class Meta:
        app_label = "ticket"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(NotifyLogModel, self).delete()


class TicketFollowerNotifyLog(NotifyLogModel):
    """工单关注人通知日志"""

    ticket = models.ForeignKey(
        "ticket.Ticket",
        help_text=_("关联工单"),
        related_name="follower_notify_logs",
        on_delete=models.CASCADE,
    )
    followers = models.CharField(
        _("关注人"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    followers_type = models.CharField(
        _("处理者类型/角色类型"),
        max_length=LEN_SHORT,
        choices=PROCESSOR_CHOICES,
        default="EMPTY",
    )
    ticket_token = models.CharField(
        _("关注链接只读标识"),
        max_length=10,
        default=EMPTY_STRING,
        unique=True,
        null=True,
        blank=True,
    )
    is_sys_sended = models.BooleanField(_("是否系统流程发送"), default=False)

    class Meta:
        app_label = "ticket"
        verbose_name = _("关注人通知日志")
        verbose_name_plural = _("关注人通知日志")

    def __unicode__(self):
        return "{}({})".format(self.creator, self.state_name)

    @classmethod
    def get_unique_token(cls):
        """生成唯一的短码，7位，3x62^6种"""

        ticket_token = get_random_string(6)
        retry = 0

        while retry < 60:
            # 满足条件，退出循环，且retry<60
            if not cls.objects.filter(ticket_token=ticket_token).exists():
                break

            get_random_string(6)
            retry += 1
        else:
            # 尝试60次一直重复，则放弃生成code
            return "##Err##"

        # [T|P|D][6c] = 7c
        return "{}{}".format(settings.RUN_MODE[0], ticket_token)


class TicketSuperviseNotifyLog(NotifyLogModel):
    """工单督办日志"""

    ticket = models.ForeignKey(
        "ticket.Ticket",
        help_text=_("关联工单"),
        related_name="supervise_notify_logs",
        on_delete=models.CASCADE,
    )
    supervised = models.CharField(
        _("被督办的人"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )

    class Meta:
        app_label = "ticket"
        verbose_name = _("督办日志")
        verbose_name_plural = _("督办日志")

    def __unicode__(self):
        return "{}({})".format(self.creator, self.state_name)


class TicketGlobalVariable(models.Model):
    """自动节点全局变量"""

    key = models.CharField(_("变量关键字"), max_length=LEN_LONG)
    name = models.CharField(_("变量名"), max_length=LEN_NORMAL, default=EMPTY_STRING)
    value = jsonfield.JSONField(_("变量值"), default=EMPTY_DICT)

    state_id = models.IntegerField(_("关联节点"), null=True, blank=True)
    ticket_id = models.IntegerField(_("关联单据"), null=True, blank=True)

    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)

    objects = managers.TicketGlobalVariableManager()

    class Meta:
        app_label = "ticket"
        verbose_name = _("单据全局变量")
        verbose_name_plural = _("单据全局变量")

    @classmethod
    def get_ticket_output(cls, ticket_id, display_type="dict"):
        variables = cls.objects.filter(ticket_id=ticket_id)
        if display_type == "dict":
            outputs = {}
            for variable in variables:
                outputs[variable.key] = variable.value
        else:
            outputs = []
            for variable in variables:
                outputs.append(
                    {
                        "key": variable.key,
                        "name": variable.name,
                        "value": variable.value,
                    }
                )
        return outputs


def uniqid():
    return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex


class TicketRemark(BaseMpttModel):
    REMARK_TYPE = [
        ("PUBLIC", "公开评论"),
        ("INSIDE", "内部评论"),
        ("ROOT", "根评论"),
    ]

    key = models.CharField(_("目录关键字"), max_length=LEN_LONG, unique=True)
    content = models.TextField(_("评论内容"), max_length=LEN_LONG, null=True, blank=True)
    order = models.IntegerField(_("节点顺序"), default=FIRST_ORDER)
    remark_type = models.CharField(_("评论类型"), max_length=LEN_SHORT, choices=REMARK_TYPE)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("上级目录"),
        null=True,
        blank=True,
        related_name="children",
    )
    ticket_id = models.IntegerField(
        _("单据id"), max_length=LEN_SHORT, null=False, default=0
    )
    users = models.JSONField(_("用户@的用户列表"), default=[])
    update_log = models.JSONField(_("用户评论的更新记录"), default=[])

    class Meta:
        app_label = "ticket"
        ordering = ("order",)

    def save(self, *args, **kwargs):
        """自动填充key"""

        # 创建目录时若key为空则自动生成key
        if self.pk is None and not self.key:
            self.key = uniqid()

        return super(TicketRemark, self).save(*args, **kwargs)

    @classmethod
    def create_root(cls, ticket_id, **kwargs):
        return cls.create_node(
            content="", ticket_id=ticket_id, remark_type="ROOT", key=None, **kwargs
        )

    @classmethod
    @transaction.atomic
    def create_node(
        cls,
        ticket_id,
        content,
        remark_type,
        key=None,
        parent=None,
        is_deleted=False,
        **kwargs
    ):
        """
        Creates a new catalog
        """

        # 通过其他手段获取parent
        if parent is None and kwargs.get("parent_key"):
            parent = cls.objects.get(key=kwargs.get("parent_key"))

        # 自动生成key
        if key is None:
            key = uniqid()

        comment, _ = cls._objects.get_or_create(
            defaults={
                "content": content,
                "parent": parent,
                "ticket_id": ticket_id,
                "remark_type": remark_type,
            },
            **{"key": key, "is_deleted": is_deleted}
        )

        return comment

    @classmethod
    def root_subtree(cls, ticket_id, show_type):
        # 获取当前节点的根节点
        try:
            root_node = cls._objects.get(ticket_id=ticket_id, remark_type="ROOT")
        except cls.DoesNotExist:
            root_node = TicketRemark.create_root(ticket_id=ticket_id)
        return cls.subtree(root_node, show_type)

    @classmethod
    def init_root_node(cls, ticket_id):
        # 获取当前节点的根节点
        try:
            node = cls._objects.get(ticket_id=ticket_id, remark_type="ROOT")
        except cls.DoesNotExist:
            node = TicketRemark.create_root(ticket_id=ticket_id)
        return node

    @classmethod
    def subtree(cls, node, show_type):
        """获取以node为根的子树"""

        node_children = (
            node.get_children()
            .filter(is_deleted=False, remark_type=show_type)
            .order_by("-create_at")
        )

        children = [node.subtree(child, show_type) for child in node_children]

        data = {
            "id": node.id,
            "key": node.key,
            "content": node.content,
            "remark": node.remark_type,
            "ticket_id": node.ticket_id,
            "level": node.level,
            "children": children,
            "update_log": node.update_log,
            "users": node.users,
            "creator": node.creator,
            "create_at": node.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "update_at": node.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_by": node.updated_by,
        }

        return data
