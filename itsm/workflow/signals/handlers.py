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
import random
import string

from django.db import transaction
from django.db.models import Q

from itsm.component.constants import (
    FIELD_BIZ,
    SIGN_STATE,
    SIGN_VARIABLES,
    SIGN_FIELDS,
    TASK_FIELDS_SCHEMA,
    SOPS_TASK_FIELDS_SCHEMA,
    SOPS_TASK,
    APPROVAL_FIELDS,
    APPROVAL_STATE,
    APPROVAL_VARIABLES,
    DEVOPS_TASK,
    DEVOPS_TASK_FIELDS_SCHEMA,
)
from itsm.component.exceptions import WorkFlowError
from itsm.component.utils.basic import get_random_key
from itsm.workflow.models import (
    Field,
    State,
    TemplateField,
    Transition,
    GlobalVariable,
    TaskFieldSchema,
    Workflow,
    Table,
    WorkflowVersion,
)
from itsm.workflow.serializers import TemplateFieldSerializer


def generate_key(name):
    """
    数字开头的key会导致mako渲染报错，固对数字开头的key做统一处理
    """
    key = get_random_key(name)
    if key[0].isdigit():
        # 开头为数字，重新生成
        first_letter = random.choice(string.ascii_letters)
        key = first_letter + key[1:]
    return key


def state_created_handler(sender, flow_id, state_id, state_type, **kwargs):
    """节点创建后的触发操作"""
    # Sign state need create extra variables
    if state_type == SIGN_STATE:
        sign_update(state_id, flow_id)
    elif state_type == APPROVAL_STATE:
        approval_update(state_id, flow_id)


def sign_update(state_id, flow_id):
    global_variables = []
    state = State.objects.get(id=state_id)
    for variable in SIGN_VARIABLES:
        variable["flow_id"] = flow_id
        variable["state_id"] = state_id
        variable["key"] = generate_key(variable["name"])
        global_variables.append(GlobalVariable(**variable))
        state.add_variables(
            variable["key"],
            variable["type"],
            name=variable["name"],
            source="global",
            meta=variable["meta"],
        )
    GlobalVariable.objects.bulk_create(global_variables)

    # Create sign state built-in fields
    field_ids = []
    for sign_field in SIGN_FIELDS:
        sign_field.update(
            key=generate_key(sign_field["name"]),
            state_id=state_id,
            workflow_id=flow_id,
        )
        # Bulk create cannot get PK
        field = Field.objects.create(**sign_field)
        field_ids.append(field.id)
    state.fields = field_ids
    state.save()


def approval_update(state_id, flow_id):
    global_variables = []
    state = State.objects.get(id=state_id)
    for variable in APPROVAL_VARIABLES + SIGN_VARIABLES:
        variable["flow_id"] = flow_id
        variable["state_id"] = state_id
        variable["key"] = generate_key(variable["name"])
        global_variables.append(GlobalVariable(**variable))
        state.add_variables(
            variable["key"],
            variable["type"],
            name=variable["name"],
            source="global",
            meta=variable["meta"],
        )
    GlobalVariable.objects.bulk_create(global_variables)
    field_ids = []
    key = ""
    for approval_field in APPROVAL_FIELDS:
        field_key = generate_key(approval_field["name"])
        show_conditions = approval_field.get("show_conditions")
        if not show_conditions:
            key = field_key
        else:
            approval_field["show_conditions"]["expressions"][0]["key"] = key
        approval_field.update(key=field_key, state_id=state_id, workflow_id=flow_id)
        field = Field.objects.create(**approval_field)
        field_ids.append(field.id)
    state.fields = field_ids
    state.save()


def state_deleted_handler(sender, flow_id, state_id, **kwargs):
    Transition.objects.filter(
        Q(from_state_id=state_id) | Q(to_state_id=state_id)
    ).delete()
    GlobalVariable.objects.filter(flow_id=flow_id, state_id=state_id).delete()


def task_schema_created_handler(sender, instance, created, *args, **kwargs):
    """任务模板创建后的触发操作"""
    if not created:
        return
    if instance.component_type == SOPS_TASK:
        task_field_schema_objs = [
            TaskFieldSchema(task_schema_id=instance.id, **task_field)
            for task_field in SOPS_TASK_FIELDS_SCHEMA
        ]
    elif instance.component_type == DEVOPS_TASK:
        task_field_schema_objs = [
            TaskFieldSchema(task_schema_id=instance.id, **task_field)
            for task_field in DEVOPS_TASK_FIELDS_SCHEMA
        ]
    else:
        task_field_schema_objs = [
            TaskFieldSchema(task_schema_id=instance.id, **task_field)
            for task_field in TASK_FIELDS_SCHEMA
        ]
    TaskFieldSchema.objects.bulk_create(task_field_schema_objs)


