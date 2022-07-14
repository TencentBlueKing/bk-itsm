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

import json
from itertools import chain

import jsonfield
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    DEFAULT_STRING,
    DISTRIBUTE_TYPE_CHOICES,
    EMPTY_DICT,
    EMPTY_INT,
    EMPTY_LIST,
    EMPTY_STRING,
    EMPTY_VARIABLE,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_XXX_LONG,
    NORMAL_STATE,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    STATE_TYPE_CHOICES,
    SUPPORTED_TYPE,
    TABLE,
    SIGN_STATE,
    APPROVAL_STATE,
    TASK_STATE,
    TASK_SOPS_STATE,
)
from itsm.component.utils.basic import create_version_number, get_random_key
from itsm.postman.models import RemoteApiInstance
from itsm.workflow import managers

from .base import Model
from .common import GlobalVariable
from .field import Field
from .transition import Transition


class State(Model):
    """状态
     variables:
         {
               "inputs":[],
               "outputs":[{"key": "xxx", "rsp_data": "data.info"},
               {"key": "ssss", "rsp_data": "data.message"]
         }
         inputs 为输入，outputs为输出
    extras:
        extras.sops_info 标准运维模版信息
        sops_info.template_id 模版id
        sops_info.bk_biz_id:object{value_type value}   业务id
        sops_info.constants: [{}] 变量信息
        constants.item :object{key name type value_type value}

        extras.ticket_status 进入节点的单据状态
            ticket_status.type 单据状态类型: "keep": 保持, "custom": 自定义
            ticket_status.key 单据状态key
    """

    workflow = models.ForeignKey(
        "workflow.Workflow",
        help_text=_("关联流程"),
        related_name="states",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("状态名"), max_length=LEN_NORMAL)
    desc = models.CharField(
        _("状态描述"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True
    )
    type = models.CharField(
        _("状态类型"),
        max_length=LEN_SHORT,
        choices=STATE_TYPE_CHOICES,
        default=NORMAL_STATE,
    )
    tag = models.CharField(_("节点标签"), max_length=LEN_LONG, default=DEFAULT_STRING)

    # 干系人，另一种设计：用一对多外键管理
    processors_type = models.CharField(
        _("处理人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="OPEN"
    )
    processors = models.TextField(
        _("处理人列表"), default=EMPTY_STRING, null=True, blank=True
    )
    assignors_type = models.CharField(
        _("派单人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    assignors = models.TextField(
        _("派单人列表"), default=EMPTY_STRING, null=True, blank=True
    )
    can_deliver = models.BooleanField(_("能否转单"), default=False)
    delivers_type = models.CharField(
        _("转单人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    delivers = models.TextField(_("转单人列表"), default=EMPTY_STRING, null=True, blank=True)

    distribute_type = models.CharField(
        _("分配方式"),
        max_length=LEN_SHORT,
        choices=DISTRIBUTE_TYPE_CHOICES,
        default="PROCESS",
    )

    notify = models.ManyToManyField("workflow.Notify", help_text=_("可关联多种通知方式"))
    notify_rule = models.CharField(
        _("通知规则"), max_length=LEN_SHORT, choices=NOTIFY_RULE_CHOICES, default="NONE"
    )
    notify_freq = models.IntegerField(_("重试间隔(s)"), default=EMPTY_INT)

    # [1,3,2,4,5]
    fields = jsonfield.JSONField(
        _("表单字段(ID列表，按顺序排列)"), default=EMPTY_LIST, null=True, blank=True
    )
    read_only_fields = jsonfield.JSONField(
        _("只读表单字段(ID列表，按顺序排列)"), default=EMPTY_LIST, null=True, blank=True
    )

    is_draft = models.BooleanField(_("是否为草稿"), default=True)
    is_terminable = models.BooleanField(_("是否可以终止"), default=False)
    is_builtin = models.BooleanField(_("是否为系统内置"), default=False)

    # 是否允许在单据处理人为空时跳过
    is_allow_skip = models.BooleanField(_("是否允许在单据处理人为空时跳过"), default=False)

    # 会签及任务控制
    is_sequential = models.BooleanField(_("是否是串行任务"), default=False)
    finish_condition = jsonfield.JSONField(_("可向下调度的条件"), default=EMPTY_DICT)

    variables = jsonfield.JSONField(_("变量"), default=EMPTY_VARIABLE, null=True)
    axis = jsonfield.JSONCharField(_("节点的坐标轴"), max_length=128, default=EMPTY_DICT)
    api_instance_id = models.IntegerField(
        _("api实例主键"), default=0, null=True, blank=True
    )
    extras = jsonfield.JSONCharField(
        _("额外信息"), max_length=LEN_XXX_LONG, default=EMPTY_DICT, null=True, blank=True
    )

    # deprecated fields
    followers_type = models.CharField(
        _("关注人类型"), max_length=LEN_SHORT, choices=PROCESSOR_CHOICES, default="EMPTY"
    )
    followers = models.CharField(
        _("关注人列表"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )

    label = models.CharField(_("标签记录"), max_length=LEN_LONG, default="EMPTY")

    # 审批节点是否多签
    is_multi = models.BooleanField(_("是否多签"), default=False)

    objects = managers.StateManager()

    class Meta:
        app_label = "workflow"
        verbose_name = _("状态")
        verbose_name_plural = _("状态")

    def __unicode__(self):
        return "{}:{}".format(self.name, self.type)

    def delete(self, using=None):
        """删除状态的同时，删除所有关联的流转关系"""
        super(State, self).delete(using)

    @property
    def key(self):
        return self.id

    @property
    def is_one_out(self):
        return self.transitions_from.count() == 1

    @property
    def api_instance(self):
        try:
            return RemoteApiInstance.objects.get(id=self.api_instance_id)
        except RemoteApiInstance.DoesNotExist:
            return None

    def get_related_fields(self):
        related_fields = []
        for key in self.workflow.fields.all().values_list("key", flat=True):
            if "${params_%s}" % key in json.dumps(self.api_info):
                related_fields.append(key)
        return related_fields

    @property
    def is_end(self):
        """是否为结束节点"""
        return self.type == "END"

    @property
    def is_first_state(self):
        """是否为提单节点"""
        return self.type == "NORMAL" and self.is_builtin

    @property
    def serialized_data(self):
        from itsm.workflow.serializers import StateSerializer

        return StateSerializer(self).data

    def append_to_fields(self, field_id, index=None):
        """追加字段到fields
        index: 指定位置，则插入到指定位置，为None的时候，直接追加到最后

        """
        if field_id not in self.fields:
            if index is None:
                self.fields.append(field_id)
            else:
                self.fields.insert(index, field_id)
            self.save()

    def append_to_read_only_fields(self, field_id, index=None):
        """read_only_fields
        index: 指定位置，则插入到指定位置，为None的时候，直接追加到最后

        """
        if field_id not in self.read_only_fields:
            if index is None:
                self.read_only_fields.append(field_id)
            else:
                self.read_only_fields.insert(index, field_id)
            self.save()

    def remove_fields(self, field_id):
        """移除字段"""
        if field_id not in self.fields:
            return
        self.fields.remove(field_id)
        self.save()

    def clear_transitions(self):
        """删除关联关系"""
        Transition.objects.filter(Q(from_state=self) | Q(to_state=self)).delete()

    def get_valid_inputs_states(self, exclude_states=None, need_loop=True):
        if exclude_states is None:
            exclude_states = []
        searched_states = []
        post_states = []

        def search_forward_routers(state):
            # 找出所有的路由，打回类的直接忽略
            sub_routers = []
            for t in Transition.objects.select_related("from_state").filter(
                to_state_id=state.id
            ):
                sub_router = []
                if (
                    t.from_state in searched_states
                    and state in searched_states
                    and not need_loop
                ):
                    # 起始点都在的线条，表示存在贿赂
                    post_states.append(state)
                    break
                if t.from_state not in searched_states:
                    searched_states.append(t.from_state)
                    sub_router = search_forward_routers(t.from_state)
                if sub_router is None:
                    continue
                sub_routers.append(sub_router)
            for sub_router in sub_routers:
                sub_router.append(state)
            return sub_routers

        def flat_routers(sub_router):
            # 将所有的有效节点平铺展开
            flat_router = []
            for r in sub_router:
                if isinstance(r, list):
                    flat_router.extend(flat_routers(r))
                else:
                    flat_router.append(r)
            return flat_router

        # 第一步， 获取所有的有效路径
        searched_states.append(self)
        routers = search_forward_routers(self)
        all_flat_routers = []
        for router in routers:
            # 平铺所有的路径
            router_flat = flat_routers(router)
            if router_flat.count(self) >= 1:
                all_flat_routers.extend(router_flat)
        return [item for item in set(all_flat_routers) if item.id not in exclude_states]

    def get_post_states(self, contain_auto="false", exclude_states=None):
        if exclude_states is None:
            exclude_states = []
        pre_states = self.get_valid_inputs_states(need_loop=False)
        exclude_states.extend([item.id for item in pre_states])
        filter_type = [NORMAL_STATE, SIGN_STATE, APPROVAL_STATE]
        if contain_auto == "true":
            filter_type.extend([TASK_STATE, TASK_SOPS_STATE])
        allow_create_task_states = self.workflow.states.filter(type__in=filter_type)
        post_states = allow_create_task_states.exclude(id__in=exclude_states).exclude(
            is_builtin=True
        )
        return post_states

    def get_valid_inputs(
        self, exclude_self=False, resource_type="both", scope="transition"
    ):
        """
        获取有效的输入参数
        :param exclude_self: 是否排除当前节点的字段变量
        :param resource_type: 变量类型，global|field|both
        :param scope: 当前作用域, transition|state
        :return: valid_inputs有效的参数列表
        """

        from itsm.workflow.serializers import (
            GlobalVariableSerializer,
            FieldVariablesSerializer,
        )

        exclude_states = [self.id] if exclude_self else []
        valid_states = self.get_valid_inputs_states(exclude_states)

        # 节点未设置任何连线时, 获取valid_states为空列表, 所以需要把self添加进去
        if not exclude_self and self not in valid_states:
            valid_states.append(self)

        valid_inputs = []
        if resource_type in ["both", "field"]:
            # 会签节点的字段属于单个任务, 不允许暴露到线条上配置
            scope_exclude_state_map = {
                "transition": [SIGN_STATE, APPROVAL_STATE],
                "state": [],
            }
            valid_fields = [
                state.fields
                for state in valid_states
                if state.type not in scope_exclude_state_map.get(scope, [])
            ]
            valid_fields = set(list(chain(*valid_fields)))

            field_queryset = Field.objects.filter(
                id__in=valid_fields, type__in=SUPPORTED_TYPE, workflow=self.workflow
            ).exclude(source="TABLE")
            valid_inputs.extend(
                FieldVariablesSerializer(field_queryset, many=True).data
            )
            valid_inputs.extend(
                FieldVariablesSerializer(
                    self.workflow.public_table_fields, many=True
                ).data
            )

        if resource_type in ["both", "global"]:
            valid_state_ids = [s.id for s in valid_states]
            global_variables_queryset = GlobalVariable.objects.filter(
                state_id__in=valid_state_ids, is_valid=True
            )
            valid_inputs.extend(
                GlobalVariableSerializer(global_variables_queryset, many=True).data
            )

        return valid_inputs

    def variable_group(self, variable_data):
        variable_dict = {}
        for item in variable_data:
            if item.get("state"):
                if item["state"] in variable_dict:
                    variable_dict[item["state"]]["fields"].append(item)
                else:
                    variable_dict.setdefault(item.get("state"), {})
                    variable_dict[item["state"]].setdefault("state_name", item["state"])
                    variable_dict[item["state"]].setdefault("fields", [])
                    variable_dict[item["state"]]["fields"].append(item)
                item.pop("state")
        return variable_dict.values()

    def get_valid_inputs_by_group(
        self, exclude_self=False, resource_type="both", scope="transition"
    ):

        from itsm.workflow.serializers import (
            GlobalVariableGroupSerializer,
            FieldVariablesGroupSerializer,
        )

        exclude_states = [self.id] if exclude_self else []
        valid_states = self.get_valid_inputs_states(exclude_states)
        # 节点未设置任何连线时, 获取valid_states为空列表, 所以需要把self添加进去
        if not exclude_self and self not in valid_states:
            valid_states.append(self)

        valid_inputs = []
        if resource_type in ["both", "field"]:
            # 会签节点的字段属于单个任务, 不允许暴露到线条上配置
            scope_exclude_state_map = {
                "transition": [SIGN_STATE, APPROVAL_STATE],
                "state": [],
            }

            valid_fields = [
                state.fields
                for state in valid_states
                if state.type not in scope_exclude_state_map.get(scope, [])
            ]
            valid_fields = set(list(chain(*valid_fields)))

            field_queryset = Field.objects.filter(
                id__in=valid_fields, type__in=SUPPORTED_TYPE, workflow=self.workflow
            )

            field_variables = FieldVariablesGroupSerializer(
                field_queryset, many=True
            ).data
            valid_inputs += field_variables

        if resource_type in ["both", "global"]:
            valid_state_ids = [s.id for s in valid_states]
            global_variables_queryset = GlobalVariable.objects.filter(
                state_id__in=valid_state_ids, is_valid=True
            )

            global_variable = GlobalVariableGroupSerializer(
                global_variables_queryset, many=True
            ).data
            valid_inputs += global_variable
        group_data = self.variable_group(valid_inputs)
        return list(group_data)

    def add_variables(
        self,
        key,
        show_type,
        source="field",
        in_or_out="outputs",
        default=None,
        **kwargs
    ):
        """
        添加变量到节点
            in_or_out: inputs/outputs，
            成功返回True，重复返回False
        """

        new_vars = self.variables.get(in_or_out) or []

        if key in [v["key"] for v in new_vars]:
            return False

        var = dict(
            {"source": source, "state": self.id, "type": show_type, "key": key},
            **kwargs
        )

        # 设置默认值，仅用于流程迁移时为执行过的节点保存变量值
        if default is not None:
            var.update(default=default)

        new_vars.append(var)

        self.variables.update({in_or_out: new_vars})
        self.save()

    def add_fields_from_table(self, fields):
        """增加公共字段到节点"""

        with transaction.atomic():
            for field in fields:
                field.pop("id", None)
                basic_info = dict(
                    workflow_id=self.workflow.id, source=TABLE, key=field["key"]
                )
                field.update(basic_info)
                obj, created = self.workflow.fields.get_or_create(
                    key=field["key"], state=self
                )
                if not created:
                    obj.is_readonly = field["is_readonly"]
                else:
                    for key, value in list(field.items()):
                        setattr(obj, key, value)
                obj.save()
                self.fields.append(obj.id)
                if obj.is_readonly:
                    self.read_only_fields.append(obj.id)
            self.fields = list(set(self.fields))
            self.read_only_fields = list(set(self.read_only_fields))
            self.save()

    def clone(self):
        # TODO: 代码有优化空间, 和数据库交互较多
        # 清除ID 然后通过save() 获取最新递增ID
        self.id = None
        self.save()

        version_name = create_version_number()

        def build_outputs(fields):
            outputs = []
            for f in fields:
                outputs.append(
                    {"key": f.key, "type": f.type, "source": "field", "state": self.id}
                )
            data = {"inputs": [], "outputs": outputs}
            return data

        old_fields = self.fields
        field_id_map = {}
        field_key_map = {}
        fields_obj_list = []
        for field in Field.objects.filter(id__in=old_fields):
            # key 长度 校验128，数据库225
            old_id = field.id
            old_field_key = field.key
            new_field_key = get_random_key(
                "clone_{}_{}".format(old_field_key, version_name)
            )
            obj = field.clone(new_field_key)
            fields_obj_list.append(obj)
            field_id_map[old_id] = obj.id
            field_key_map[old_field_key] = new_field_key
        new_fields = [field_id_map.get(f, f) for f in old_fields]
        self.fields = new_fields
        self.is_draft = True
        self.is_builtin = False
        self.axis.update(x=self.axis["x"] + 250)
        self.variables = build_outputs(fields_obj_list)
        self.save()
        Field.objects.filter(id__in=new_fields).update(state_id=self.id)
        self.update_field_show_conditions(new_fields, field_key_map)
        return self

    @staticmethod
    def update_field_show_conditions(new_fields, field_key_map):
        # 单节点字段数有限，这边可以不考虑批量更新
        fields = Field.objects.filter(id__in=new_fields)
        for field in fields:
            expressions = field.show_conditions.get("expressions", [])
            if expressions:
                for expression in expressions:
                    new_key = field_key_map.get(expression["key"])
                    expression["key"] = new_key if new_key else expression["key"]
                field.save()

    def auth_actions(self, username):
        """
        节点的权限完全按照流程的管理权限
        """
        return self.workflow.auth_actions(username)

    def get_approve_states(self):
        states = self.get_valid_inputs_states(need_loop=False)
        return [
            {"id": state.id, "name": state.name}
            for state in states
            if state.type in [SIGN_STATE, APPROVAL_STATE]
        ]
