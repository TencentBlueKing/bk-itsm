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
import json
import os
import random
import string
import time
import six
from six.moves import range

from django.conf import settings
from django.db import models, transaction
from django.db.models import QuerySet
from django.db.models.signals import post_save

from common.log import logger
from itsm.component.constants import (
    COVERAGE_STATE,
    DEFAULT_END_AXIS,
    DEFAULT_ENGINE_VERSION,
    DEFAULT_FIRST_AXIS,
    DEFAULT_START_AXIS,
    DEFAULT_APPROVAL_AXIS,
    DIAMOND_SELECT_KEY,
    EMPTY,
    END_STATE,
    FIELD_BACK_MSG,
    FIELD_BIZ,
    FIELD_STATUS,
    FIELD_TERM_MSG,
    NORMAL_STATE,
    NORMAL_STATES,
    REJECT_MESSAGE,
    REJECT_SELECT_KEY,
    ROUTER_P_STATE,
    ROUTER_STATE,
    SHOW_BY_CONDITION,
    START_STATE,
    TABLE,
    EMPTY_STRING,
    EMPTY_DICT,
    SOURCE_WORKFLOW,
    SOURCE_TASK,
    FLOW_SIGNAL,
    STATE_SIGNAL,
    TRANSITION_SIGNAL,
    TASK_SIGNAL,
    SOPS_TASK,
    FLOW,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.db import managers
from itsm.component.utils.basic import (
    TempDisableSignal,
    create_version_number,
    dotted_name,
    get_model_fields,
    get_random_key,
)
from itsm.component.utils.bk_bunch import bunchify
from itsm.component.utils.misc import find_sub_string
from itsm.role.models import UserRole
from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.trigger.api import copy_triggers_by_source, restore_trigger_data


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeleteQuerySet, self).update(is_deleted=True)

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()


class TransitionQuerySet(SoftDeleteQuerySet):
    def delete(self):
        deleted_transition_info = []
        for row in self:
            deleted_transition_info.append({"from": row.from_state, "to": row.to_state})

        rows = super(SoftDeleteQuerySet, self).update(is_deleted=True)
        for row in deleted_transition_info:
            StateManager.update_state_label(
                row["from"], row["to"], operate_type="delete"
            )
        return rows


class Manager(managers.Manager):
    pass


class ConditionManager(Manager):
    """
    condition表级操作
    """

    def build_select_condition(self, key, operator, value, choices):
        """下拉选择条件构造"""

        return {
            "expressions": [
                {
                    "expressions": [
                        {
                            "key": key,
                            "condition": operator,
                            "value": value,
                            "source": "field",
                            "type": "SELECT",
                            "choiceList": choices,
                        }
                    ],
                    "type": "and",
                }
            ],
            "type": "and",
        }

    def build_yes_or_no(self, key, field_choice, cond_type="YES"):
        choices = [
            {"isDisabled": False, "id": c["key"], "name": c["name"]}
            for c in field_choice
        ]
        return self.build_select_condition(key, "==", cond_type, choices)


