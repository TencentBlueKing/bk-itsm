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

import re

import six
from django.db.models import Q
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import (
    BASE_MODEL,
    COVERAGE_STATE,
    COVERAGE_STATE_LABEL_PREFIX,
    EMPTY,
    FIELD_BIZ,
    FIELD_TITLE,
    GLOBAL_LABEL,
    LABEL_PREFIX,
    LEN_MIDDLE,
    NORMAL_STATE_LABEL_PREFIX,
    NORMAL_STATES,
    ROUTER_P_STATE,
    ROUTER_STATE_LABEL_PREFIX,
    SELECT_TYPE_CHOICES,
    SHOW_BY_CONDITION,
    TABLE,
    TASK_SOPS_STATE,
    TASK_STATE,
    TICKET_GLOBAL_VARIABLES,
    SOURCE_WORKFLOW,
    SOURCE_TASK,
    TRIGGER_SOURCE_TYPE,
    FLOW,
)
from itsm.component.constants import role
from itsm.component.dlls.component import ComponentLibrary
from itsm.component.drf.exception import ValidationError
from itsm.component.exceptions import (
    ParamError,
    TransitionError,
    WorkFlowInvalidError,
)
from itsm.component.utils.basic import list_by_separator
from itsm.component.utils.bk_bunch import bunchify
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.component.utils.misc import find_sub_string
from itsm.postman.models import RemoteApi
from itsm.role.models import RoleType
from itsm.workflow.backend import PipelineWrapper
from itsm.workflow.models import (
    Field,
    GlobalVariable,
    TemplateField,
    Transition,
    Workflow,
    TaskSchema,
    TaskConfig,
)
from itsm.trigger.models import Trigger
from pipeline.exceptions import ConvergeMatchError, ParserException, StreamValidateError
from pipeline.parser import PipelineParser


def person_validate(processors):
    """
    用户是否为蓝鲸用户的校验
    """
    processors = list_by_separator(processors)
    bk_users = get_bk_users(users=processors)
    if not set(processors).issubset(set(bk_users)):
        raise ParamError(
            _("【{}】用户不存在").format(
                ",".join(list(set(processors).difference(set(bk_users))))
            )
        )


def person_and_type_validate(processors, processors_type, is_biz_needed):
    """
    用户角色校验
    """
    if processors_type == role.CMDB and is_biz_needed is False:
        raise ParamError(_("不关联业务的流程不能选择CMDB操作角色"))
    if processors_type == role.PERSON:
        person_validate(processors)


def transition_batch_update_validate(workflow_id, transitions):
    """
    方向批量更新时流程是否正确的校验
    """
    try:
        workflow = Workflow.objects.get(id=workflow_id)
    except Workflow.DoesNotExist:
        raise ParamError(_("流程不存在"))
    read_t_ids = workflow.transitions.values_list("id", flat=True)
    t_ids = [transition.get("id") for transition in transitions]
    if not set(t_ids).issubset(read_t_ids):
        raise ParamError(_("存在线条不属于该流程，请检查"))


def related_validate(instance):
    """
    与字段关联信息的校验
    """
    field_key = instance.key
    _workflow = instance.workflow
    workflow_fields = _workflow.fields.filter(is_deleted=False)
    workflow_transitions = _workflow.transitions.filter(is_deleted=False)
    workflow_states = _workflow.states.filter(is_deleted=False)

    related_field_validate(field_key, workflow_fields)
    show_conditions_validate(field_key, workflow_fields)
    related_transitions_validate(field_key, workflow_transitions)
    related_states_validate(field_key, workflow_states)


def related_states_validate(field_key, workflow_states):
    """
    与字段有引用关系节点的校验
    """
    from itsm.workflow.serializers import StateExtrasSerializer

    filter_key = "${params_%s}" % field_key
    for task_state in workflow_states.filter(type=TASK_STATE, is_draft=False):
        # 导入的API节点会丢失API配置，跳过校验
        task_api_instance = task_state.api_instance
        if not task_api_instance:
            continue

        if (
            filter_key in task_api_instance.req_body
            or filter_key in task_api_instance.req_params
        ):
            raise ParamError(_("该字段正在被【{}】节点引用，请先取消引用").format(task_state.name))

    sops_states = StateExtrasSerializer(
        workflow_states.filter(type=TASK_SOPS_STATE, is_draft=False), many=True
    ).data
    for state in sops_states:
        keys = []
        if state["extras"]["sops_info"]["bk_biz_id"]["value_type"] == "variable":
            keys.append(state["extras"]["sops_info"]["bk_biz_id"]["value"])
        keys.extend(
            [
                constant["value"]
                for constant in state["extras"]["sops_info"]["constants"]
                if constant["value_type"] == "variable"
            ]
        )
        if field_key in keys:
            raise ParamError(_("该字段正在被【{}】节点引用，请先取消引用").format(state["name"]))


