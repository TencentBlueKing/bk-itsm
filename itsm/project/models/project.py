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

import jsonfield
from django.db import models, transaction

from itsm.component.constants import (
    LEN_MIDDLE,
    LEN_LONG,
    EMPTY_STRING,
    LEN_NORMAL,
    LEN_SHORT,
    PUBLIC_PROJECT_PROJECT_KEY,
    EMPTY_DICT,
    FIRST_ORDER,
    CATALOG,
)
from itsm.iadmin.contants import PROJECT_SETTING
from itsm.project.models.base import Model
from django.utils.translation import ugettext as _

from itsm.service.models import ServiceCatalog
from itsm.sla.models import Sla, Schedule


class Project(Model):
    key = models.CharField(_("项目唯一标识"), max_length=LEN_SHORT, primary_key=True)
    name = models.CharField(_("项目名"), max_length=LEN_MIDDLE)
    desc = models.CharField(
        _("项目描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    logo = models.TextField(_("logo base64 内容"), default="", blank=True)
    color = models.CharField(_("项目颜色"), null=True, default="", max_length=LEN_SHORT)
    is_enabled = models.BooleanField(_("是否启用"), default=True, db_index=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    resource_operations = [
        "project_view",
        "project_edit",
        "service_create",
        "field_create",
        "user_group_create",
        "triggers_create",
        "sla_calendar_create",
        "sla_agreement_create",
        "settings_view",
        "settings_manage",
        "catalog_create",
        "catalog_edit",
        "catalog_delete",
    ]

    auth_resource = {"resource_type": "project", "resource_type_name": "项目"}

    need_auth_grant = True

    def init_service_catalogs(self, catalog):
        level_1 = [item for item in catalog if item["level"] == 1]
        level_2 = [item for item in catalog if item["level"] == 2]
        # 预留支持3级
        level_3 = [item for item in catalog if item["level"] == 3]
        root_key = "{}_{}".format(self.key, "root")
        root = ServiceCatalog.create_root(
            key=root_key, name=_("根目录"), is_deleted=False, project_key=self.key
        )
        for level1 in level_1:
            l_1 = ServiceCatalog.create_catalog(
                key=level1["key"],
                name=level1["name"],
                parent=root,
                project_key=self.key,
            )
            for level2 in level_2:
                if l_1.key == level2["parent_key"]:
                    l_2 = ServiceCatalog.create_catalog(
                        key=level2["key"],
                        name=level2["name"],
                        parent=l_1,
                        project_key=self.key,
                    )
                    for level3 in level_3:
                        if l_2.key == level3["parent_key"]:
                            ServiceCatalog.create_catalog(
                                key=level3["key"],
                                name=level3["name"],
                                parent=l_2,
                                project_key=self.key,
                            )

    def init_project_settings(self):
        for project_setting in PROJECT_SETTING:
            ProjectSettings.objects.get_or_create(
                type=project_setting[1],
                key=project_setting[0],
                value=project_setting[2],
                project=self,
            )

    def init_project_sla(self):
        schedules = Schedule.init_schedule(project_key=self.key)
        sla_list = Sla.init_sla(schedules, project_key=self.key)
        self.grant_instance_permit(schedules)
        self.grant_instance_permit(sla_list)

    def init_custom_notify_template(self):
        from itsm.sla.models import CustomNotice

        CustomNotice.init_project_template(self.key)

    def grant_instance_permit(self, instances):
        from itsm.auth_iam.utils import grant_instance_creator_related_actions

        for instance in instances:
            instance.creator = self.creator
            instance.save()
            grant_instance_creator_related_actions(instance)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    @classmethod
    def init_default_project(cls):
        try:
            Project.objects.get_or_create(
                key=0, name="默认项目", desc="全局默认项目", creator="admin"
            )
            Project.objects.get_or_create(
                key=PUBLIC_PROJECT_PROJECT_KEY,
                name="公共项目",
                desc="全局公共项目，用于存放公共字段",
                creator="admin",
            )
        except BaseException as error:
            print("init_default_project error， error is {}".format(error))

    @classmethod
    def init_lesscode_project(cls):

        if Project.objects.filter(key="lesscode").exists():
            return
        try:
            project = Project.objects.create(
                key="lesscode", name="Lesscode", desc="蓝鲸低代码项目", creator="admin"
            )
            catalogs = copy.deepcopy(CATALOG)
            for catalog in catalogs:
                catalog["key"] = "{}_{}".format(project.key, catalog["key"])
                catalog["parent_key"] = "{}_{}".format(
                    project.key, catalog["parent_key"]
                )
            project.init_service_catalogs(catalogs)
            project.init_project_settings()
            project.init_project_sla()
            project.init_custom_notify_template()
        except BaseException as error:
            print("init_default_project error， error is {}".format(error))


class ProjectSettings(Model):
    type = models.CharField(_("类型"), max_length=LEN_NORMAL, default="FUNCTION")
    key = models.CharField(_("关键字唯一标识"), max_length=LEN_NORMAL, unique=False)
    value = models.TextField(_("系统设置值"), default=EMPTY_STRING, null=True, blank=True)
    project = models.ForeignKey("Project", help_text=_("项目"), on_delete=models.CASCADE)


class UserProjectAccessRecord(Model):
    username = models.CharField(_("用户名"), max_length=LEN_SHORT, primary_key=True)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    @classmethod
    def create_record(cls, username, project_key):
        with transaction.atomic():
            cls.objects.create(
                creator=username, username=username, project_key=project_key
            )

    def update_record(self, project_key):
        with transaction.atomic():
            self.project_key = project_key
            self.updated_by = self.username
            self.save()


class CostomTab(Model):
    name = models.CharField(_("名称"), max_length=LEN_SHORT)
    desc = models.CharField(_("描述"), max_length=LEN_LONG, null=True, blank=True)
    project_key = models.CharField(_("项目key"), max_length=LEN_SHORT)
    conditions = jsonfield.JSONField(
        _("筛选条件"), default=EMPTY_DICT, null=True, blank=True
    )
    order = models.IntegerField(_("排序"), default=FIRST_ORDER)
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()