def init_after_workflow_created(sender, instance, created, *args, **kwargs):
    """工作流创建后的关联数据初始化"""

    if not created:
        return

    if instance.name == "内置审批流" and instance.flow_type == "internal":
        return

    if instance.table:
        ordering = "FIELD(`id`, %s)" % ",".join(
            [str(field_id) for field_id in instance.table.fields_order]
        )
        fields = TemplateField.objects.filter(
            id__in=instance.table.fields_order, is_builtin=True
        )

        if not instance.is_biz_needed:
            fields.exclude(key=FIELD_BIZ)

        fields = fields.extra(select={"ordering": ordering}, order_by=("ordering",))

        try:
            Field.objects.create_table_fields(instance, fields)
        except BaseException as error:
            instance.delete()
            raise WorkFlowError("create table field error:%s" % str(error))

    # 默认创建三个节点
    try:
        start_state = State.objects.create_start_state(instance.pk)
    except BaseException as error:
        instance.delete()
        raise WorkFlowError("create start state error:%s" % str(error))

    try:
        first_state = State.objects.create_first_state(instance, name="提单")
    except BaseException as error:
        instance.delete()
        raise WorkFlowError("create first state error:%s" % str(error))

    try:
        end_state = State.objects.create_end_state(instance.pk)
    except BaseException as error:
        instance.delete()
        raise WorkFlowError("create end state error:%s" % str(error))

    # 默认串行连线：start->first->end
    try:
        Transition.objects.create_forward_transition(
            instance.pk, start_state.pk, first_state.pk, True, ""
        )
        Transition.objects.create_forward_transition(
            instance.pk, first_state.pk, end_state.pk, True, "默认"
        )
    except BaseException as error:
        instance.delete()
        raise WorkFlowError("create transition error:%s" % str(error))

    # 为什么还会有save()
    instance.save()


def after_basic_model_saved(sender, instance, created, *args, **kwargs):
    """
    基础模型修改之后，直接删除掉不存在的字段
    """
    if created:
        return
    Field.objects.filter(
        workflow__in=instance.used_workflow.all(), source="TABLE"
    ).exclude(key__in=instance.fields.values_list("key", flat=True)).delete()


def after_base_field_saved(sender, instance, created, *args, **kwargs):
    """
    基础公共字段修改属性之后，更新到对应的流程节点字段
    """
    if created:
        return

    field = TemplateFieldSerializer(instance).data
    field.pop("id")
    field_names = {field.name for field in Field._meta.fields}
    field_data_keys = set(field.keys())
    for name in field_data_keys - field_names:
        field.pop(name)

    base_models = instance.tables.all()

    Field.objects.filter(workflow__table__in=base_models, key=instance.key).update(
        **field
    )


def builtin_approval_workflow_create():
    """工作流创建后的关联数据初始化"""
    # 1、微信。 2、邮箱
    with transaction.atomic():
        if Workflow.objects.filter(name="内置审批流", flow_type="internal").exists():
            return WorkflowVersion.objects.get(name="内置审批流", flow_type="internal")
        table = Table.objects.get(id=1)
        instance = Workflow.objects.create(
            table=table,
            name="内置审批流",
            flow_type="internal",
            is_revocable=True,
            is_enabled=True,
            is_draft=False,
            notify_rule="ONCE",
            notify_freq=0,
            creator="",
            updated_by="admin",
            is_builtin=True,
        )
        instance.notify.add(1, 2)

        # 先创建基础模型内字段，后面节点从基础模型添加字段依赖这些字段
        if instance.table:
            fields = TemplateField.objects.filter(key="title", is_builtin=True)
            Field.objects.create_table_fields(instance, fields)

        # 默认创建三个节点
        start_state = State.objects.create_start_state(instance.pk)
        first_state = State.objects.create_first_state(instance, name="提单")
        approver_field = Field.objects.create(
            workflow=instance,
            name="审批人",
            key="APPROVER",
            type="MEMBERS",
            state=first_state,
            layout="COL_12",
        )
        approve_content_field = Field.objects.create(
            workflow=instance,
            name="审批内容",
            key="APPROVAL_CONTENT",
            type="TEXT",
            state=first_state,
        )

        first_state.fields.append(approver_field.pk)
        first_state.fields.append(approve_content_field.pk)
        first_state.save()

        approval_state = State.objects.create_approval_state(instance, name="内置审批节点")
        approval_update(approval_state.id, approval_state.workflow_id)

        end_state = State.objects.create_end_state(
            instance.pk, axis={"x": 890, "y": 150}
        )

        # 默认串行连线：start->first->approval->end
        Transition.objects.create_forward_transition(
            instance.pk, start_state.pk, first_state.pk, True, ""
        )
        Transition.objects.create_forward_transition(
            instance.pk, first_state.pk, approval_state.pk, True, "默认"
        )
        Transition.objects.create_forward_transition(
            instance.pk, approval_state.pk, end_state.pk, True, "默认"
        )
        instance.save()
        version = instance.create_version(name=instance.name, operator="")
        return version
