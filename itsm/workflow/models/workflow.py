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
import six

import jsonfield
from django.db import models, transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.utils.translation import ugettext as _
from rest_framework.exceptions import ValidationError

from itsm.component.constants import (
    DEFAULT_ENGINE_VERSION,
    DEFAULT_STRING,
    DEFAULT_VERSION,
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_LIST,
    EMPTY_STRING,
    FIELD_BIZ,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    TICKET_GLOBAL_VARIABLES,
    LEN_XX_LONG,
    SOURCE_TICKET,
    SOURCE_WORKFLOW,
    REVOKE_TYPE,
    REQUIRED_FIELD,
    FLOW,
    VERSION,
    NORMAL_STATE,
    SIGN_STATE,
    APPROVAL_STATE,
    TASK_STATE,
    TASK_SOPS_STATE,
)
from itsm.component.drf.mixins import ObjectManagerMixin
from itsm.component.utils.basic import create_version_number, list_by_separator
from itsm.component.utils.graph import dfs_paths
from itsm.postman.models import RemoteApiInstance
from itsm.trigger.api import copy_triggers_by_source
from itsm.trigger.models import Trigger
from itsm.workflow import managers
from .base import Model
from .field import Field, Table
from .task import TaskSchema, TaskConfig
from .common import GlobalVariable, Notify


