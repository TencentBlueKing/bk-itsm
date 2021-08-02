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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

import jsonfield
from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    EMPTY_DICT,
    LEN_MIDDLE,
    LEN_NORMAL,
    TASK_COMPONENT_CHOICE,
    TASK_STAGE_CHOICE,
    LEN_X_LONG,
    EMPTY_STRING,
    TASK_STAGE_LIST,
    TASK_GLOBAL_VARIABLES,
    TICKET_GLOBAL_VARIABLES,
    LEN_XX_LONG,
    SOURCE_TASK,
    LEN_SHORT,
    TASK_TYPE,
)
from itsm.workflow.models import Model, BaseField
from itsm.workflow.managers import TaskSchemaManager, TaskSchemaFieldManager
from itsm.trigger.models import Trigger


class TaskSchema(Model):
    """
    任务模型
    """

    fields = (
    "id", "name", "is_builtin", "component_type", "desc", "is_draft", "can_edit", "owners")

    name = models.CharField(_("任务模版的名称"), max_length=LEN_MIDDLE, null=False)
    is_builtin = models.BooleanField(_("是否内置"), default=False)
    component_type = models.CharField(_("任务组件类型"), choices=TASK_COMPONENT_CHOICE,
                                      max_length=LEN_NORMAL)
    desc = models.CharField(_("任务模版的名称"), max_length=LEN_X_LONG, default=EMPTY_STRING, blank=True)
    is_draft = models.BooleanField(_("是否为草稿"), default=True)
    is_enabled = models.BooleanField(_("是否为开启状态"), default=False)
    owners = models.CharField(_("负责人"), max_length=LEN_XX_LONG, default=EMPTY_STRING)

    can_edit = models.BooleanField(_("是否可编辑状态"), help_text=_("当为流程version引用的时候，不可编辑和查看"),
                                   default=True)
    inputs = jsonfield.JSONField(_("组件输入信息"), help_text=_("当前组件输入参数引用的参数变量"), default=EMPTY_DICT)

    objects = TaskSchemaManager()

    need_auth_grant = True

    auth_resource = {"resource_type": "task_template", "resource_type_name": "任务模板"}
    resource_operations = ["task_template_view", "task_template_manage"]

    class Meta:
        app_label = "workflow"
        verbose_name = _("任务模型")
        verbose_name_plural = _("任务模型")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.component_type)

    def get_variables(self, stage=None):
        if stage not in TASK_STAGE_LIST:
            return []

        valid_stages = []
        for _stage in TASK_STAGE_LIST:
            valid_stages.append(_stage)
            if _stage == stage:
                # 获取的阶段只包含当前阶段和之前阶段
                break

        variables = [
            {"key": _field.key, "type": _field.type, "source": "field", "name": _field.name,
             "choice": _field.choice}
            for _field in self.all_fields.all()
        ]

        variables.extend(TASK_GLOBAL_VARIABLES)
        variables.extend(TICKET_GLOBAL_VARIABLES)
        if self.component_type == "SOPS":
            variables.append(
                {"key": "sops_relate_id", "type": "string", "source": "ticket", "name": "REL单号",
                 "choice": []}
            )
        # 工单内的信息更新
        variables.extend(self.inputs.get("ticket_variables", []))
        return variables

    def tag_data(self):
        triggers = []
        for trigger in Trigger.objects.filter(source_type=SOURCE_TASK, source_id=self.id):
            triggers.append(trigger.tag_data())
        fields = []
        for field in self.all_fields.all():
            fields.append(field.tag_data())

        return dict(id=self.id, name=self.name, component_type=self.component_type,
                    triggers=triggers, fields=fields)

    def restore_fields(self, fields):
        TaskFieldSchema.objects.restore(fields, self)


class TaskFieldSchema(BaseField):
    """任务对应的表单字段"""

    task_schema = models.ForeignKey(TaskSchema, related_name="all_fields", help_text=_("对应的任务模型"),
                                    on_delete=models.CASCADE)
    stage = models.CharField(_("所处阶段"), choices=TASK_STAGE_CHOICE, default="CREATE",
                             max_length=LEN_NORMAL)
    sequence = models.IntegerField(_("序号"), default=0)

    objects = TaskSchemaFieldManager()

    class Meta:
        app_label = "workflow"
        verbose_name = _("任务字段表")
        verbose_name_plural = _("任务字段表")
        ordering = ("-id", "sequence")

    def __unicode__(self):
        return "{}({})".format(self.name, self.task_schema.name)


class TaskConfig(Model):
    """
    任务配置
    """

    workflow_id = models.IntegerField(_("流程id"), db_index=True)
    workflow_type = models.CharField(_("流程类型"), choices=TASK_TYPE, max_length=LEN_SHORT)
    task_schema_id = models.IntegerField(_("任务模版id"))
    create_task_state = models.IntegerField(_("任务创建节点"))
    execute_task_state = models.IntegerField(_("任务执行节点"))
    execute_can_create = models.BooleanField(_("执行节点是否可创建"), default=False)
    need_task_finished = models.BooleanField(_("流转是否需要任务全部完成"), default=False)

    class Meta:
        app_label = "workflow"
        verbose_name = _("任务配置")
        verbose_name_plural = _("任务配置")
        index_together = (
            ("create_task_state", "workflow_id"),
            ("execute_task_state", "workflow_id"),
        )
