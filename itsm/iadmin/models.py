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
import os
import re

import jsonfield
import mistune
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import ugettext as _

from config.default import PROJECT_ROOT
from itsm.component.constants import (
    EMPTY_LIST,
    EMPTY_STRING,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.db import managers
from itsm.component.fields import IOField
from itsm.component.utils.basic import now
from itsm.iadmin.contants import (
    ACTION_CHOICES,
    DEFAULT_SETTINGS,
    NOTIFY_TEMPLATE,
    GENERAL_NOTIFY_TEMPLATE_LIST,
)

# 匹配版本
VERSION_PATTERN = re.compile(r".*:(.*)].*")
# 匹配日期
DATA_PATTERN = re.compile(r"(\d{4}-\d{1,2}-\d{1,2})")


class Model(models.Model):
    """基础字段"""

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    _objects = models.Manager()

    auth_resource = {"resource_type": "system_settings", "resource_type_name": "系统配置"}
    resource_operations = ["system_settings_manage"]

    class Meta:
        app_label = "iadmin"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()


class SystemSettings(Model):
    type = models.CharField(_("类型"), max_length=LEN_NORMAL)
    key = models.CharField(_("关键字唯一标识"), max_length=LEN_NORMAL, unique=True)
    value = models.TextField(_("系统设置值"), default=EMPTY_STRING, null=True, blank=True)

    objects = managers.Manager()

    class Meta:
        app_label = "iadmin"
        verbose_name = _("系统设置")
        verbose_name_plural = _("系统设置")

    def __unicode__(self):
        return "{}({})".format(self.type, self.key)

    @classmethod
    def init_default_settings(cls, *args, **kwargs):
        for setting in DEFAULT_SETTINGS:
            SystemSettings.objects.get_or_create(
                defaults={
                    "type": setting[1],
                    "value": setting[2],
                    "creator": "system",
                    "updated_by": "system",
                },
                key=setting[0],
            )


class CustomNotice(models.Model):
    """自定义通知模板"""

    title_template = models.CharField(
        _("标题模板"),
        max_length=LEN_LONG,
        default="",
        null=True,
        blank=True,
        help_text=_("工单字段的值可以作为参数写到模板中，格式如：【ITSM】${service}管理单【${action}】提醒"),
    )
    content_template = models.TextField(
        _("内容模板"),
        default="",
        null=True,
        blank=True,
        help_text=_("工单字段的值可以作为参数写到模板中，格式如：单号:${sn}"),
    )
    action = models.CharField(
        _("通知模板类型"), max_length=LEN_SHORT, choices=ACTION_CHOICES, default="default"
    )
    notify_type = models.CharField(_("通知方式"), max_length=LEN_SHORT, default="EMAIL")
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("更新人"), max_length=LEN_NORMAL, default="system")
    used_by = models.CharField(_("使用者"), max_length=LEN_NORMAL, default="system")
    version = models.CharField(_("版本"), max_length=LEN_SHORT, default="V1")

    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=PUBLIC_PROJECT_PROJECT_KEY
    )

    auth_resource = {"resource_type": "flow_element", "resource_type_name": "流程元素"}
    resource_operations = ["flow_element_manage"]

    class Meta:
        app_label = "iadmin"
        verbose_name = _("通知模板")
        verbose_name_plural = _("通知模板")

    def __unicode__(self):
        return "%s-%s" % (self.get_action_display(), self.notify_type)

    @property
    def action_name(self):
        return self.get_action_display()

    @classmethod
    def init_project_template(cls, project_key):
        # 1.获取第三方通知方式
        from itsm.workflow.utils import get_third_party_notify_type

        third_party_notify_type_list = get_third_party_notify_type()
        # 2.初始化第三方通知方式模版
        third_party_notify_template_list = []
        for notify_type in third_party_notify_type_list:
            general_notify_template = copy.deepcopy(GENERAL_NOTIFY_TEMPLATE_LIST)
            for template in general_notify_template:
                template[3] = notify_type
            third_party_notify_template_list.extend(general_notify_template)

        for template in NOTIFY_TEMPLATE + third_party_notify_template_list:
            try:
                CustomNotice.objects.get(
                    action=template[2],
                    notify_type=template[3],
                    used_by=template[4],
                    version="V2",
                    project_key=project_key,
                )
            except CustomNotice.DoesNotExist:
                CustomNotice.objects.create(
                    **{
                        "title_template": template[0],
                        "content_template": template[1],
                        "action": template[2],
                        "used_by": template[4],
                        "notify_type": template[3],
                        "version": "V2",
                        "project_key": project_key,
                    }
                )
            except CustomNotice.MultipleObjectsReturned:
                CustomNotice.objects.filter(
                    action=template[2],
                    notify_type=template[3],
                    project_key=project_key,
                ).delete()
                CustomNotice.objects.create(
                    **{
                        "title_template": template[0],
                        "content_template": template[1],
                        "used_by": template[4],
                        "version": "V2",
                        "action": template[2],
                        "notify_type": template[3],
                        "project_key": project_key,
                    }
                )

    @classmethod
    def init_default_template(cls, *args, **kwargs):

        # 升级（V1->V2）或初始化通知模板
        if CustomNotice.objects.filter(version="V1").exists():
            CustomNotice.objects.filter(version="V1").delete()

        from itsm.project.models import Project

        project_keys = Project.objects.filter(is_deleted=False).values_list(
            "key", flat=True
        )

        for project_key in project_keys:
            # 公共项目不参与初始化通知模板
            if project_key == PUBLIC_PROJECT_PROJECT_KEY:
                continue
            cls.init_project_template(project_key=project_key)