def related_transitions_validate(field_key, workflow_transitions):
    """
    与字段有引用关系线条的校验
    """
    from itsm.workflow.serializers import TransitionSerializer

    transitions = TransitionSerializer(
        [
            transition
            for transition in workflow_transitions.filter(condition_type="by_field")
            if transition.from_state.is_one_out is False
        ],
        many=True,
    ).data
    for transition in transitions:
        keys = []
        for outside_exp in transition["condition"]["expressions"]:
            for inside_exp in outside_exp["expressions"]:
                keys.append(inside_exp["key"])
        if field_key in keys:
            raise ParamError(_("该字段正作为【{}】线条的判断条件，请先取消引用").format(transition["name"]))


def show_conditions_validate(field_key, workflow_fields):
    """
    显示条件校验
    """
    from itsm.workflow.serializers import ConditionsFieldSerializer

    show_conditions = ConditionsFieldSerializer(
        workflow_fields.filter(show_type=SHOW_BY_CONDITION), many=True
    ).data
    for condition in show_conditions:
        if field_key in [
            exp["key"] for exp in condition["show_conditions"]["expressions"]
        ]:
            raise ParamError(_("该字段正作为【{}】字段的显示条件，请先取消引用").format(condition["name"]))


def related_field_validate(field_key, workflow_fields):
    """
    字段间是否引用的校验
    """
    from itsm.workflow.serializers import RelatedFieldSerializer

    related_fields = RelatedFieldSerializer(workflow_fields, many=True).data
    for field in related_fields:
        if field_key in field["related_fields"].get("rely_on", []):
            raise ParamError(_("该字段正在被【{}】字段引用，请先取消引用").format(field["name"]))


def template_fields_exists_validate(fields):
    """基础模型字段校验"""

    if not fields:
        raise ParamError(_("请选择字段"))
    template_fields = list(
        TemplateField.objects.filter(id__in=fields).values_list("id", flat=True)
    )
    if set(fields).difference(template_fields):
        raise ParamError(
            _("{}公共字段不存在，请联系管理员").format(list(set(fields).difference(template_fields)))
        )


def table_remove_fiels_validate(fields, table):
    """基础模型删除字段校验"""

    template_fields_exists_validate(fields)

    table_fields = list(table.fields.values_list("id", flat=True))
    if not set(fields).issubset(table_fields):
        raise ParamError(
            _("{}公共字段不存在，请联系管理员").format(list(set(table_fields).difference(fields)))
        )


def add_fields_from_table_validate(fields, state):
    """从基础模型添加字段校验"""

    custom_fields = (
        Field.objects.filter(id__in=state.fields)
        .exclude(source__in=[TABLE, BASE_MODEL])
        .values_list("key", flat=True)
    )
    table_fields = [field["key"] for field in fields]

    if set(custom_fields).difference(table_fields) != set(custom_fields):
        raise ParamError(
            _("当前流程已存在唯一标识【{}】，请重新输入").format(
                ",".join(
                    list(
                        set(custom_fields) - set(custom_fields).difference(table_fields)
                    )
                )
            )
        )


def state_exists_validate(from_state_id, to_state_id):
    """SLA起始节点必传校验"""

    if not (from_state_id and to_state_id):
        raise ParamError(_("当前SLA任务缺少开始节点或者结束节点，请重新选择"))


