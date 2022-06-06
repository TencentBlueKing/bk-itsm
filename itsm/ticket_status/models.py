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

import itertools
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    BUILTIN_TICKET_STATUS,
    EMPTY_INT,
    EMPTY_STRING,
    FLOW_STATUS_CHOICES,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    PROCESS_RUNNING,
    SERVICE_CATEGORY,
)
from itsm.component.utils.basic import get_random_key
from itsm.service.models import ServiceCategory
from itsm.ticket_status import managers


class Model(models.Model):
    """基础字段"""

    DISPLAY_FIELDS = (
        "creator",
        "create_at",
        "updated_by",
        "update_at",
    )

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    auth_resource = {"resource_type": "sla", "resource_type_name": "服务协议管理"}
    resource_operations = ["sla_manage"]

    class Meta:
        abstract = True

    objects = managers.Manager()
    _objects = models.Manager()

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()

    @classmethod
    def get_unique_key(cls, name):
        """生成唯一的key"""

        key = get_random_key(name)
        retry = 0

        while retry < 60:
            # 满足条件，退出循环，且retry<60
            if not cls.objects.filter(key=key).exists():
                break

            key = get_random_key(name)
            retry += 1
        else:
            # 尝试60次一直重复，则放弃生成key
            return "##Err##"

        return key


class TicketStatusConfig(Model):
    """
    工单状态配置信息
    """

    service_type = models.CharField(_("服务类型"), max_length=LEN_NORMAL)
    configured = models.BooleanField(_("已配置"), default=False)

    objects = managers.TicketStatusConfigManager()

    class Meta:
        app_label = "ticket_status"
        verbose_name = _("工单状态配置")
        verbose_name_plural = _("工单状态配置")

    def __unicode__(self):
        return "{}({})".format(self.service_type, self.configured)

    @classmethod
    def init_ticket_status_config(cls):
        """初始化配置表信息"""
        if cls.objects.exists():
            print("ticket_status_config exists, skip init ticket_status_config data")
            return

        service_types = list(ServiceCategory.objects.values_list("key", flat=True))
        for service_type in service_types:
            cls.objects.create(
                creator="system", configured=True, service_type=service_type
            )

    @property
    def service_type_name(self):
        return _(str(SERVICE_CATEGORY[self.service_type]))

    @property
    def ticket_status(self):
        """对应服务类型下状态信息"""
        all_status = TicketStatus.objects.filter(service_type=self.service_type).all()
        return "/".join([_(status.name) for status in all_status])

    @classmethod
    def update_config(cls, service_type, user, configured=None):
        """更新配置需更新更新时间和更新人"""
        updated_by = getattr(user, "username", "guest")
        update_kwargs = {"updated_by": updated_by, "update_at": datetime.now()}
        if configured is not None:
            update_kwargs.update({"configured": configured})
        cls.objects.filter(service_type=service_type).update(**update_kwargs)