class ReleaseVersionLogManager(models.Manager):
    @classmethod
    def init_version_log_info(cls, lang="zh-cn"):
        print("init version log info for <{}>".format(lang))

        LANG_FILES = {
            "zh-cn": "docs/RELEASE.md",
            "en": "docs/RELEASE_EN.md",
        }

        lang_file = LANG_FILES.get(lang, "zh-cn")

        # 日志文件中读取日志信息
        file_path = os.path.join(PROJECT_ROOT, lang_file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            ReleaseVersionLog.objects.filter(lang=lang).delete()

        ver_logs = content.strip().split("##")[1:]

        # 用于解析markdown的工具
        mk = mistune.Markdown()

        # 遍历从文件中读取的日志信息并存入数据库
        for outer_index, item in enumerate(ver_logs):
            item = item.strip()
            lines = item.split("\n")

            version, create_at, log = "", "", ""
            for inner_index, value in enumerate(lines):
                if inner_index == 0:
                    string = str(value)
                    # 正则匹配版本的日期
                    version = VERSION_PATTERN.findall(string)[0].strip()
                    create_at = DATA_PATTERN.findall(string)[0].strip()
                else:
                    log += mk(value.strip())

            vers = version.split(".")
            version_size = int(vers[0]) * 1000 + int(vers[1]) * 100 + int(vers[2]) * 1
            ReleaseVersionLog.objects.update_or_create(
                version=version,
                lang=lang,
                log=log,
                create_at=create_at,
                is_latest=(outer_index == 0),
                version_size=version_size,
            )


class ReleaseVersionLog(models.Model):
    """版本日志"""

    version = models.CharField(_("版本号"), max_length=LEN_NORMAL)
    log = models.TextField(_("日志内容"), default=EMPTY_STRING, null=True, blank=True)
    lang = models.CharField(_("语言"), max_length=64, default="zh-cn")
    create_at = models.DateField(_("日期"))
    is_latest = models.BooleanField(_("是否最新版本"), default=False)
    version_size = models.IntegerField(_("版本号大小"), default=0)

    objects = ReleaseVersionLogManager()

    class Meta:
        app_label = "iadmin"
        verbose_name = _("版本日志")
        verbose_name_plural = _("版本日志")


class MigrateLogs(models.Model):
    """数据迁移日志"""

    version_from = models.CharField(_("旧版本"), max_length=LEN_NORMAL)
    version_to = models.CharField(_("新版本"), max_length=LEN_NORMAL)
    operator = models.CharField(_("升级人"), max_length=LEN_NORMAL, blank=True)
    create_at = models.DateTimeField(_("记录创建日期"), auto_now_add=True, blank=True)
    note = models.TextField(_("备注"), null=True, blank=True)
    exe_func = jsonfield.JSONField(_("执行的函数"), default=EMPTY_LIST, blank=True)
    is_finished = models.BooleanField(_("是否执行结束"), default=False)
    is_success = models.BooleanField(_("是否迁移成功"), default=False)

    class Meta:
        app_label = "iadmin"
        verbose_name = _("数据迁移日志")
        verbose_name_plural = _("数据迁移日志")


class DataManager(models.Manager):
    """排除过期数据"""

    def get_queryset(self):
        return QuerySet(self.model).exclude(expire_at__lte=now())


class Data(models.Model):
    """数据存储"""

    TYPE_CHOICES = (
        ("string", _("字符串")),
        ("hash", _("哈希值")),
        ("list", _("列表")),
        ("set", _("集合")),
        ("zset", _("有序集合")),
    )
    key = models.CharField(_("关键字"), max_length=LEN_MIDDLE, db_index=True)
    value = IOField(verbose_name=_("值"))
    type = models.CharField(
        _("类型"), choices=TYPE_CHOICES, default="string", max_length=LEN_SHORT
    )
    expire_at = models.DateTimeField(_("过期时间"), null=True, blank=True, db_index=True)

    objects = DataManager()

    auth_resource = {"resource_type": "flow_element", "resource_type_name": "流程元素"}
    resource_operations = ["flow_element_manage"]

    class Meta:
        app_label = "iadmin"
        verbose_name = _("数据存储")
        verbose_name_plural = _("数据存储")

    def __str__(self):
        return "{}({})".format(self.key, self.type)