class WorkflowPipelineValidator(object):
    def __init__(self, instance):
        self.instance = instance
        self.states_map = {}

    def __call__(self, if_deploy=False):
        if if_deploy:
            # 如果需要部署，则需要进行触发器和任务配置的有效性校验
            self.trigger_validate(self.instance)
            self.task_validate()

        # step 1 节点是否有效
        self.state_validate()

        # step 2 配置字段条件校验是否生效
        self.field_condition_validate()

        # step 3：是否可以组装为pipeline_tree
        self.pipeline_validate()

    @staticmethod
    def trigger_validate(source_instance, source_type=SOURCE_WORKFLOW):
        """
        触发器是否有效的校验
        """
        source_type_dict = dict(TRIGGER_SOURCE_TYPE)
        draft_triggers = Trigger.objects.filter(
            source_id=source_instance.id, source_type=source_type, is_draft=True
        ).values_list("name", flat=True)
        if draft_triggers and source_type == SOURCE_WORKFLOW:
            raise WorkFlowInvalidError(
                [],
                _("{source_type}【{source_name}】内的触发器【{trigger_name}】为草稿状态，无法部署").format(
                    source_type=source_type_dict.get(source_type),
                    source_name=source_instance.name,
                    trigger_name=",".join(draft_triggers),
                ),
            )

    def task_validate(self):
        task_schema_ids = []
        task_config = TaskConfig.objects.filter(
            workflow_id=self.instance.id, workflow_type=FLOW
        )
        for task_info in task_config:
            if task_info.task_schema_id not in task_schema_ids:
                task_schema_ids.append(task_info.task_schema_id)
        if not task_schema_ids:
            return

        draft_tasks = TaskSchema.objects.filter(
            id__in=task_schema_ids, is_draft=True
        ).values_list("name", flat=True)
        if draft_tasks:
            raise WorkFlowInvalidError(
                [], _("流程内引用的任务模版【%s】为草稿状态，无法部署") % ",".join(draft_tasks)
            )

        for task in TaskSchema.objects.filter(id__in=task_schema_ids):
            self.trigger_validate(task, SOURCE_TASK)

    def state_validate(self):
        invalid_state_ids = list(
            self.instance.states.filter(
                is_draft=True, is_deleted=False, type__in=NORMAL_STATES
            ).values_list("id", flat=True)
        )

        if invalid_state_ids:
            raise WorkFlowInvalidError(invalid_state_ids, _("流程内任务信息没有配置"))

    def field_condition_validate(self):
        # 字段条件校验

        error_messages = []
        all_field_keys = list(self.instance.fields.all().values_list("key", flat=True))
        all_field_keys.extend([gv["key"] for gv in TICKET_GLOBAL_VARIABLES])
        all_field_keys.extend(
            self.instance.table.fields.all().values_list("key", flat=True)
        )
        all_field_keys.extend(
            GlobalVariable.objects.filter(flow_id=self.instance.id).values_list(
                "key", flat=True
            )
        )

        field_variables = self.get_condition_related_fields()
        for item in field_variables:
            item["diff"] = ",".join(set(item["fields"]).difference(set(all_field_keys)))
            if item["diff"]:
                error_messages.append(
                    _("{obj_type}【{name}】使用了未定义的字段【{diff}】").format(**item)
                )

        if error_messages:
            raise WorkFlowInvalidError([], ", ".join(error_messages))

    def get_condition_related_fields(self):
        def flat_condition(expressions):
            flat_expressions = []
            if isinstance(expressions, list):
                for _expr in expressions:
                    flat_expressions.extend(flat_condition(_expr))

            if "expressions" in expressions:
                flat_expressions.extend(flat_condition(expressions["expressions"]))

            if "key" in expressions and expressions["key"] != "G_INT_1":
                flat_expressions.append(expressions["key"])
            return flat_expressions

        conditions = [
            {"condition": item.condition, "name": item.name, "obj_type": "线条"}
            for item in self.instance.transitions.all()
            if item.condition_type == "by_field"
        ]
        conditions.extend(
            [
                {"condition": item.show_conditions, "name": item.name, "obj_type": "字段"}
                for item in self.instance.fields.all()
                if item.show_conditions
            ]
        )

        used_fields_info = []

        for _condition in conditions:
            obj_info = {
                "name": _condition["name"],
                "obj_type": _condition["obj_type"],
                "fields": flat_condition(_condition["condition"]),
            }

            used_fields_info.append(obj_info)
        return used_fields_info

    def pipeline_validate(self):
        try:
            workflow_data = bunchify(self.instance.tag_data())
            pipeline_wrapper = PipelineWrapper(workflow_data)
            pipeline_data = pipeline_wrapper.build_tree("validator", use_cache=False)

            # 通过pipeline的status_id获取到workflow的state_id
            for k, v in list(pipeline_data["states_map"].items()):
                self.states_map.update(**{v: k})

            # 通过pipeline的exclusive_gateway_id获取workflow的来源state_id
            for k, v in list(pipeline_data["exclusive_gateway_source_state"].items()):
                self.states_map.update(**{v: k})

            # 流程引擎解析校验
            PipelineParser(pipeline_data["pipeline_tree"], cycle_tolerate=True).parse(
                root_pipeline_data={"ticket_id": "validator"}
            )
        except WorkFlowInvalidError as error:
            raise error
        except ParserException as error:
            invalid_state_ids = [
                int(self.states_map[k]) for arg in error.args for k, v in arg.items()
            ]
            raise WorkFlowInvalidError(invalid_state_ids, _("当前流程画布连线不合理，请重新确认. "))
        except ConvergeMatchError as error:
            invalid_state_ids = [int(self.states_map[error.gateway_id])]
            raise WorkFlowInvalidError(invalid_state_ids, str(error))
        except StreamValidateError as error:
            invalid_state_ids = [int(self.states_map[error.node_id])]
            raise WorkFlowInvalidError(invalid_state_ids, _("当前节点画布连线不合理，请重新确认. "))
        except Exception as error:
            logger.exception(str(error))
            raise WorkFlowInvalidError([], str(error))


class SopsStateValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        if not value["extras"]["sops_info"]["template_id"]:
            raise ParamError(_("请选择标准运维流程模板"))
        for constant in value["extras"]["sops_info"]["constants"]:
            if not constant.get("value"):
                raise ParamError(_("【{}】参数不能为空").format(constant.get("name")))


class DevSopsStateValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        if not value["extras"]["devops_info"]["project_id"]:
            raise ParamError(_("请选择蓝盾项目"))
        if not value["extras"]["devops_info"]["pipeline_id"]:
            raise ParamError(_("请选择蓝盾流水线"))
        for constant in value["extras"]["devops_info"]["constants"]:
            if not constant.get("value"):
                raise ParamError(_("【{}】参数不能为空").format(constant.get("name")))


class StateProcessorsValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        processors_type = value.get("processors_type", "")
        processors = value.get("processors", "")

        # 更新state
        if not self.instance:
            # 创建的时候不需要校验这部分信息
            return

        is_biz_needed = value.get("workflow").is_biz_needed

        if not RoleType.objects.filter(
            is_processor=True, type=processors_type
        ).exists():
            raise ParamError(_("操作角色不存在"))

        # 支持提单人角色：STARTER
        if (
            processors_type
            not in [role.OPEN, role.STARTER, role.BY_ASSIGNOR, role.STARTER_LEADER]
            and processors == ""
        ):
            raise ParamError(_("操作角色不能为空"))

        if processors_type == role.OPEN:
            if not (
                self.instance.is_first_state
                or value["distribute_type"]
                in ["DISTRIBUTE_THEN_PROCESS", "DISTRIBUTE_THEN_CLAIM"]
            ):
                raise ParamError(_("该节点操作角色不能选择不限"))

        person_and_type_validate(processors, processors_type, is_biz_needed)