class WorkflowManager(Manager):
    """
    workflow表级操作
    """

    def draw_workflow(
        self,
        flow,
        name=None,
        dest=None,
        layout="LR",
        width=20,
        height=16,
        save=False,
        view=False,
    ):
        """转换为png图表，依赖graphviz"""

        from graphviz import Digraph

        name = name or flow.name

        f = Digraph(name, filename="%s.gv" % name, format="png")

        # 左右布局
        f.attr(rankdir=layout, size="{},{}".format(width, height))

        # 节点类型->形状
        shapes = {
            "START": "circle",  # 'circle
            "END": "doublecircle",
            "NORMAL": "box",  # 'ellipse'
            "ROUTER-P": "Mcircle",
            "COVERAGE": "Msquare",
            "ROUTER": "diamond",
            "TASK": "ellipse",
        }

        # 添加节点
        for node in flow.graphviz["nodes"].values():
            shape = shapes.get(node["type"])
            f.attr("node", shape=shape)
            f.node(name=str(node["id"]), label=node["name"])

        # 添加连线
        for edge in flow.graphviz["edges"]:
            from_node_id, to_node_id, label = edge
            f.edge(str(from_node_id), str(to_node_id), label)

        if view:
            # 看效果
            f.view()

        # 保存为source
        f.save()

        # 不需要保存
        if not save:
            return

        # 保存为图片到dest或者当前目录下
        if dest is None:
            dest = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(dest, name), "wb") as output_file:
            output_file.write(f.pipe(format="png"))

    def init_builtin_workflow(self):

        file_path = os.path.join(
            settings.PROJECT_ROOT,
            "initials",
            "workflow",
            "bk_itsm_builtin_workflow.json",
        )
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()

        for flow_data in json.loads(data):
            try:
                self.restore(flow_data)
            except BaseException as error:
                print(
                    "init workflow [{name}] error : {error}".format(
                        name=flow_data.get("name", "none"), error=str(error)
                    )
                )

    def init_iam_system(self):
        UserRole.objects.get_or_create(
            defaults={"role_type": "API", "role_key": "BK_IAM"},
            role_type="API",
            name="权限中心系统",
            members="",
            owners="admin",
            desc="权限中心系统",
            role_key="BK_IAM",
            creator="admin",
            is_builtin=True,
        )

    def init_iam_default_workflow(self):
        try:
            iam_default = os.path.join(
                settings.PROJECT_ROOT, "initials/workflow/iam_default.json"
            )
            with open(iam_default) as fp:
                data = json.load(fp)
                item = data[0]
                for state_id, state in item["states"].items():
                    if state["processors_type"] == "IAM":
                        processors = UserRole.objects.get(
                            role_type="IAM", role_key="super_manager"
                        ).id
                        state["processors"] = str(processors)
                item.update(is_builtin=True)
                self.restore(item)

            iam_user = os.path.join(
                settings.PROJECT_ROOT, "initials/workflow/iam_user.json"
            )
            with open(iam_user) as fp:
                data = json.load(fp)
                item = data[0]
                for state_id, state in item["states"].items():
                    if state["processors_type"] == "IAM":
                        processors = UserRole.objects.get(
                            role_type="IAM", role_key="rating_manager"
                        ).id
                        state["processors"] = str(processors)
                item.update(is_builtin=True)
                self.restore(item)
        except Exception as err:
            logger.exception("init_iam_default_workflow error, msg is {}".format(err))

    def init_bkbase_workflow(self):
        bkbase_path = os.path.join(
            settings.PROJECT_ROOT, "initials", "workflow", "bkbase"
        )
        bkbase_files = os.listdir(bkbase_path)
        for file in bkbase_files:
            file_path = os.path.join(bkbase_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            for flow_data in json.loads(data):
                try:
                    flows = self.filter(name=flow_data.get("name"))
                    if len(flows) > 0:
                        continue

                    flow_data.update(is_builtin=True)
                    self.restore(flow_data)
                except BaseException as error:
                    print(
                        "init workflow [{name}] error : {error}".format(
                            name=flow_data.get("name", "none"), error=str(error)
                        )
                    )

    def create_workflow(self, content):
        # workflow
        content.update(is_draft=False)
        return self.create(**content)

    def restore(self, data, operator="", for_migrate=False, name=None):
        """WorkflowVersion->Workflow's record"""
        case_one = (
            data.get("is_builtin")
            and self.filter(is_builtin=True, name=data.get("name")).exists()
        )
        case_two = (
            data.get("is_iam_used")
            and self.filter(is_iam_used=True, name=data.get("name")).exists()
        )
        if case_one or case_two:
            # 内置流程只能导入一次
            logger.info(
                "workflow exist, skip restore workflow {}".format(data.get("name"))
            )
            print("workflow exist, skip restore workflow {}".format(data.get("name")))
            return
        return self.clone(data, operator, for_migrate, name)

    @transaction.atomic
    def clone(self, data, operator="", for_migrate=False, name=None):
        from django.db.models.signals import post_save
        from itsm.workflow.signals.handlers import init_after_workflow_created
        from itsm.workflow.models import (
            State,
            Field,
            Transition,
            Table,
            TaskSchema,
            TaskConfig,
        )
        from itsm.iadmin.models import SystemSettings
        from distutils.dir_util import copy_tree

        states = data.pop("states")
        transitions = data.pop("transitions")
        fields = data.pop("fields")
        triggers = data.pop("triggers", [])
        task_schemas = data.pop("task_schemas", [])

        notify = data.pop("notify")
        table_data = data.pop("table")

        # 更新WorkflowVersion的is_biz_needed、is_supervise_needed、supervise_type、supervisor
        if for_migrate:
            data["is_biz_needed"] = data.get("extras", {}).get("biz_related", False)
            data["supervisor"] = data.get("extras", {}).get("urgers", "")
            data["is_supervise_needed"] = data.get("extras", {}).get("need_urge", False)
            data["supervise_type"] = data.get("extras", {}).get("urgers_type", "EMPTY")

        # remove and update some fields
        for field in [
            "id",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
            "states",
            "fields",
            "transitions",
            "version_message",
            "_state",
            "_flow_type_cache",
            "_prefetched_objects_cache",
            "pipeline_data",
        ]:
            data.pop(field, None)

        data.update(
            creator=operator,
            updated_by=operator,
            owners=operator,
            name=data["name"]
            if data.get("is_builtin")
            else "{name}-{version_number}".format(**data),
            version_number=create_version_number(),
        )

        if name is not None:
            data.update(name=name)

        old_workflow_id = data.pop("workflow_id")
        old_state_ids = list(states.keys())
        # 临时关闭post_save信号：init_after_workflow_created，恢复workflow
        with TempDisableSignal(post_save, init_after_workflow_created, self.model):
            workflow = self.create(**data)
            workflow.notify.set(notify)
            workflow.save()

        # 恢复table
        table, table_fields_map = Table.objects.restore(table_data)
        new_task_schemas, new_old_id_map = TaskSchema.objects.restore(
            task_schemas=task_schemas, operator=operator
        )

        new_workflow_id = workflow.id
        # 恢复state/transition/field
        _states, _state_map = State.objects.restore_states(states, new_workflow_id)
        _, _field_map = Field.objects.restore_fields(
            fields, workflow, _state_map, for_migrate
        )
        _, _transition_map = Transition.objects.restore_transitions(
            transitions, new_workflow_id, _state_map
        )
        if new_task_schemas:
            task_settings = workflow.extras.get("task_settings", [])
            if task_settings and isinstance(task_settings, dict):
                new_settings = []
                task_schema_ids = task_settings.pop("task_schema_ids")
                for schema_id in task_schema_ids:
                    task_setting = copy.deepcopy(task_settings)
                    task_setting["task_schema_id"] = schema_id
                    new_settings.append(task_setting)
                task_settings = new_settings

            task_objs = []
            for setting in task_settings:
                obj = TaskConfig(
                    workflow_id=new_workflow_id,
                    workflow_type=FLOW,
                    task_schema_id=setting["task_schema_id"],
                    create_task_state=setting["create_task_state"],
                    execute_task_state=setting["execute_task_state"],
                    execute_can_create=setting["execute_can_create"],
                    need_task_finished=setting["need_task_finished"],
                )
                task_objs.append(obj)
            TaskConfig.objects.bulk_create(task_objs)
            workflow.extras["task_settings"] = task_settings
        workflow.table = table
        workflow.save()

        restore_trigger_data(
            triggers,
            source_type=SOURCE_WORKFLOW,
            source_id=new_workflow_id,
            operator=operator,
            sender_map={
                STATE_SIGNAL: {str(key): value for key, value in _state_map.items()},
                TRANSITION_SIGNAL: {
                    str(key): value for key, value in _transition_map.items()
                },
                FLOW_SIGNAL: {str(old_workflow_id): new_workflow_id},
            },
        )
        # 刷新附件目录
        system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value

        for state_id in old_state_ids:
            old_path = os.path.join(
                system_file_path, "workflow_{}_{}".format(old_workflow_id, state_id)
            )
            if os.path.exists(old_path):
                new_path = os.path.join(
                    system_file_path,
                    "workflow_{}_{}".format(
                        new_workflow_id, _state_map.get(int(state_id), state_id)
                    ),
                )
                copy_tree(old_path, new_path)

        # 刷新自动过单的配置
        workflow.is_auto_approve = data.get("is_auto_approve", False)
        workflow.save()

        # 刷新脏数据
        StateManager.refresh_states(_states, _field_map)

        return workflow, _state_map, _transition_map

    @transaction.atomic
    def upgrade_workflow(
        self,
        flow_id=None,
        for_migrate=False,
        transition_map=None,
        state_map=None,
        ticket=None,
        **kwargs
    ):
        """升级workflow
        增加一个引擎版本号字段，旧流程版本号为空，新流程版本号为PIPELINE_VX
        新建流程、构建流程周边数据，复制普通节点，并处理一下特殊节点
        1、打回
        2、菱形
        3、场景

        for_migrate和transition_map：用于查找菱形节点的历史命中项
        """

        from itsm.workflow.models import Condition, Transition, Field

        # select old workflows by engine_version
        # workflows = self.exclude(engine_version=DEFAULT_ENGINE_VERSION)
        workflows = self.model._objects.all()
        if flow_id:
            workflows = workflows.filter(id=flow_id)

        group = kwargs.get("is_biz_group", False)
        biz_instance = kwargs.get("biz_instance")
        group_instance = kwargs.get("group_instance", None)

        for workflow in workflows:
            # fix transitions of router about accept transition
            Transition.objects.fix_old_workflow_transitions(workflow)

            # upgrade_fields
            self.fix_fields(workflow)

            axis_dict = {}
            new_old_state_map = {}
            for index, state in enumerate(workflow.master):
                x = 200 + 200 * index
                y = 50 + 50 * index
                axis_dict[str(state["id"])] = {"y": y, "x": x}
            if state_map:
                for o_s, n_s in list(state_map.items()):
                    axis_dict[str(n_s)] = axis_dict.pop(str(o_s), {})
                    new_old_state_map[n_s] = o_s

            print("migrate workflow-{}: {}".format(workflow.id, workflow.name))
            logger.info("migrate workflow-{}: {}".format(workflow.id, workflow.name))
            for state in workflow.states.all():
                state.axis = axis_dict.get(str(state.id), {})
                extras = state.extras
                transitions = workflow.transitions.filter(from_state_id=state.id)
                extra_transitions = extras.get("transitions", [])
                diamond_selected_transition_id = None

                # deprecated direction fixed
                for t in extra_transitions:
                    if t["direction"] == "BACK":
                        # print 'update direction back'
                        transitions.filter(id=t["id"]).update(direction="BACK")

                # # 路由分支历史命中
                if state.type == "ROUTER" and ticket:
                    last_log = ticket.logs.filter(
                        from_state_id=new_old_state_map[state.id]
                    ).last()
                    if last_log:
                        diamond_selected_transition_id = transition_map.get(
                            last_log.transition_id
                        )

                can_back = extras.get("can_back", False)
                can_distribute = extras.get("can_distribute", False)
                need_claim = extras.get("need_claim", False)
                back_transition = transitions.filter(direction="BACK").first()
                forward_transitions = transitions.filter(direction="FORWARD")

                state_reject_key = "{}{}".format(REJECT_SELECT_KEY, state.id)
                state_diamond_key = "{}{}".format(DIAMOND_SELECT_KEY, state.id)

                # 获取
                state_fields = state.fields

                # 普通节点的打回逻辑迁移 - 字段/线条条件
                if state.type != ROUTER_STATE and can_back and back_transition:
                    # 更新已有字段的展示条件

                    workflow.fields.filter(state_id=state.id).update(
                        show_conditions={
                            "expressions": [
                                {
                                    "value": "YES",
                                    "type": "SELECT",
                                    "condition": "==",
                                    "key": state_reject_key,
                                }
                            ],
                            "type": "and",
                        },
                        show_type=SHOW_BY_CONDITION,
                    )

                    # 创建字段：是否打回到【节点名】/单选下拉/是|否
                    field_name = "是否打回到【{}】".format(back_transition.to_state.name)
                    field_choice = [
                        {"key": "YES", "name": "是"},
                        {"key": "NO", "name": "否"},
                    ]
                    reject_field, created = workflow.fields.update_or_create(
                        state=state,
                        key=state_reject_key,
                        defaults={
                            "name": field_name,
                            "type": "SELECT",
                            "choice": field_choice,
                            "source_type": "CUSTOM",
                            "layout": "COL_12",
                            "is_builtin": True,
                            "desc": "旧流程迁移后自动创建的字段，对应以前的打回操作",
                            "is_tips": True,
                            "tips": "请慎重执行打回操作，并填写打回原因",
                        },
                    )
                    state_fields.insert(0, reject_field.id)

                    # 创建打回原因字段
                    message_field = self.create_reject_message_field(
                        state, workflow, state_reject_key, "YES"
                    )
                    state_fields.append(message_field.id)

                    # print 'reject: create(%s) field[%s] in state [%s]' % (created, field_name, state.name)
                    state.add_variables(state_reject_key, "SELECT", in_or_out="outputs")
                    # print 'reject: create condition for back_transition: %s' % back_transition.name

                    # 构造打回连线条件
                    yes_condition = Condition.objects.build_yes_or_no(
                        state_reject_key, field_choice, "YES"
                    )
                    Condition.objects.create(workflow=workflow, data=yes_condition)
                    transitions.filter(direction="BACK").update(
                        condition=yes_condition,
                        condition_type="by_field",
                        axis={"end": "Bottom", "start": "Bottom"},
                    )

                    # 构造非打回连线条件
                    no_condition = Condition.objects.build_yes_or_no(
                        state_reject_key, field_choice, "NO"
                    )
                    Condition.objects.create(workflow=workflow, data=no_condition)
                    forward_transitions.update(
                        condition=no_condition,
                        condition_type="by_field",
                        axis={"end": "Top", "start": "Right"},
                    )

                # 菱形迁移 - 合并打回字段和菱形选择字段/线条条件
                if state.type == ROUTER_STATE and (
                    forward_transitions.count() > 1 or back_transition
                ):
                    # 创建字段：节点名称/单选下拉/选项为出口线名称列表
                    field_name = state.name
                    field_choice = [
                        {"key": "OPTION-{}".format(ft.id), "name": ft.name}
                        for ft in forward_transitions
                    ]

                    if back_transition:
                        choice_name = "打回到【{}】".format(back_transition.to_state.name)
                        field_choice.append(
                            {
                                "key": "OPTION-{}".format(back_transition.id),
                                "name": choice_name,
                            }
                        )
                        transitions.filter(direction="BACK").update(
                            axis={"end": "Bottom", "start": "Bottom"}
                        )
                        # 有打回，则更新字段展示条件
                        workflow.fields.filter(state_id=state.id).update(
                            show_conditions={
                                "expressions": [
                                    {
                                        "value": "OPTION-{}".format(back_transition.id),
                                        "type": "SELECT",
                                        "condition": "==",
                                        "key": state_diamond_key,
                                    }
                                ],
                                "type": "and",
                            },
                            show_type=SHOW_BY_CONDITION,
                        )
                        # 创建打回原因
                        message_field = self.create_reject_message_field(
                            state,
                            workflow,
                            state_diamond_key,
                            "OPTION-{}".format(back_transition.id),
                        )
                        state_fields.append(message_field.id)

                    diamond_field, created = workflow.fields.update_or_create(
                        state=state,
                        key=state_diamond_key,
                        defaults={
                            "name": field_name,
                            "type": "SELECT",
                            "choice": field_choice,
                            "source_type": "CUSTOM",
                            "layout": "COL_12",
                            "is_builtin": True,
                            "desc": "旧流程迁移后自动创建的字段，对应以前的分支选项",
                            "is_tips": True,
                            "tips": "请慎重选择，不同选项对应不同的分支",
                        },
                    )
                    # print 'diamond: get or create(%s) field[%s] in state [%s]' % (created, field_name, state.name)
                    # 路由分支历史命中的选项值获取
                    diamond_selected_value = None
                    if for_migrate and diamond_selected_transition_id:
                        # 历史命中选项：OPTION-{transition_id}
                        for fc in field_choice:
                            fc_id = int(fc["key"].split("-")[-1])
                            if diamond_selected_transition_id == fc_id:
                                diamond_selected_value = fc["key"]
                                break
                        else:
                            raise NotImplementedError("should never be here")

                    state_fields.insert(0, diamond_field.id)
                    state.add_variables(
                        state_diamond_key,
                        "SELECT",
                        in_or_out="outputs",
                        default=diamond_selected_value,
                    )

                    # 构造连线条件
                    for fc in field_choice:
                        cond_select = Condition.objects.build_select_condition(
                            state_diamond_key, "==", fc["key"], field_choice
                        )
                        fc_id = fc["key"].split("-")[-1]
                        fct = transitions.get(id=fc_id)
                        fct.condition = cond_select
                        fct.condition_type = "by_field"
                        fct.save()

                # remove [FIELD_BACK_MSG, FIELD_TERM_MSG]
                for field in workflow.fields.filter(
                    state_id=state.id, key__in=[FIELD_BACK_MSG, FIELD_TERM_MSG]
                ):
                    try:
                        state_fields.remove(field.id)
                    except Exception:
                        pass

                # 提单节点业务字段
                if state.type == "NORMAL" and state.is_builtin is True:
                    if workflow.is_biz_needed:
                        if group:
                            group_field = workflow.fields.create(
                                name=settings.BIZ_GROUP_DESC,
                                api_instance_id=group_instance.id,
                                source_type="API",
                                type="SELECT",
                                kv_relation={
                                    "name": "bk_inst_name",
                                    "key": "bk_inst_id",
                                },
                                key=settings.BIZ_GROUP_CONF["biz_obj_id"],
                                desc=settings.BIZ_GROUP_DESC,
                                state=state,
                            )
                            state_fields.insert(1, group_field.id)
                            Field._objects.filter(
                                key=FIELD_BIZ, id__in=state.fields
                            ).update(
                                api_instance_id=biz_instance.id,
                                source_type="API",
                                type="SELECT",
                                kv_relation={"name": "bk_biz_name", "key": "bk_biz_id"},
                                related_fields={"rely_on": [group_field.key]},
                                desc="请选择业务",
                            )
                        else:
                            Field._objects.filter(
                                key=FIELD_BIZ, id__in=state.fields
                            ).update(
                                api_instance_id=biz_instance.id,
                                source_type="API",
                                type="SELECT",
                                kv_relation={"name": "bk_biz_name", "key": "bk_biz_id"},
                                desc="请选择业务",
                            )
                # 更新
                state.fields = state_fields

                # 填充场景字段
                if can_distribute and need_claim:
                    state.distribute_type = "DISTRIBUTE_THEN_CLAIM"
                elif need_claim:
                    state.distribute_type = "CLAIM_THEN_PROCESS"
                elif can_distribute:
                    state.distribute_type = "DISTRIBUTE_THEN_CLAIM"
                else:
                    state.distribute_type = "PROCESS"

                # 菱形节点转换为普通节点
                if state.type == ROUTER_STATE:
                    state.type = NORMAL_STATE

                # extras -> state.assignors/assignors_type/delivers/delivers_type
                # {
                # "assignor": "admin,poc_admin,admin",
                # "transitions": [],
                # "branches": [],
                # "can_back": false,
                # "deliver_to": "admin,admin,guest",
                # "assignor_type": "PERSON",
                # "can_deliver": true,
                # "can_distribute": true,
                # "need_claim": false
                # }
                state.assignors_type = extras.get("assignor_type", "EMPTY") or "EMPTY"
                state.assignors = extras.get("assignor", "")
                state.can_deliver = extras.get("can_deliver", False)
                if state.can_deliver:
                    state.delivers_type = "PERSON"
                    state.delivers = extras.get("deliver_to", "")

                state.save()

                # 更新引擎版本为默认的最新版本，避免重复迁移

            workflow.engine_version = DEFAULT_ENGINE_VERSION
            workflow.save()
            print("migrate workflow success: %s" % workflow.id)
            logger.info("migrate workflow success: %s" % workflow.id)

        return workflows

    def fix_fields(self, workflow):
        workflow.fields.all().update(related_fields={})
        workflow.fields.filter(key="fault_level").update(
            source_type="DATADICT", source_uri="FAULT_LEVEL_INIT"
        )
        workflow.fields.filter(key="event_type").update(
            source_type="DATADICT",
            source_uri="EVENT_TYPE",
        )

    def create_reject_message_field(self, state, workflow, key, select_value):
        message_field, created = workflow.fields.update_or_create(
            state=state,
            key="{}{}".format(REJECT_MESSAGE, state.id),
            defaults={
                "name": "打回原因",
                "type": "TEXT",
                "choice": [],
                "source_type": "CUSTOM",
                "layout": "COL_12",
                "is_builtin": True,
                "desc": "旧流程迁移后自动创建的字段，对应以前的打回原因",
                "is_tips": False,
                "tips": "",
                "show_conditions": {
                    "expressions": [
                        {
                            "value": select_value,
                            "type": "SELECT",
                            "condition": "!=",
                            "key": key,
                        }
                    ],
                    "type": "and",
                },
                "show_type": SHOW_BY_CONDITION,
            },
        )
        return message_field


class StateManager(Manager):
    """
    state表级操作
    """

    def create_states(self, workflow_id, states):
        obj_map = {}
        for state_id, state in states.items():
            state.update(workflow_id=workflow_id)
            obj = self.create(**state)
            obj_map[state_id] = obj.pk
        return obj_map

    def create_start_state(self, workflow_id):
        """创建开始节点"""

        return self.create(
            workflow_id=workflow_id,
            name="开始",
            type="START",
            is_draft=False,
            is_builtin=True,
            axis=DEFAULT_START_AXIS,
            label="G",
        )

    def create_end_state(self, workflow_id, axis=DEFAULT_END_AXIS):
        """创建结束节点"""

        return self.create(
            workflow_id=workflow_id,
            name="结束",
            type="END",
            is_draft=False,
            is_builtin=True,
            axis=axis,
            label="G",
        )

    def create_first_state(self, workflow, name):
        """创建初始节点"""
        with transaction.atomic():
            first_state = self.create(
                workflow_id=workflow.id,
                name=name,
                type="NORMAL",
                is_draft=False,
                is_builtin=True,
                axis=DEFAULT_FIRST_AXIS,
                label="G",
            )

            # 初始化初始阶段的默认字段
            first_state.fields = list(
                workflow.fields.filter(is_builtin=True)
                .exclude(key=FIELD_STATUS)
                .values_list("id", flat=True)
            )
            first_state.save()

            return first_state

    def create_approval_state(self, workflow, name):
        """创建初始节点"""
        with transaction.atomic():
            approval_state = self.create(
                workflow_id=workflow.id,
                name=name,
                type="APPROVAL",
                is_draft=False,
                is_builtin=False,
                axis=DEFAULT_APPROVAL_AXIS,
                label="G",
                processors_type="VARIABLE",
                processors="APPROVER",
            )

            return approval_state

    def fields_of_state(self, state_id):
        return self.get(id=state_id).fields

    def update_outputs_variables(self, conditions, workflow_id):
        """
        更新线条条件变化关联的输出变量
        """
        from itsm.workflow.models import Field, GlobalVariable

        field_outputs = [
            expression["key"]
            for expressions in conditions["expressions"]
            for expression in expressions["expressions"]
            if expression["source"] == "field"
        ]
        global_outputs = [
            expression["key"]
            for expressions in conditions["expressions"]
            for expression in expressions["expressions"]
            if expression["source"] == "global"
        ]

        # 基础模型中的字段默认所有节点可用，无需设置到某个节点
        fields = []
        for item in Field.objects.filter(
            key__in=field_outputs, workflow_id=workflow_id
        ).values("key", "type", "state", "source"):
            if item["source"] != "TABLE":
                fields.append(
                    {
                        "key": item["key"],
                        "type": item["type"],
                        "source": "field",
                        "state": item["state"],
                    }
                )

        # 插入字段变量
        for field in fields:
            state = self.get(id=field["state"])
            if not state.variables.get("outputs"):
                state.variables["outputs"] = []

            exist_field_key = [
                item["key"]
                for item in state.variables["outputs"]
                if item["source"] == "field"
            ]

            if field["key"] not in exist_field_key:
                state.variables["outputs"].append(field)

            state.save()

        # 插入全局变量
        global_variables = [
            {
                "key": item["key"],
                "type": item["type"],
                "source": "global",
                "state": item["state_id"],
            }
            for item in GlobalVariable.objects.filter(
                key__in=global_outputs, flow_id=workflow_id
            ).values("key", "type", "state_id")
        ]

        for variable in global_variables:
            state = self.get(id=variable["state"])
            if not state.variables.get("outputs"):
                state.variables["outputs"] = []

            exist_variable_key = [
                item["key"]
                for item in state.variables["outputs"]
                if item["source"] == "global"
            ]

            if variable["key"] not in exist_variable_key:
                state.variables["outputs"].append(variable)

            state.save()

    @transaction.atomic
    def restore_states(self, states, workflow_id):
        """states->State's record
        还原前后的记录ID映射关系：1->2,3->4,5->6
        """
        from itsm.workflow.models import GlobalVariable

        state_map = {}
        restored_states = []

        for state_id, state in states.items():
            for key in [
                "id",
                "key",
                "create_at",
                "update_at",
                "creator",
                "updated_by",
                "workflow",
                "distribute_rule",
                "distribute_keys",
                "order",
                "is_first_state",
            ]:
                state.pop(key, None)

            api_info = state.pop("api_info", None)

            # 更新字段
            state.update(workflow_id=workflow_id)

            # 旧流程版本数据兼容处理
            for k in ["fields", "extras"]:
                if isinstance(state[k], six.string_types):
                    state[k] = json.loads(state[k])
            if state["type"] == "TASK":
                # API字段的还原
                try:
                    # 用于还原
                    # 导入的时候出现的问题
                    logger.info("api_info is {}".format(api_info))
                    remote_api_info = api_info.pop("remote_api_info")
                    for key in [
                        "remote_system_name",
                        "remote_system_id",
                        "auth_actions",
                        "remote_system",
                        "count",
                        "id",
                    ]:
                        remote_api_info.pop(key, None)
                        api_info.pop(key, None)

                    remote_api_info["name"] = "{}({})".format(
                        remote_api_info["name"], create_version_number()
                    )

                    api = RemoteApi.restore_api(remote_api_info, "system")
                    api_info["remote_api_id"] = api.id
                    api_instance = RemoteApiInstance.objects.create(**api_info)
                except BaseException as error:
                    logger.exception("restore api state error %s" % str(error))
                    api_instance = None

                state["api_instance_id"] = api_instance.id if api_instance else 0

            state_restored = self.create(**state)
            restored_states.append(state_restored)
            state_map[int(state_id)] = state_restored.id

            # 批量创建全局变量
            variables_outputs = state["variables"].get("outputs", [])
            GlobalVariable.objects.bulk_create_global_variables(
                variables_outputs, state_restored.id, workflow_id
            )
        return restored_states, state_map

    @classmethod
    def refresh_states(cls, states, field_map):
        """更新state中的相关id"""

        for state in states:
            # 兼容脏数据
            state.fields = [x for x in [field_map.get(f) for f in state.fields] if x]
            state.save()

    @classmethod
    def update_state_label(cls, from_state, to_state, operate_type="add"):
        """
        添加或者删除线条的时候更新状态的label
        """

        def set_empty(state):
            if state.type in [START_STATE, END_STATE]:
                state.label = "G"

            elif state.transitions_to.filter(is_deleted=False).exists():
                # 当前节点的前面存在连线，不需要改变label
                return

            elif not (
                state.transitions_from.filter(is_deleted=False).exists()
                or state.transitions_to.filter(is_deleted=False).exists()
            ):
                # 如果前后都不存在连线，直接置空
                state.label = EMPTY

            state.save()

        def set_all_route_p_empty():
            from itsm.workflow.models import State

            State.objects.filter(label__contains=from_state.label).update(label=EMPTY)

        def set_empty_from():
            # 如果 from 为 EMPTY，并且与 to_state 为普通节点和网关节点的交叉连接

            if from_state.type == COVERAGE_STATE:
                # 如果为空的聚合网关连接，直接返回
                return

            if to_state.type == ROUTER_P_STATE:
                # to 为 并行网关，则from 取 |p 之前的前缀，表示上一级是一致的
                from_state_label = find_sub_string(to_state.label, "|")

            elif to_state.type == COVERAGE_STATE:
                # to 为 合并网关，则表示from 是在对应合并网关的一个子区间内，此时获取到相同的前缀，加上普通节点的label即可
                from_state_label = "{prefix}|N{state_id}".format(
                    prefix=find_sub_string(to_state.label, "|"), state_id=from_state.id
                )
            else:
                # TODO test tostate为普通节点，from 为网关的时候
                from_state_label = to_state.label
            from_state.label = from_state_label
            # from_state 相关流程的empty都需要修改为from_state 一致
            from_state.save()

            cls.update_related_states_label(from_state)

        def set_empty_to():
            # 如果to_state为空的时候
            if to_state.type == ROUTER_P_STATE:
                # 如果to 为 并行网关， 分为几种情况

                _prefix = (
                    find_sub_string(from_state.label, "|P")
                    if from_state.type == COVERAGE_STATE
                    else from_state.label
                )
                to_state_label = "{}|P{}".format(_prefix, to_state.id)
            if to_state.type == COVERAGE_STATE:
                label = from_state.label
                if from_state.type == COVERAGE_STATE:
                    label = find_sub_string(label, "|P")
                _prefix = find_sub_string(label, "|N")
                # from 为并行分支，to 为聚合网关不合法，直接忽略
                to_state_label = "{}|C{}".format(_prefix, to_state.id)
            if to_state.type in NORMAL_STATES:
                _prefix = from_state.label
                if from_state.type == COVERAGE_STATE:
                    _prefix = find_sub_string(_prefix, "|P")
                if from_state.type == ROUTER_P_STATE:
                    _prefix = "{}|N{}".format(_prefix, to_state.id)
                to_state_label = _prefix
            to_state.label = to_state_label
            to_state.save()
            cls.update_related_states_label(to_state)

        if operate_type == "delete":
            if not from_state.is_deleted:
                set_empty(from_state)
            if not to_state.is_deleted:
                if from_state.type == ROUTER_P_STATE:
                    set_all_route_p_empty()
                else:
                    set_empty(to_state)
            return

        if (
            EMPTY not in [from_state.label, to_state.label]
            or from_state.label == to_state.label
        ):
            # 本来label存在并且部位空的时候，不需要修改
            # 第一种情况：不包含空位，说明工作区间已经确定
            # 第二种情况：还没有合入到主流程的时候，所有节点都为EMPTY，采用默认即可
            return

        if {from_state.type, to_state.type}.issubset(set(NORMAL_STATES)):
            # 如果是普通节点之间的连接，直接根据前后节点不为空的label赋值
            if from_state.label == EMPTY:
                from_state.label = to_state.label
                from_state.save()
            else:
                to_state.label = from_state.label
                to_state.save()
            return

        if from_state.label == EMPTY:
            return set_empty_from()

        if to_state.label == EMPTY:
            return set_empty_to()

    @classmethod
    def update_related_states_label(cls, current_state):
        cls.update_next_states_label(current_state)
        cls.update_pre_states_label(current_state)

    @classmethod
    def update_next_states_label(cls, current_state):
        next_states = [
            t.to_state
            for t in current_state.transitions_from.filter(is_deleted=False)
            if t.to_state.label == EMPTY
        ]
        for state in next_states:
            cls.update_state_label(current_state, state)

    @classmethod
    def update_pre_states_label(cls, current_state):
        pre_states = [
            t.from_state
            for t in current_state.transitions_to.filter(is_deleted=False)
            if t.from_state.label == EMPTY
        ]
        for state in pre_states:
            cls.update_state_label(state, current_state)


class TransitionManager(Manager):
    """
    transition表级操作
    """

    def get_queryset(self):
        return TransitionQuerySet(self.model).filter(is_deleted=False)

    def create_accept_transitions(self, workflow_id, states):
        """
        创建主流程的所有accept流转
            states: [
                {
                    'id': '1',
                    'name': 'xxx',
                    ...
                }
            ]
        """

        from .models import State

        transitions = []

        for index, state in enumerate(states[:-1]):
            from_state_id = state.get("id")

            # 自动砍断从from_state_id出发的accept-transitions
            from_state = State.objects.get(pk=from_state_id)

            # 砍断后接入新的节点
            next_accept_transition = self.filter(from_state_id=from_state_id).exclude(
                pk__in=from_state.extras.get("branches", [])
            )

            next_accept_transition.delete()
            next_state_id = states[index + 1].get("id")

            obj, created = self.get_or_create(
                defaults={
                    "name": "确定",
                    "direction": "FORWARD",
                },
                workflow_id=workflow_id,
                from_state_id=from_state_id,
                to_state_id=next_state_id,
            )

            transitions.append(obj.pk)

        return transitions

    def create_transitions(self, workflow_id, transitions, state_map):
        obj_map = {}

        from .models import State

        for transition_id, transition in transitions.items():
            _, from_key, to_key = transition_id.split("-")

            if from_key == "start":
                from_state_key = State.objects.get(
                    workflow_id=workflow_id, type="START"
                ).pk
            else:
                from_state_key = state_map.get(from_key)

            if to_key == "end":
                to_state_key = State.objects.get(workflow_id=workflow_id, type="END").pk
            else:
                to_state_key = state_map.get(to_key)

            transition.update(
                workflow_id=workflow_id,
                from_state_id=from_state_key,
                to_state_id=to_state_key,
            )
            obj = self.create(**transition)
            obj_map[transition_id] = obj.pk
        return obj_map

    def create_forward_transition(
        self,
        workflow_id,
        from_state_id,
        to_state_id,
        is_builtin=False,
        name="通过",
        creator="system",
    ):
        """正向连接两个状态"""

        return self.create(
            name=name,
            workflow_id=workflow_id,
            from_state_id=from_state_id,
            to_state_id=to_state_id,
            is_builtin=is_builtin,
            creator=creator,
            updated_by=creator,
        )

    @transaction.atomic
    def restore_transitions(self, transitions, workflow_id, state_map):
        """transitions->Transition's record"""

        from itsm.workflow.models import Transition

        _transitions = []
        transition_map = {}

        for transition_id, transition in transitions.items():

            for key in [
                "id",
                "create_at",
                "update_at",
                "creator",
                "updated_by",
                "workflow",
                "type",
            ]:
                transition.pop(key, None)

            # 兼容以前数据
            try:
                from_state_id, to_state_id = (
                    transition.pop("from_state"),
                    transition.pop("to_state"),
                )
            except KeyError:
                from_state_id, to_state_id = (
                    transition.pop("from_state_id"),
                    transition.pop("to_state_id"),
                )

            transition.update(
                workflow_id=workflow_id,
                from_state_id=state_map[from_state_id],
                to_state_id=state_map[to_state_id],
            )

            transition_restored = Transition.objects.create(**transition)
            _transitions.append(transition_restored)

            transition_map[int(transition_id)] = transition_restored.id

        return _transitions, transition_map

    def fix_old_workflow_transitions(self, workflow):
        # fix transitions of router
        for mi in list(range(0, len(workflow.master)))[:-1]:
            self.model._objects.filter(
                from_state_id=workflow.master[mi]["id"],
                to_state_id=workflow.master[mi + 1]["id"],
                is_deleted=True,
            ).update(is_deleted=False, name="默认(通过)")


class FieldManager(Manager):
    """
    field表级操作
    """

    def create_table_fields(self, workflow, fields):

        from itsm.workflow.models import TemplateField, Field
        from itsm.component.utils.basic import get_model_fields

        w_fields = []
        field_names = get_model_fields(TemplateField, name_only=True)
        for field in fields:
            field_values = {
                field_name: getattr(field, field_name, "") for field_name in field_names
            }
            field_values.pop("id", None)
            field_values.pop("flow_type", None)
            field_values.pop("table", None)
            field_values.pop("project_key", None)
            field_values.update(workflow=workflow, source=TABLE)
            w_fields.append(Field(**field_values))
        self.bulk_create(w_fields)

    def create_fields(self, workflow_id, fields):
        for field_id, field in fields.items():
            field.update(workflow_id=workflow_id)
            self.create(**field)

    @transaction.atomic
    def restore_fields(self, fields, workflow, state_map, for_migrate=False):
        """fields->Field's record"""

        _fields = []
        field_map = {}

        for field_id, field in fields.items():
            try:
                # 去除以前业务字段是由is_valid判断是否出现的逻辑
                if field["key"] == FIELD_BIZ and not workflow.is_biz_needed:
                    continue

                # 去除以前FIELD_BACK_MSG, FIELD_TERM_MSG
                if field["key"] in [FIELD_BACK_MSG, FIELD_TERM_MSG] and for_migrate:
                    continue

                for key in ["id", "create_at", "update_at", "creator", "updated_by"]:
                    field.pop(key, None)

                api_info = field.pop("api_info", None)
                state_id = field.pop("state_id")

                # TODO unicode isinstance(field['choice'], (str, unicode))
                if isinstance(field["choice"], str):
                    choice = json.loads(field["choice"])
                else:
                    choice = field["choice"]

                if "meta" in field and not isinstance(field["meta"], dict):
                    field["meta"] = json.loads(field["meta"])

                if not isinstance(field["related_fields"], (dict, list)):
                    field["related_fields"] = json.loads(field["related_fields"])

                field.update(
                    workflow_id=workflow.id,
                    state_id=state_map.get(state_id),
                    choice=choice,
                )

                # 旧流程迁移跳过的步骤：API字段
                if not for_migrate and field["source_type"] == "API":
                    # API字段的还原
                    try:
                        # 用于还原
                        # 导入的时候出现的问题
                        remote_api_info = api_info["remote_api_info"]
                        api_instance_info = api_info["api_instance_info"]

                        remote_api_info["name"] = "{}({})".format(
                            remote_api_info["name"], create_version_number()
                        )

                        api = RemoteApi.restore_api(remote_api_info, "system")
                        api_instance_info["remote_api"] = api
                        api_instance = RemoteApiInstance.objects.create(
                            **api_instance_info
                        )
                    except BaseException:
                        api_instance = RemoteApiInstance._objects.get(
                            id=field.get("api_instance_id")
                        )
                        api_instance.id = None
                        api_instance.is_deleted = False
                        api_instance.save()
                        api_instance.refresh_from_db()

                    field["api_instance_id"] = api_instance.id

                field_restored = self.create(**field)
                _fields.append(field_restored)

                field_map[int(field_id)] = field_restored.id
            except Exception as e:
                logger.error(
                    "import workflow fields[{}] error: {}".format(field["key"], e)
                )

        return _fields, field_map


class TemplateFieldManager(Manager):
    """
    字段库 表级操作
    """

    def create_default_template_field(self, default_template_fields):

        for f in default_template_fields:
            if self.filter(key=f[4]).exists():
                # 防止重复创建覆盖已有的内容
                instance = self.filter(key=f[4]).first()
                if f[4] == "bk_biz_id":
                    if instance.api_instance_id == 0:
                        api_instance = RemoteApiInstance.create_default_api_instance(
                            func_name="search_business",
                            req_params={},
                            req_body={"fields": ["bk_biz_id", "bk_biz_name"]},
                            rsp_data="data.info",
                        )
                        instance.api_instance_id = api_instance.id
                    instance.kv_relation = {"name": "bk_biz_name", "key": "bk_biz_id"}
                    instance.save()
                instance.project_key = PUBLIC_PROJECT_PROJECT_KEY
                instance.save()
                continue
            defaults = {
                "name": f[0],
                "type": f[1],
                "source_type": f[2],
                "choice": f[3],
                "display": f[5],
                "related_fields": f[6],
                "source_uri": f[7],
                "desc": f[8],
                "is_builtin": f[9],
                "is_readonly": f[10],
                "is_valid": f[11],
                "regex": f[12],
                "layout": "COL_12",
                "project_key": PUBLIC_PROJECT_PROJECT_KEY,
            }
            self.update_or_create(key=f[4], defaults=defaults)


class TableManager(Manager):
    """
    基础模型 表级操作
    """

    def init_table(self, tables):
        """创建默认基础模型"""
        from itsm.workflow.models import TemplateField, Workflow

        for table in tables:
            obj, created = self.get_or_create(is_builtin=True, name=table[0])
            if not created:
                # 已经存在的，直接忽略
                continue

            field_values = TemplateField.objects.filter(key__in=table[2]).values(
                "id", "key"
            )
            field_values = sorted(field_values, key=lambda x: table[2].index(x["key"]))
            fields = [field["id"] for field in field_values]
            obj.fields.set(fields)
            obj.fields_order = fields
            obj.desc = table[1]
            obj.save()

        # 初始化默认基础模型
        Workflow.objects.filter(table=None).update(table_id=1)

    def is_same_to(self, table, table_data):
        """判断导入的基础模型数据和系统内同id的基础模型的差异"""

        if table.fields.count() != len(table_data.fields):
            return False

        # 比较公共字段差异
        for tf in table_data.fields:
            if not table.fields.filter(key=tf.key).exists():
                return False

        return True

    def create_table(self, table_data):
        """利用导入的数据创建模型
        新建模型，并复原公共字段
        """
        from itsm.workflow.models import TemplateField

        fields_map = {}

        table = self.create(
            name="{}_{}".format(table_data.name, create_version_number()),
            desc=table_data.desc,
            is_builtin=False,
        )

        model_attrs = get_model_fields(TemplateField)
        for field in table_data.fields:
            template_field = {
                attr: field.get(attr, "")
                for attr in model_attrs
                if attr not in TemplateField.FIELDS
            }
            old_field_id = template_field.pop("id")

            new_field, created = TemplateField.objects.get_or_create(
                defaults=template_field,
                key=field.key,
            )
            fields_map[old_field_id] = new_field.id

        new_fields_order = [fields_map[f] for f in table_data.fields_order]
        table.fields.set(list(fields_map.values()))
        table.fields_order = new_fields_order
        table.save()

        return table, fields_map

    def restore(self, data):
        """从快照复原table"""

        if not data:
            return None, None

        table_data = bunchify(data)
        is_builtin = table_data.pop("is_builtin", False)

        try:
            table = (
                self.get(is_builtin=True, name=table_data.name)
                if is_builtin
                else self.get(id=table_data.id, version=table_data.version)
            )
            if self.is_same_to(table, table_data):
                return table, {f: f for f in table_data.fields_order}

        except self.model.DoesNotExist:
            return self.create_table(table_data)

        return self.create_table(table_data)


class WorkflowSnapManager(models.Manager):
    """
    workflow 版本表级操作
    """

    def create_snapshot(self, workflow, operator=""):
        """创建快照信息"""

        # 统一key为string
        states = {}
        for item in list(workflow.states.values()):
            # 固化state中处理角色为提单人的处理人列表为提单人
            if item.get("processors_type") == "STARTER":
                item.update(processors_type="PERSON", processors=dotted_name(operator))
            states[str(item["id"])] = item

        transitions = {
            str(item["id"]): item for item in list(workflow.transitions.values())
        }
        fields = {
            str(item["id"]): item
            for item in list(workflow.fields.filter(is_valid=True).values())
        }

        tag = self.create(
            workflow_id=workflow.id,
            states=states,
            master=workflow.master,
            transitions=transitions,
            notify_rule=workflow.notify_rule,
            notify_freq=workflow.notify_freq,
            fields=fields,
        )

        for item in workflow.notify.all():
            tag.notify.add(item)

        return tag


class WorkflowVersionManager(Manager):
    """
    workflow 版本表级操作
    """

    def service_cnt(self, instance):
        from itsm.service.models import Service

        return Service.objects.filter(workflow_id=instance["id"]).count()

    def get_or_create_version_from_workflow(self):
        """抛弃旧的流程版本，合并流程快照到最后一个流程版本"""

        from itsm.workflow.models import Workflow, WorkflowSnap, WorkflowVersion

        total = Workflow._objects.all().count()
        print("get_or_create_version_from_workflow, total workflow: %s" % total)

        ver_for_snaps = {}
        count = 0
        # 创建流程最新版本，并聚合快照（被删除的流程相关的工单也需要迁移）
        for workflow in Workflow._objects.all():
            # workflow对应的快照
            snaps = set(
                WorkflowSnap.objects.filter(workflow_id=workflow.pk).values_list(
                    "id", flat=True
                )
            )
            count += 1
            # 跳过已有版本的迁移（避免重复迁移）
            try:
                version = WorkflowVersion._objects.get(workflow_id=workflow.id)
                print(
                    "skip exist workflow version: {}({})".format(
                        version.name, version.version_number
                    )
                )
            except WorkflowVersion.DoesNotExist:
                version = workflow.create_version("system")
                print(
                    "create workflow version: {}({})".format(
                        version.name, version.version_number
                    )
                )

            ver_for_snaps[version.pk] = snaps
            print(
                "update workflow: {}, cnt={}, workflow_number={}".format(
                    workflow.name, len(snaps), count
                )
            )

        return ver_for_snaps

    @transaction.atomic
    def upgrade_version(
        self, version_id=None, for_migrate=False, ticket=None, **kwargs
    ):
        """
        升级流程版本：version->workflow->upgrade->new version

        for_migrate: True，转为迁移未完成单据的流程版本，嵌入了额外处理逻辑（历史执行信息）
        """

        from itsm.workflow.models import Workflow

        old_version = self.model._objects.get(id=version_id)
        data = copy.deepcopy(old_version.__dict__)
        data.update(notify=list(old_version.notify.values_list("id", flat=True)))

        workflow, states_map, transition_map = Workflow.objects.restore(
            data, "system", for_migrate=True
        )
        Workflow.objects.upgrade_workflow(
            workflow.id, for_migrate, transition_map, states_map, ticket, **kwargs
        )

        # 部署流程
        version_name = "{}_{}".format(old_version.name, old_version.id)
        new_version = workflow.create_version(
            name=version_name, operator=old_version.creator
        )

        logger.info("create tmp version: %s" % version_name)
        # 选择性删除升级后的版本
        if old_version.is_deleted:
            new_version.delete()

        # 删除临时流程和旧流程版本
        workflow.delete()
        old_version.delete()

        return new_version, states_map, transition_map


class GlobalVariableManager(Manager):
    def create_global_variable(self, state_id, flow_id, inst_data, validate_data):
        """创建全局变量"""
        mapping = {"string": "STRING", "number": "INT", "boolean": "BOOLEAN"}
        inst_data_dict = {item["ref_path"]: item["key"] for item in inst_data}

        # 取消有效
        self.filter(state_id=state_id, flow_id=flow_id).update(is_valid=False)
        for gvar in validate_data:
            if gvar["source"] != "global":
                continue
            key = get_random_key(gvar["name"])
            if key[0].isdigit():
                # 开头为数字，重新生成
                first_letter = random.choice(string.ascii_letters)
                key = first_letter + key[1:]
            gvar.update(
                {
                    "type": mapping.get(gvar["type"], gvar["type"]),
                    "key": inst_data_dict.get(gvar["ref_path"], key),
                }
            )
            self.update_or_create(
                key=gvar["key"],
                state_id=state_id,
                flow_id=flow_id,
                defaults={
                    "name": gvar["name"],
                    "type": gvar["type"],
                    "is_valid": True,
                },
            )
        return validate_data

    def bulk_create_global_variables(self, variables, state_id, flow_id):
        """根据state下的variables 批量创建global variables"""
        global_variables = [
            self.model(
                name=variable.get("name", EMPTY_STRING),
                type=variable["type"],
                key=variable["key"],
                meta=variable.get("meta", EMPTY_DICT),
                state_id=state_id,
                flow_id=flow_id,
                is_valid=True,
            )
            for variable in variables
            if variable["source"] == "global"
        ]
        self.bulk_create(global_variables)


class TriggerManager(Manager):
    # TODO
    def restore_triggers(self, triggers, new_workflow_id, state_map):
        trigger_map = {}
        restored_triggers = []

        for pk, item in triggers.items():

            # drop dirty data
            for key in ["id", "create_at", "update_at", "creator", "updated_by"]:
                item.pop(key, None)

            item["workflow_id"] = new_workflow_id
            item["state_id"] = state_map.get(item["state_id"])
            restored_trigger = self.create(**item)
            restored_triggers.append(restored_trigger)
            trigger_map[int(pk)] = restored_trigger.pk

        return restored_triggers, trigger_map


class TaskSchemaManager(Manager):
    """
    任务模版的 manager
    """

    def clone(self, src_schema_ids, can_edit=True, is_draft=False):
        """
        复制任务模板
        """
        from itsm.workflow.signals.handlers import task_schema_created_handler

        # 排除临时TaskSchema创建后的信号，避免重复创建字段
        with TempDisableSignal(post_save, task_schema_created_handler, self.model):

            dst_schema_ids = []
            for schema_id in src_schema_ids:
                src_schema = self.get(id=schema_id)
                src_fields = src_schema.all_fields.all()
                # src_schema.id = None
                src_schema.name = "{}_{}".format(
                    src_schema.name, create_version_number()
                )
                dst_schema = copy.deepcopy(src_schema)
                dst_schema.id = None
                dst_schema.can_edit = can_edit
                dst_schema.is_draft = is_draft
                # 复制出来的模板，必须为非内置可删除
                dst_schema.is_builtin = False
                dst_schema.save()
                dst_schema.refresh_from_db(fields=["id"])

                # 字段的更新
                for field in src_fields:
                    field.id = None
                    field.task_schema = dst_schema
                    field.save()

                # 触发器的更新
                copy_triggers_by_source(
                    src_source_type="task",
                    src_source_id=schema_id,
                    dst_source_type="task",
                    dst_source_id=dst_schema.id,
                )

                dst_schema_ids.append(dst_schema.id)
        return dst_schema_ids

    def tag_data(self, src_schema_ids):
        task_schemas = []
        for task_schema in self.filter(id__in=src_schema_ids):
            task_schemas.append(task_schema.tag_data())
        return task_schemas

    def restore(self, task_schemas, operator=""):
        """
        导入TaskSchema的值
        """
        from itsm.workflow.signals.handlers import task_schema_created_handler

        new_ids = []
        new_old_id_map = {}
        for task_schema in task_schemas:
            if task_schema["component_type"] == SOPS_TASK:
                # 标准运维类型的任务直接不做导入，直接引用现有的任务模板
                sops_task_id = self.get(component_type=SOPS_TASK, can_edit=True).id
                new_ids.append(sops_task_id)
                new_old_id_map[task_schema["id"]] = sops_task_id
                continue
            triggers = task_schema.pop("triggers", [])
            fields = task_schema.pop("fields")
            # 对于导入的任务，默认设置为草稿
            old_task_id = task_schema.pop("id", None)
            task_schema.update(
                id=None,
                is_draft=False,
                creator=operator,
                updated_by=operator,
                name="{}-{}".format(task_schema["name"], int(time.time())),
            )
            with TempDisableSignal(post_save, task_schema_created_handler, self.model):
                new_instance = self.create(**task_schema)
            restore_trigger_data(
                triggers,
                SOURCE_TASK,
                new_instance.id,
                operator,
                sender_map={TASK_SIGNAL: {str(old_task_id): new_instance.id}},
            )
            new_instance.restore_fields(fields)
            new_ids.append(new_instance.id)
            new_old_id_map[old_task_id] = new_instance.id
        return new_ids, new_old_id_map


class TaskSchemaFieldManager(Manager):
    """
    任务字段管理
    """

    def restore(self, fields, task_schema):
        """
        批量导入一个任务的字段
        """
        new_fields = []
        for field in fields:
            for key in [
                "id",
                "create_at",
                "update_at",
            ]:
                field.pop(key, None)

            api_info = field.pop("api_info", None)

            if "meta" in field and not isinstance(field["meta"], dict):
                field["meta"] = json.loads(field["meta"])

            if not isinstance(field["related_fields"], (dict, list)):
                field["related_fields"] = json.loads(field["related_fields"])

            field.update(
                task_schema_id=task_schema.id,
                creator=task_schema.creator,
                updated_by=task_schema.updated_by,
            )

            if field["source_type"] == "API":
                # API字段的还原
                try:
                    # 用于还原
                    remote_api_info = api_info["remote_api_info"]
                    api_instance_info = api_info["api_instance_info"]

                    remote_api_info["name"] = "{}({})".format(
                        remote_api_info["name"], create_version_number()
                    )

                    api = RemoteApi.restore_api(remote_api_info, "system")
                    api_instance_info["remote_api"] = api
                    api_instance = RemoteApiInstance.objects.create(**api_instance_info)
                except BaseException:
                    api_instance = RemoteApiInstance._objects.get(
                        id=field.get("api_instance_id")
                    )
                    api_instance.id = None
                    api_instance.is_deleted = False
                    api_instance.save()
                    api_instance.refresh_from_db()

                field["api_instance_id"] = api_instance.id

            new_fields.append(self.model(**field))

        self.bulk_create(new_fields)