class TicketStatus(Model):
    """
    工单状态
    """

    service_type = models.CharField(_("服务类型"), max_length=LEN_NORMAL)
    key = models.CharField(_("状态关键字"), max_length=LEN_LONG)
    name = models.CharField(_("状态名称"), max_length=LEN_LONG)
    color_hex = models.CharField(_("二进制颜色"), max_length=LEN_SHORT, blank=True)
    desc = models.CharField(
        _("状态说明"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    flow_status = models.CharField(
        _("流程状态"),
        max_length=LEN_SHORT,
        choices=FLOW_STATUS_CHOICES,
        default=PROCESS_RUNNING,
    )
    order = models.IntegerField(_("序号"), default=EMPTY_INT)
    is_builtin = models.BooleanField(_("是否内置状态"), default=False)
    is_start = models.BooleanField(_("是否为开始状态"), default=False)
    is_over = models.BooleanField(_("是否为结束状态"), default=False)
    is_suspend = models.BooleanField(_("是否为挂起状态"), default=False)

    objects = managers.TicketStatusManager()

    class Meta:
        app_label = "ticket_status"
        verbose_name = _("工单状态")
        verbose_name_plural = _("工单状态")

    def __unicode__(self):
        return "{}({})".format(self.name, self.key)

    @classmethod
    def init_ticket_status(cls):
        """初始化默认工单状态"""

        service_types = list(ServiceCategory.objects.values_list("key", flat=True))
        for service_type, status in itertools.product(
            service_types, BUILTIN_TICKET_STATUS
        ):
            cls.objects.update_or_create(
                defaults={
                    "name": status["name"],
                    "color_hex": status["color_hex"],
                    "flow_status": status["flow_status"],
                    "order": status["order"],
                    "is_builtin": status["is_builtin"],
                    "is_start": status["is_start"],
                    "is_over": status["is_over"],
                    "is_suspend": status["is_suspend"],
                },
                key=status["key"],
                service_type=service_type,
            )

    @classmethod
    def all_status_info(cls):
        all_status = cls.objects.all().values("service_type", "name", "key", "is_over")
        status_info = {}
        for status in all_status:
            status_key = "{}_{}".format(status["service_type"], status["key"])
            status_info[status_key] = {
                "name": status["name"],
                "over": status["is_over"],
            }
        return status_info

    def get_to_status_ids(self):
        """获取当前单据状态跳转到所有单据状态ID列表
        :return <type QuerySet>, 懒加载减少数据库交互次数
        """
        return self.from_transits.values_list("to_status", flat=True)

    @property
    def to_status(self):
        return (
            self.__class__.objects.filter(id__in=self.to_status_id_set)
            .exclude(key="SUSPENDED")
            .order_by("order")
        )

    @property
    def to_status_keys(self):
        return set(self.to_status.values_list("key", flat=True))

    @property
    def to_over_status(self):
        return self.__class__.objects.filter(
            id__in=self.to_status_id_set, is_over=True
        ).order_by("order")

    @property
    def to_over_status_keys(self):
        return set(self.to_over_status.values_list("key", flat=True))

    @property
    def to_status_id_set(self):
        return set(self.from_transits.values_list("to_status__id", flat=True))


class StatusTransit(Model):
    """
    状态转换规则
    """

    service_type = models.CharField(_("服务类型"), max_length=LEN_NORMAL)

    from_status = models.ForeignKey(
        help_text=_("源状态"),
        to=TicketStatus,
        related_name="from_transits",
        on_delete=models.CASCADE,
    )
    to_status = models.ForeignKey(
        help_text=_("目标状态"),
        to=TicketStatus,
        related_name="to_transits",
        on_delete=models.CASCADE,
    )
    is_auto = models.BooleanField(_("是否自动转换"), default=False)
    threshold = models.IntegerField(_("阈值"), default=EMPTY_INT)
    threshold_unit = models.CharField(
        _("时长单位"),
        max_length=LEN_SHORT,
        default="m",
        choices=[
            ("m", "分钟"),
            ("h", "小时"),
            ("d", "天"),
        ],
    )

    objects = managers.StatusTransitManager()

    class Meta:
        app_label = "ticket_status"
        verbose_name = _("状态转换规则")
        verbose_name_plural = _("状态转换规则")

    def __unicode__(self):
        return "{}-{}({})".format(
            self.from_status.name, self.to_status.name, self.service_type
        )

    @property
    def from_status_name(self):
        return self.from_status.name

    @property
    def to_status_name(self):
        return self.to_status.name

    @classmethod
    def init_status_transit(cls):
        """初始化状态流转数据"""
        if cls.objects.exists():
            print("status transit exists, skip init status transit")
            return

        status = [status["key"] for status in BUILTIN_TICKET_STATUS]
        # 可流转的状态映射
        transit_map = {
            status[0]: status[:2] + status[5:],
            status[1]: status[1:],
            status[2]: status[1:],
            status[3]: status[1:],
            status[4]: status[1:],
            status[5]: status[5:],
            status[6]: status[5:],
        }
        # 每种服务类别都创建一套
        transits = []
        for service_type, v in list(SERVICE_CATEGORY.items()):

            # 每个源状态的流转
            for from_status, to_status_list in list(transit_map.items()):
                from_status_inst = TicketStatus.objects.get(
                    service_type=service_type, key=from_status
                )

                for to_status in to_status_list:
                    to_status_inst = TicketStatus.objects.get(
                        service_type=service_type, key=to_status
                    )

                    if from_status and to_status_inst:
                        transits.append(
                            cls(
                                service_type=service_type,
                                from_status=from_status_inst,
                                to_status=to_status_inst,
                            )
                        )
        cls.objects.bulk_create(transits)