class FieldValidator(object):
    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        self.key_validate(value)
        self.select_type_choice_validate(value)
        self.custom_table_validate(value)
        self.tips_validate(value)
        self.api_instance_validate(value)
        self.update_type_validate(self.instance, value)

    @staticmethod
    def tips_validate(value):
        if value.get("is_tips", False) and not value.get("tips", ""):
            raise ParamError("请填写字段展示说明")

    @staticmethod
    def api_instance_validate(value):
        if value.get("source_type") != "API":
            return

        try:
            RemoteApi.objects.get(id=value["api_info"]["remote_api_id"])
        except KeyError:
            raise ParamError(_("参数格式错误，请联系管理员"))
        except RemoteApi.DoesNotExist:
            raise ParamError(_("所选API接口不存在，请重新选择"))

    def key_validate(self, value):
        """
        key的有效性校验
        """
        self.field_key_validate(value.get("key"))
        if self.instance:
            if self.instance.key != value.get("key"):
                raise ParamError(_("字段唯一标识不能修改"))
            return

        if value.get("key") in [FIELD_TITLE]:
            raise ParamError(_("title 为内置唯一标识，请重新输入"))

        if (
            Field.objects.filter(
                workflow_id=value.get("workflow"), key=value.get("key")
            ).exists()
            or GlobalVariable.objects.filter(
                flow_id=value.get("workflow").id, key=value.get("key")
            ).exists()
        ):
            raise ParamError(_("当前流程已存在唯一标识【{}】，请重新输入").format(value.get("key")))

    @staticmethod
    def custom_table_validate(value):
        """
        自定义表格校验
        """
        if value.get("type") != "CUSTOMTABLE":
            # 非表格字段不需要校验
            return

        def single_column_validate(column):
            if not column.get("name") or not column.get("key"):
                raise ParamError(_("存在空行数据，请补全或删除"))
            if column.get("display") not in [
                "input",
                "select",
                "date",
                "datetime",
                "multiselect",
            ]:
                raise ParamError(_("表现形式不支持，请重新选择！"))
            if column["display"] == "select":
                for choice in column.get("choice", []):
                    if not choice.get("name") or not choice.get("key"):
                        raise ParamError(_("选择框数据存在空行，请检查"))

        meta = value.get("meta")
        if not meta:
            raise ParamError(_("自定义表格表头不能为空，请联系管理员！"))
        columns = meta.get("columns")
        for column in columns:
            single_column_validate(column)

    def select_type_choice_validate(self, value):
        if not (
            value.get("type") in list(SELECT_TYPE_CHOICES.keys())
            and value.get("source_type") == "CUSTOM"
        ):
            return
        choice = value.get("choice", [])
        if not choice:
            raise ParamError(
                _("【{0}】请输入自定义数据，换行分隔。").format(SELECT_TYPE_CHOICES[value.get("type")])
            )
        for field in choice:
            name = field.get("name")
            key = field.get("key")
            self.field_common_validate(name)
            self.field_key_validate(key)
        self.unique_validate(choice, "name")
        self.unique_validate(choice, "key")

    @staticmethod
    def unique_validate(choice, value):
        keys = [field[value] for field in choice]
        if len(keys) > len(set(keys)):
            raise ParamError(_("自定义数据【{}】不唯一，请重新输入").format(value))

    @staticmethod
    def field_common_validate(name):
        if not name:
            raise ParamError(_("请输入选项值"))
        if len(name) > LEN_MIDDLE:
            raise ParamError(_("自定义数据【{}】长度不能大于{}个字符").format(name, LEN_MIDDLE))

    def field_key_validate(self, key):
        """
        key有效性判断
        """
        self.field_common_validate(key)
        if not re.match("^[_a-zA-Z0-9]*$", key) or len(key) > LEN_MIDDLE:
            raise ParamError(
                _("自定义数据key值【{}】仅支持【英文、数字和下划线】，长度小于128字符，请重新输入").format(key)
            )

    @staticmethod
    def update_type_validate(instance, value):
        """
        字段更新类型的校验
        """
        if instance is None:
            return
        if instance.type != value["type"]:
            related_validate(instance)
            return
        if (
            instance.type in list(SELECT_TYPE_CHOICES.keys())
            and instance.source_type == "CUSTOM"
        ):
            if value.get("source_type") != "CUSTOM":
                # source_type发生变化了，不需要以下校验
                return

                # 字段类型没有发生变化的选择字段，不能随意修改原有数据的key
            inst_choice_keys = [item.get("key") for item in instance.choice]
            value_choice_keys = [item.get("key") for item in value.get("choice", [])]
            if not set(inst_choice_keys).issubset(value_choice_keys):
                related_validate(instance)