class WorkflowBase(ObjectManagerMixin, Model):
    """流程模板"""

    name = models.CharField(_("流程名"), max_length=LEN_MIDDLE)
    desc = models.CharField(
        _("流程描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    flow_type = models.CharField(
        _("流程分类"), max_length=LEN_NORMAL, default=DEFAULT_STRING
    )
    is_enabled = models.BooleanField(_("是否启用"), default=False, db_index=True)
    is_revocable = models.BooleanField(_("是否可撤销"), default=True)
    revoke_config = jsonfield.JSONField(
        _("撤销配置"),
        default={"type": REVOKE_TYPE.FIRST, "state": 0},
        null=True,
        blank=True,
    )
    is_draft = models.BooleanField(_("是否为草稿"), default=True)
    is_builtin = models.BooleanField(_("是否为系统内置"), default=False)
    is_task_needed = models.NullBooleanField(_("是否需要关联子任务"), default=False, null=True)
    owners = models.CharField(_("负责人"), max_length=LEN_XX_LONG, default=EMPTY_STRING)

    notify = models.ManyToManyField("workflow.Notify", help_text=_("可关联多种通知方式"))
    notify_rule = models.CharField(
        _("通知规则"), max_length=LEN_SHORT, choices=NOTIFY_RULE_CHOICES, default="NONE"
    )
    notify_freq = models.IntegerField(_("重试间隔(s)"), default=EMPTY_INT)

    # 业务逻辑字段
    is_biz_needed = models.BooleanField(_("是否绑定业务"), default=False)
    # 是否自动过单
    is_auto_approve = models.BooleanField(_("是否自动过单"), default=False)
    is_iam_used = models.BooleanField(_("是否使用IAM角色"), default=False)
    is_supervise_needed = models.BooleanField(_("是否需要督办"), default=False)
    supervise_type = models.CharField(
        _("督办人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    supervisor = models.CharField(
        _("督办列表"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    engine_version = models.CharField(
        _("引擎版本：空/PIPELINE_VX"), max_length=LEN_NORMAL, null=True, blank=True
    )
    version_number = models.CharField(
        _("版本号"), max_length=LEN_NORMAL, default=DEFAULT_VERSION
    )

    # deprecated fields
    master = jsonfield.JSONField(_("主分支列表"), default=EMPTY_LIST, null=True, blank=True)
    extras = jsonfield.JSONField(
        _("其他配置信息"),
        default={
            # 强制业务关联
            "biz_related": False,
            # 督办相关
            "need_urge": False,
            "urgers_type": "EMPTY",
            "urgers": EMPTY_STRING,
            "task_settings": [],
        },
    )

    # need_auth_grant = True

    class Meta:
        abstract = True


class Workflow(WorkflowBase):
    """流程模板"""

    table = models.ForeignKey(
        Table,
        help_text=_("关联的基础模型"),
        related_name="used_workflow",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    # deprecated fields
    service = models.CharField(
        _("对应的服务类型，为服务的主键"),
        max_length=LEN_NORMAL,
        null=True,
        blank=True,
        default="default",
    )

    service_property = jsonfield.JSONField(
        _("对应服务的属性，为json字段"), default=EMPTY_DICT, null=True, blank=True
    )

    objects = managers.WorkflowManager()

    auth_resource = {"resource_type": "workflow", "resource_type_name": "流程"}
    resource_operations = ["workflow_manage", "workflow_deploy"]

    class Meta:
        app_label = "workflow"
        verbose_name = _("流程模板")
        verbose_name_plural = _("流程模板")
        ordering = ("-id",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.pk)

    def tag_data(self, operator="", message="", need_tag_task=False):
        """创建新的流程版本"""

        # 统一key为string
        states = {str(state.pk): state.serialized_data for state in self.states.all()}

        transitions = {
            str(transition.pk): transition.serialized_data
            for transition in self.transitions.all()
        }

        fields, be_relied = {}, {}
        valid_fields = []  # 只获取有效的字段
        for state in self.states.all():
            valid_fields.extend(state.fields)
        for field in self.fields.all().filter(id__in=valid_fields):
            try:
                field_info = field.tag_data()
            except Exception as err:
                raise ValidationError(
                    "节点{}字段{}存在异常,请检查字段配置,详情:{}".format(
                        field.state.name, field.name, err
                    )
                )
            fields[str(field.id)] = field_info

            cur_field_key = field_info["key"]
            for field_key in field_info["related_fields"].get("rely_on", []):
                if field_key not in be_relied:
                    be_relied[field_key] = [cur_field_key]
                else:
                    be_relied[field_key].append(cur_field_key)

        for field in list(fields.values()):
            if field["key"] in be_relied:
                field["related_fields"]["be_relied"] = be_relied[field["key"]]

        # update before fields removed
        data = model_to_dict(
            self,
            exclude=[
                "id",
                "creator",
                "create_at",
                "end_at",
                "update_at",
                "notify",
                "extras",
                "updated_by",
                "service",
                "service_property",
                "_state",
                "master",
            ],
        )

        exclude_fields = []
        if not self.is_biz_needed:
            exclude_fields.append(FIELD_BIZ)

        if need_tag_task:
            task_config = TaskConfig.objects.filter(workflow_id=self.id)
            task_schema_ids = [task_info.task_schema_id for task_info in task_config]
            task_schemas = TaskSchema.objects.tag_data(task_schema_ids)
            data.update(task_schemas=task_schemas)

        triggers = []
        for trigger in Trigger.objects.filter(
            source_type=SOURCE_WORKFLOW, source_id=self.id
        ):
            triggers.append(trigger.tag_data())

        data.update(
            creator=operator,
            updated_by=operator,
            workflow_id=self.id,
            version_number=create_version_number(),
            version_message=message,
            states=states,
            transitions=transitions,
            triggers=triggers,
            table=self.table.tag_data(exclude=exclude_fields) if self.table else None,
            fields=fields,
            notify=list(self.notify.values_list("id", flat=True)),
            engine_version=DEFAULT_ENGINE_VERSION,
            revoke_config=self.revoke_config,
            is_auto_approve=self.is_auto_approve,
            extras=self.extras,
        )
        return data

    @transaction.atomic
    def create_version(self, operator="", message="version created.", name=None):
        """创建新的流程版本"""

        data = self.tag_data(operator, message)

        # 从外部指定流程版本名称
        if name:
            data.update(name=name)

        notify = data.pop("notify", [])
        version = WorkflowVersion.objects.create(**data)
        version.tag_task()
        version.notify.set(notify)
        version.save()

        # 创建触发器的版本信息
        copy_triggers_by_source(
            src_source_type="workflow",
            src_source_id=self.id,
            dst_source_type=SOURCE_TICKET,
            dst_source_id=version.id,
        )

        return version

    def clear_orphan_states(self):
        """根据流转关系清理孤儿状态"""

        connected_states = set()
        for trans in self.transitions.all():
            connected_states.add(trans.from_state_id)
            connected_states.add(trans.to_state_id)

        orphan_states = self.states.exclude(pk__in=connected_states)
        deleted_states = orphan_states.values_list("pk", flat=True)
        orphan_states.delete()

        return deleted_states

    def dotted_property(self, name):
        """
        '' -> ''
        ',aaa,bbb,ccc', -> 'aaa,bbb,ccc'
        """
        return ",".join(list_by_separator(getattr(self, name, "")))

    def update_biz_field(self):
        """更新关联业务字段"""

        # 兼容不关联业务流程转关联业务流程

        try:
            biz_field = self.fields.get(key=FIELD_BIZ)
        except Field.DoesNotExist:
            api_instance = RemoteApiInstance.create_default_api_instance(
                func_name="search_business",
                req_params={},
                req_body={"fields": ["bk_biz_id", "bk_biz_name"]},
                rsp_data="data.info",
            )

            biz_field = Field.objects.create(
                **{
                    "key": FIELD_BIZ,
                    "name": "关联业务",
                    "type": "SELECT",
                    "source_type": "API",
                    "choice": [],
                    "display": True,
                    "related_fields": {},
                    "desc": "请选择关联业务",
                    "is_builtin": True,
                    "is_readonly": False,
                    "is_valid": True,
                    "regex": "EMPTY",
                    "api_instance_id": api_instance.id,
                    "kv_relation": {"name": "bk_biz_name", "key": "bk_biz_id"},
                    "workflow_id": self.id,
                    "state_id": self.first_state.id,
                }
            )

        if self.is_biz_needed:
            self.first_state.append_to_fields(biz_field.id, index=1)
        else:
            self.first_state.remove_fields(biz_field.id)
            RemoteApiInstance.objects.filter(id=biz_field.api_instance_id).delete()
            biz_field.hard_delete()

    @property
    def first_state(self):
        """获取初始状态：这里指<提单>"""
        return self.states.get(type="NORMAL", is_builtin=True)

    @property
    def start_state(self):
        """获取开始状态"""
        return self.states.get(type="START")

    @property
    def end_state(self):
        """获取开始状态"""
        return self.states.get(type="END")

    @classmethod
    @transaction.atomic
    def restore_tag(cls, data, operator="system"):
        """WorkflowVersion->Workflow's record"""

        workflow, _, _ = cls.objects.restore(data, operator)
        return workflow

    @property
    def public_table_fields(self):
        """
        流程公共字段
        :return:
        """
        if self.table:
            query_set = self.table.fields.all()
            return query_set if self.is_biz_needed else query_set.exclude(key=FIELD_BIZ)
        return None

    @property
    def variables(self):
        """
        流程的全局变量
        :return:
        """

        field_variables = [
            {
                "key": _field.key,
                "name": "{}({})".format(_field.name, _("基础模型")),
                "type": _field.type,
                "source": "TABLE",
                "source_type": _field.source_type,
                "source_uri": _field.source_uri,
                "choice": _field.choice,
                "kv_relation": _field.kv_relation,
                "api_instance_id": _field.api_instance_id,
                "meta": _field.meta,
            }
            for _field in self.public_table_fields
        ]

        field_keys = [item["key"] for item in field_variables]

        field_variables.extend(
            [
                {
                    "key": _field.key,
                    "name": "{}({})".format(_field.name, _field.state.name),
                    "type": _field.type,
                    "source": _field.source,
                    "source_type": _field.source_type,
                    "source_uri": _field.source_uri,
                    "choice": _field.choice,
                    "kv_relation": _field.kv_relation,
                    "api_instance_id": _field.api_instance_id,
                }
                for _field in self.fields.filter(is_deleted=False)
                if _field.key not in field_keys
            ]
        )

        global_variables = [
            {"key": v.key, "name": v.name, "type": v.type, "source": "global_variable"}
            for v in GlobalVariable.objects.filter(is_deleted=False, flow_id=self.id)
        ]

        return field_variables + global_variables + TICKET_GLOBAL_VARIABLES

    def update_first_state_process_config(self, processors_type, processors):
        state = self.first_state
        state.processors_type = processors_type
        state.processors = processors
        state.save()

    def flush_relate_owners(self):
        """刷新流程周边负责人，只增不减
        Workflow---m--->WorkflowVersions--1-->Services.owners
                     |->State(API)--1-->RemoteApi.owners
                     |->State(Roles)--1-->UserRole.owners
                     |->Field(API)--1-->RemoteApi.owners
                     |->Field(DataSource)--1-->SysDict.owners
        UpdateOwnerMixin: a->owners (add if not exist)
        """
        pass

    @transaction.atomic
    def create_task(self, task_config):
        TaskConfig.objects.filter(workflow_id=self.id, workflow_type=FLOW).delete()
        task_objs = []
        for task_info in task_config:
            obj = TaskConfig(
                workflow_id=self.id,
                workflow_type=FLOW,
                task_schema_id=task_info["task_schema_id"],
                create_task_state=task_info["create_task_state"],
                execute_task_state=task_info["execute_task_state"],
                execute_can_create=task_info["execute_can_create"],
                need_task_finished=task_info["need_task_finished"],
            )
            task_objs.append(obj)
        TaskConfig.objects.bulk_create(task_objs)

    def can_bind_sla(self):
        """判断是否满足绑定SLA的先决条件"""
        field_keys = set()
        for field_id, field_data in self.tag_data()["fields"].items():
            field_keys.add(field_data["key"])

        # 挂载SLA流程的字段 需包括紧急程度、影响范围、优先级
        required_field = {"urgency", "impact", "priority"}
        missing_field = required_field - field_keys
        if missing_field:
            field_desc = [REQUIRED_FIELD[field] for field in missing_field]
            raise ValidationError(
                _("检测到您的流程已经发生改变，现流程版本中缺少【{}】信息，请补充完整后重新配置sla").format(
                    ",".join(field_desc)
                )
            )

    def get_notifiy_objs(self, notify_list):
        """
        根据notify通知查询相关notify对象
        """
        notifies = []
        for item in notify_list:
            notifies.append(Notify.objects.filter(type=item["type"]).first())
        return notifies

    def update_workflow_configs(self, workflow_config):
        self.is_revocable = workflow_config["is_revocable"]
        self.revoke_config = workflow_config["revoke_config"]
        self.notify.set(self.get_notifiy_objs(workflow_config["notify"]))
        self.notify_freq = workflow_config.get("notify_freq", EMPTY_INT)
        self.notify_rule = workflow_config.get("notify_rule", "NONE")
        self.is_supervise_needed = workflow_config["is_supervise_needed"]
        self.supervise_type = workflow_config["supervise_type"]
        self.supervisor = workflow_config["supervisor"]
        self.is_auto_approve = workflow_config["is_auto_approve"]
        if "extras" in workflow_config:
            self.extras = workflow_config["extras"]
            if "task_settings" in workflow_config.get("extras", {}):
                self.create_task(workflow_config["extras"]["task_settings"])
        self.save()


class WorkflowVersion(WorkflowBase):
    """
    流程版本管理：当Workflow的版本号发生变化时，自动创建一个新的版本

    PIPELINE: 对应到PIPELINE的流程模板
    """

    workflow_id = models.IntegerField(_("流程模板ID"))

    fields = jsonfield.JSONField(_("字段快照字典"), default=EMPTY_DICT, null=True, blank=True)
    states = jsonfield.JSONField(_("状态快照字典"), default=EMPTY_DICT, null=True, blank=True)
    transitions = jsonfield.JSONField(
        _("流转快照字典"), default=EMPTY_DICT, null=True, blank=True
    )
    triggers = jsonfield.JSONField(
        _("触发器快照字典"), default=EMPTY_DICT, null=True, blank=True
    )
    table = jsonfield.JSONField(
        _("基础模型快照字典"), default=EMPTY_DICT, null=True, blank=True
    )
    version_message = models.TextField(
        _("版本信息"), default=EMPTY_STRING, null=True, blank=True
    )

    pipeline_data = jsonfield.JSONField(
        _("pipeline描述数据"), default=EMPTY_DICT, null=True, blank=True
    )

    objects = managers.WorkflowVersionManager()

    auth_resource = {"resource_type": "flow_version", "resource_type_name": "流程版本"}
    resource_operations = ["flow_version_manage", "flow_version_restore"]

    class Meta:
        app_label = "workflow"
        verbose_name = _("流程快照")
        verbose_name_plural = _("流程快照")

    def __unicode__(self):
        return "{}({})".format(self.name, str(self.workflow_id))

    def post_states(self, from_id):
        all_path = self.flow_path()
        state_id_list = []
        for path in all_path:
            if from_id in path:
                from_id_index = path.index(from_id)
                state_id_list.extend(path[from_id_index + 1 :])
        state_list = []
        common_type = [
            NORMAL_STATE,
            SIGN_STATE,
            APPROVAL_STATE,
            TASK_STATE,
            TASK_SOPS_STATE,
        ]
        for state_id in set(state_id_list):
            state_info = self.states[str(state_id)]
            if state_info["type"] in common_type:
                state_list.append(state_info)
        return state_list

    def flow_path(self):
        start = 0
        end = 0
        for state in self.states.values():
            if state["type"] == "START":
                start = state["id"]
            if state["type"] == "END":
                end = state["id"]

        all_path = []

        def get_path(begin, last, path=None):
            if path is None:
                path = []
            if begin == last:
                all_path.append(path[:])
                return
            for line in self.transitions.values():
                if line["from_state"] == begin:
                    if line["to_state"] in path:
                        continue
                    path.append(line["to_state"])
                    get_path(line["to_state"], last, path)
                    path.pop()

        get_path(start, end)
        return all_path

    @property
    def service_cnt(self):
        return self.services.count()

    @property
    def graphviz(self):
        """获取工作流图"""
        nodes = {
            sid: {"id": sid, "name": "{}({})".format(s["name"], sid), "type": s["type"]}
            for sid, s in six.iteritems(self.states)
        }
        edges = [
            [t["from_state"], t["to_state"], "{}({})".format(t["name"], tid)]
            for tid, t in six.iteritems(self.transitions)
        ]

        return {"nodes": nodes, "edges": edges}

    @property
    def start_state(self):
        """获取开始节点"""
        return self._get_state_by_type("START")

    @property
    def end_state(self):
        """获取结束节点"""
        return self._get_state_by_type("END")

    @property
    def first_state(self):
        """获取初始节点"""

        first_transition = self.get_first_transition()
        return self.states[str(first_transition["to_state"])]

    @transaction.atomic
    def tag_task(self):
        task_config = TaskConfig.objects.filter(
            workflow_id=self.workflow_id, workflow_type=FLOW
        ).values()
        version_config = []

        task_schema_map = {}
        for task in task_config:
            task_schema_id = task["task_schema_id"]
            if task_schema_id not in task_schema_map:
                task_schema_map[task_schema_id] = TaskSchema.objects.clone(
                    [task_schema_id], can_edit=False
                )[0]

        for task_info in task_config:
            task_info.pop("id")
            task_info["workflow_id"] = self.id
            task_info["workflow_type"] = VERSION
            new_schema_id = task_schema_map.get(task_info["task_schema_id"])
            task_info["task_schema_id"] = new_schema_id
            version_config.append(TaskConfig(**task_info))
        TaskConfig.objects.bulk_create(version_config)

    def create_task(self, task_config):
        TaskConfig.objects.filter(workflow_id=self.id, workflow_type=VERSION).delete()
        task_objs = []
        for task_info in task_config:
            obj = TaskConfig(
                workflow_id=self.id,
                workflow_type=VERSION,
                task_schema_id=task_info["task_schema_id"],
                create_task_state=task_info["create_task_state"],
                execute_task_state=task_info["execute_task_state"],
                execute_can_create=task_info["execute_can_create"],
                need_task_finished=task_info["need_task_finished"],
            )
            task_objs.append(obj)
        TaskConfig.objects.bulk_create(task_objs)

    def get_execute_by_create(self, state_id, task_schema_id):
        task_config = TaskConfig.objects.filter(
            workflow_id=self.id,
            workflow_type=VERSION,
            create_task_state=state_id,
            task_schema_id=task_schema_id,
        )
        if task_config:
            return task_config[0].execute_task_state
        return state_id

    def task_schema_ids(self, state_id):
        task_config = TaskConfig.objects.filter(
            Q(workflow_id=self.id, workflow_type=VERSION)
            & Q(
                Q(create_task_state=state_id)
                | Q(execute_task_state=state_id, execute_can_create=True)
            )
        )
        return task_config.values_list("task_schema_id", flat=True)

    @property
    def transitions_hash(self):
        return {
            "{from_state}_{to_state}".format(**t): tid
            for tid, t in six.iteritems(self.transitions)
        }

    def graph_matrix(self, scopes=None):
        """流程图矩阵描述
        scopes: 有效矩阵顶点列表，用于截取流程图的局部矩阵
        {
            'A': set(['B', 'C']),
            'B': set(['A', 'D', 'E']),
            'C': set(['A', 'F']),
            'D': set(['B']),
            'E': set(['B', 'F']),
            'F': set(['C', 'E'])
        }
        """

        matrix = {}
        for sid, s in six.iteritems(self.states):
            ssid = str(sid)
            transitions_from = self.get_transitions_from(ssid)

            # 根据指定范围过滤流程矩阵
            if scopes:
                if str(ssid) not in scopes:
                    continue
                to_states = {
                    str(t["to_state"])
                    for t in transitions_from
                    if str(t["to_state"]) in scopes
                }
            else:
                to_states = {str(t["to_state"]) for t in transitions_from}

            matrix[ssid] = to_states

        return matrix

    def get_state_fields(self, state_id):
        """获取某个state下的字段信息"""

        state = self.get_state(state_id)
        all_fields = map(lambda field_id: self.get_field(field_id), state["fields"])

        return list(filter(lambda f: f["is_valid"], all_fields))

    def get_first_state_fields(self):
        return self.get_state_fields(self.first_state["id"])

    def get_state(self, state_id):
        """根据ID获取节点"""
        return self.states.get(str(state_id))

    def _get_state_by_type(self, type_name, return_first=True):
        """根据类型获取节点"""

        states = []
        for state_id, state in list(self.states.items()):
            if state["type"] == type_name:
                if return_first:
                    return state
                else:
                    states.append(state)

        return states

    def get_transition(self, transition_id):
        """根据ID获取连线"""
        return self.transitions.get(str(transition_id))

    def get_field(self, field_id):
        """根据ID获取字段"""
        return self.fields.get(str(field_id))

    def transition_to_state(self, transition_id):
        """根据transition获取两侧的状态"""
        return self.transitions.get(str(transition_id)).get("to_state")

    def get_first_transition(self):
        """获取start之后的第一个状态流转信息"""

        for transition_id, transition in six.iteritems(self.transitions):
            from_state_id = str(transition["from_state"])
            if self.states[from_state_id]["type"] == "START":
                return transition
        return None

    def get_transitions_from(self, from_state_id=None):
        """根据起始state查询transition"""

        # 起始状态为空
        if not from_state_id:
            return list(self.transitions.values())

        transitions_from = []
        for trans_id, trans in six.iteritems(self.transitions):
            if trans["from_state"] == int(from_state_id):
                transitions_from.append(trans)

        return transitions_from

    def get_transition_path(self, from_state_id, to_state_id):
        """
        根据起始节点，查找流转经过的所有节点和线条
        :param from_state_id: 起始节点id
        :param to_state_id: 目标节点id
        :return: 示例 {"states": [6, 9, 8], "lines": [7, 6]}
        """
        matrix = self.graph_matrix()
        # 找到图graph中start->goal中的所有路径
        paths = dfs_paths(
            matrix, str(from_state_id), str(to_state_id), skip_circle=True
        )

        transitions = set()
        states = set()
        for path in paths:
            for i in range(len(path) - 1):
                trans_id = self.transitions_hash.get(
                    "{}_{}".format(path[i], path[i + 1])
                )
                transitions.add(trans_id)
                states.add(path[i])
            # 补充最后一个节点id
            states.add(path[-1])

        return {
            "states": [int(s) for s in states],
            "lines": [int(t) for t in transitions],
        }

        # ========================= old workflow ====================================

    def get_old_w_first_transition(self):
        """获取start之后的第一个状态流转信息"""

        for transition_id, transition in six.iteritems(self.transitions):
            from_state_id = str(transition["from_state_id"])
            if self.states[from_state_id]["type"] == "START":
                return transition
        return None

    def old_flow_first_state_id(self):
        """获取初始节点"""

        first_transition = self.get_old_w_first_transition()
        return self.states[str(first_transition["to_state_id"])]["id"]

    def can_bind_sla(self):
        """判断是否满足绑定SLA的先决条件"""
        field_keys = set()
        for field_id, field_data in self.fields.items():
            field_keys.add(field_data["key"])

        # 挂载SLA流程的字段 需包括紧急程度、影响范围、优先级
        required_field = {"urgency", "impact", "priority"}
        missing_field = required_field - field_keys
        if missing_field:
            field_desc = [REQUIRED_FIELD[field] for field in missing_field]
            raise ValidationError(
                _("流程版本中缺少【{}】信息，请补充完整后再进行服务协议的关联").format(",".join(field_desc))
            )