class TemplateFieldValidator(FieldValidator):
    def __call__(self, value):
        self.key_validate(value)
        self.name_validate(value)
        self.select_type_choice_validate(value)
        self.custom_table_validate(value)
        self.tips_validate(value)

    def key_validate(self, value):

        if not value.get("key") or not value.get("project_key"):
            return
        self.field_key_validate(value.get("key"))
        if not self.instance:
            if TemplateField.objects.filter(
                Q(key=value.get("key"))
                & Q(project_key=value.get("project_key"))
                & Q(is_deleted=False)
            ).exists():
                if value.get("key") in [FIELD_TITLE, FIELD_BIZ]:
                    raise ParamError(_("title, bk_biz_id 为内置唯一标识，请重新输入"))
                raise ParamError(_("当前项目字段库已存在唯一标识【{}】，请重新输入").format(value.get("key")))

    def name_validate(self, value):
        fields = TemplateField.objects.filter(
            Q(name=value.get("name"))
            & Q(is_deleted=False)
            & Q(project_key=value.get("project_key"))
        )
        if self.instance:
            fields = fields.exclude(id=self.instance.id)
        if fields.exists():
            raise ParamError(_("字段库已存在名称【{}】，请重新输入").format(value.get("name")))


def template_field_can_destroy(instance):
    """公共字段可删除校验"""
    tables = instance.tables.all()

    if tables:
        table_names = ",".join([table.name for table in tables])
        raise ValidationError(_("字段已被基础模型[{}]引用，无法删除".format(table_names)))


class StatePollValidator(object):
    def __call__(self, kwargs):
        api_info = kwargs.get("api_info", {})
        need_poll = api_info.get("need_poll", "")
        succeed_conditions = api_info.get("succeed_conditions", {})
        end_conditions = api_info.get("end_conditions", {})

        if not api_info.get("remote_api_id"):
            raise ParamError(_("请选择API接口"))

        if not RemoteApi.objects.filter(id=api_info.get("remote_api_id")).exists():
            raise ParamError(_("API接口不存在"))

        if not need_poll:
            return

        for expression in succeed_conditions.get("expressions", []):
            for field in expression.get("expressions", []):
                if not (field["key"] and field["condition"] and str(field["value"])):
                    raise ParamError(_("请添加完整成功条件"))
        if not end_conditions.get("poll_interval"):
            raise ParamError(_("轮询间隔必须为大于0的整数"))
        if not end_conditions.get("poll_time", ""):
            raise ParamError(_("轮询次数必须为大于0的整数"))
        if not (
            str(end_conditions.get("poll_interval", ""))
            and str(end_conditions.get("poll_time", ""))
        ):
            raise ParamError(_("请添加完整结束条件"))


class StateGlobalVariablesValidator(object):
    def __init__(self, instance):
        self.instance = instance
        self.workflow = self.instance.workflow

    def __call__(self, value):
        variables = value.get("variables", {})
        outputs = variables.get("outputs", [])
        names = [variable.get("name") for variable in outputs if variable.get("name")]

        # 节点内重名/非空校验
        if len(names) > len(set(names)):
            raise ParamError(_("全局变量名重复或存在空值，请重新输入"))

        self.related_validate(outputs)

    def related_validate(self, outputs):
        """
        和其他相关联的model校验
        """
        path_key_dict = {
            item["ref_path"]: item["key"] for item in self.instance.variables["outputs"]
        }
        refs = [output.get("ref_path") for output in outputs]
        deleted_variable = []
        for ref, key in six.iteritems(path_key_dict):
            if ref not in refs:
                deleted_variable.append(key)
        workflow_fields = self.workflow.fields.filter(is_deleted=False)
        workflow_transitions = self.workflow.transitions.filter(is_deleted=False)
        workflow_states = self.workflow.states.filter(is_deleted=False)
        for key in deleted_variable:
            related_field_validate(key, workflow_fields)
            related_transitions_validate(key, workflow_transitions)
            related_states_validate(key, workflow_states)


class TransitionValidator(object):
    def __init__(self, instance=None):
        self.instance = instance
        self.from_state = None
        self.to_state = None

    def __call__(self, value):

        self.from_state = value["from_state"]
        self.to_state = value["to_state"]
        if Transition.objects.filter(
            from_state=self.from_state, to_state=self.to_state, is_deleted=False
        ).exists():
            raise TransitionError(_("起始节点已经存在连接线."))

        # 节点连接校验
        self.state_validate()

    def state_validate(self):
        """
        原则1：其中一个label为empty的时候， 可以通过
        原则2：两个label完全相等的时候，可以通过
        原则3：前者为G，后者为并行G|P*的时候可以通过

        不满足条件的情况：两者label不想等并排除掉原则三，直接raise
        """

        if self.from_state.label == self.to_state.label:
            # label一致的节点，可以连接(同一个流程内)
            return

        if self.from_state.type == ROUTER_P_STATE:
            # 并行网关
            if self.to_state.label == EMPTY and self.to_state.type != COVERAGE_STATE:
                return
            if (
                find_sub_string(self.to_state.label, NORMAL_STATE_LABEL_PREFIX)
                == self.from_state.label
                and self.to_state.type in NORMAL_STATES
            ):
                return
            if (
                self.to_state.type == ROUTER_P_STATE
                and find_sub_string(self.to_state.label, ROUTER_STATE_LABEL_PREFIX)
                == self.from_state.label
            ):
                return
            raise TransitionError(_("并行网关连线不规范"))

        if EMPTY in [self.from_state.label, self.to_state.label]:
            # 其中一个为空，也可以连接
            if self.from_state.type in NORMAL_STATES:
                if (
                    self.to_state.type == COVERAGE_STATE
                    and self.to_state.label == EMPTY
                ):
                    if self.from_state.label.rfind(NORMAL_STATE_LABEL_PREFIX) == -1:
                        raise TransitionError(_("待连接的聚合网关与当前节点不在同一个工作区域内"))
            if (
                self.from_state.type == COVERAGE_STATE == self.to_state.type
                and find_sub_string(self.from_state.label, ROUTER_STATE_LABEL_PREFIX)
                == GLOBAL_LABEL
            ):
                raise TransitionError(_("待连接的聚合网关与当前节点不在同一个工作区域内"))
            return

        # 以下label不相等且可能多入多出的情况
        if self.from_state.type == self.to_state.type:
            if {self.from_state.type, self.to_state.type}.issubset(set(NORMAL_STATES)):
                # 普通节点label不一致，一定是不同的工作区域内的
                raise TransitionError(_("源任务和目标任务不在同一个工作区域内"))
            if self.from_state.type != COVERAGE_STATE:
                return

            from_state_pre_label = find_sub_string(
                self.from_state.label, ROUTER_STATE_LABEL_PREFIX
            )
            # 如果from 和 to 都是聚合，则from的比较值要继续往前推一个区域
            from_state_pre_label = find_sub_string(
                from_state_pre_label, NORMAL_STATE_LABEL_PREFIX
            )
            to_state_pre_label = find_sub_string(self.to_state.label, LABEL_PREFIX)

            if from_state_pre_label != to_state_pre_label:
                raise TransitionError(_("源任务和目标任务不在同一个工作区域内"))
            return

        to_state_pre_label = find_sub_string(self.to_state.label, LABEL_PREFIX)

        if self.from_state.type == COVERAGE_STATE:
            from_state_pre_label = find_sub_string(
                self.from_state.label, ROUTER_STATE_LABEL_PREFIX
            )
            if self.to_state.type == ROUTER_P_STATE:
                to_state_pre_label = find_sub_string(
                    self.to_state.label, ROUTER_STATE_LABEL_PREFIX
                )
            else:
                to_state_pre_label = self.to_state.label
        elif self.to_state.type == COVERAGE_STATE:
            from_state_pre_label = find_sub_string(
                self.from_state.label, NORMAL_STATE_LABEL_PREFIX
            )
            to_state_pre_label = find_sub_string(
                self.to_state.label, COVERAGE_STATE_LABEL_PREFIX
            )
        else:
            from_state_pre_label = self.from_state.label
        if from_state_pre_label != to_state_pre_label:
            raise TransitionError(_("源任务和目标任务不在同一个工作区域内"))


def task_schema_delete_validate(instance):
    """
    当被引用的时候，不能删除任务模板
    """
    is_exist = TaskConfig.objects.filter(
        workflow_type=FLOW, task_schema_id=instance.id
    ).exists()
    if is_exist:
        raise ValidationError(_("当前任务模板已经被流程引用，无法删除！"))


class TriggerValidator(object):
    """
    TODO：可以准备废弃了
    """

    def __init__(self, instance):
        self.instance = instance

    def __call__(self, value):
        # Throw error if component key illegal
        ComponentLibrary.get_component_class("trigger", value["component_key"])
