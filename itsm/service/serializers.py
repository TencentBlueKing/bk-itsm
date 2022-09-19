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

from django.db import transaction
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import JSONField
from rest_framework.validators import UniqueValidator
from rest_framework.fields import empty

from itsm.component.constants import (
    DISPLAY_CHOICES,
    EMPTY_LIST,
    EMPTY_STRING,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_XX_LONG,
    SERVICE_CHOICE,
    LEN_SHORT,
    DEFAULT_ENGINE_VERSION,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    OPEN,
    SERVICE_SOURCE_CHOICES,
    EMPTY_INT,
    INVISIBLE,
)
from itsm.component.drf.serializers import (
    DynamicFieldsModelSerializer,
    AuthModelSerializer,
)
from itsm.component.exceptions import ServiceCatalogValidateError, ServerError
from itsm.component.utils.basic import dotted_name, list_by_separator, normal_name
from itsm.component.utils.misc import transform_single_username
from itsm.project.models import Project
from itsm.service.models import (
    CatalogService,
    DictData,
    Favorite,
    OldSla,
    Service,
    ServiceCatalog,
    ServiceCategory,
    ServiceSla,
    SysDict,
    FavoriteService,
)
from itsm.service.validators import key_validator, name_validator, time_validator
from itsm.workflow.models import Workflow, Table
from itsm.workflow.serializers import NotifySerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化"""

    name = serializers.CharField(
        required=False, initial=EMPTY_STRING, max_length=LEN_LONG
    )
    service = serializers.CharField(required=True, max_length=LEN_NORMAL)
    data = JSONField(required=True, initial=EMPTY_LIST)

    class Meta:
        model = Favorite
        fields = ("id", "user", "service", "name", "data", "create_at")
        read_only_fields = ("id", "user", "create_at")

    def create(self, validated_data):
        """改写post方法,提供update_or_create逻辑"""

        instance, created = Favorite.objects.update_or_create(
            defaults={"data": validated_data.pop("data")},
            **{
                "user": validated_data.pop("user"),
                "service": validated_data.pop("service"),
            }
        )

        return instance


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("key", "name", "desc")

    def to_representation(self, instance):
        data = super(ServiceCategorySerializer, self).to_representation(instance)
        data.update({"desc": _(data["desc"])})
        data.update({"name": _(data["name"])})
        return data


class ServiceCatalogSerializer(serializers.ModelSerializer):
    """服务目录序列化"""

    level = serializers.IntegerField(required=False, min_value=0)
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        validators=[name_validator],
        max_length=LEN_NORMAL,
    )
    # allow_blank -> 允许字段为空字符串
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    parent__id = serializers.CharField(
        required=False, allow_blank=True, source="parent.id"
    )
    parent__name = serializers.CharField(
        required=False, allow_blank=True, source="parent.name"
    )

    parent_key = serializers.CharField(required=False, allow_blank=True)
    parent_name = serializers.CharField(required=False, allow_blank=True)
    project_key = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        该函数可用于关联字段校验，比如账号密码是否匹配，
        还可以用来自动添加一些read_only字段，比如某些key、转换某些字段等
        """

        from itsm.service.models import ServiceCatalog

        # OrderedDict([(u'parent', {u'id': u'1'}), (u'name', u'\u518d\u6765\u4e00\u904d'), (u'desc', _(u''))])

        parent_object = None

        # 剔除中间字段，若字段不存在，则返回None
        parent_key = attrs.pop("parent_key", None)
        parent = attrs.pop("parent", None)

        # 转换parent_key到parent，parent_id优先级高于parent_key
        if parent_key:
            # TODO 如何更好的获取对应的Model
            try:
                parent_object = ServiceCatalog.objects.get(key=parent_key)
            except (ServiceCatalog.DoesNotExist, ValueError):
                raise ValidationError(_("指定的父目录不存在"))

        if parent:
            try:
                parent_object = ServiceCatalog.objects.get(pk=parent.get("id"))
                # ValueError: invalid literal for int() with base 10: ''
            except (ServiceCatalog.DoesNotExist, ValueError):
                raise ValidationError(_("指定的父目录不存在"))

        # 禁止创建根目录
        if not parent_object and self.context["view"].action == "create":
            raise ServiceCatalogValidateError(_("请提供合法的父级目录"))
        # 限制目录层级为三级
        if parent_object and parent_object.level >= 3:
            raise ServiceCatalogValidateError(_("服务目录最多只支持3级"))

        # 同级下目录名不能重复
        if self.context["view"].action == "create":
            if (
                parent_object
                and parent_object.get_children()
                .filter(is_deleted=False, name=attrs["name"])
                .exists()
            ):
                raise ServiceCatalogValidateError(_("同级下目录名不能重复，请修改后提交"))
        if self.context["view"].action == "update":
            if (
                parent_object
                and parent_object.get_children()
                .filter(is_deleted=False, name=attrs["name"])
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise ServiceCatalogValidateError(_("同级下目录名不能重复，请修改后提交"))

        attrs["parent"] = parent_object

        return attrs

    class Meta:
        model = ServiceCatalog
        fields = (
            "id",
            "key",
            "level",
            "parent",
            "parent_name",
            "parent_key",
            "parent__id",
            "parent__name",
            "name",
            "desc",
            "project_key",
        )
        # 只读字段在创建和更新时均被忽略
        read_only_fields = (
            "id",
            "key",
            "parent_name",
            "parent_key",
            "parent__id",
            "parent__name",
        )


class ServiceCatalogShortcutSerializer(serializers.ModelSerializer):
    """服务目录简化序列化"""

    parent_id = serializers.CharField(
        required=False, allow_blank=True, source="parent.id"
    )
    parent_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ServiceCatalog
        fields = (
            "id",
            "key",
            "level",
            "name",
            "parent_id",
            "parent_name",
        )


class SlaSerializer(serializers.ModelSerializer):
    """服务级别序列化"""

    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称为必填项")},
        max_length=8,
        validators=[
            UniqueValidator(queryset=OldSla.objects.all(), message=_("服务级别名已存在，请重新输入")),
            name_validator,
        ],
    )
    key = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    level = serializers.ChoiceField(
        choices=OldSla.level_choices, error_messages={"invalid_choice": _("选项不合法")}
    )
    resp_time = serializers.CharField(
        required=True, error_messages={"blank": _("响应时间为必填项")}
    )
    deal_time = serializers.CharField(
        required=True, error_messages={"blank": _("处理时间为必填项")}
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    class Meta:
        model = OldSla
        fields = (
            "id",
            "key",
            "name",
            "level",
            "resp_time",
            "deal_time",
            "desc",
            "is_builtin",
        )

    def create(self, validated_data):
        validated_data["key"] = OldSla.get_unique_key(validated_data["name"])
        return super(SlaSerializer, self).create(validated_data)

    def validate_resp_time(self, value):
        """resp_time校验"""
        time_validator(value)
        return value

    def validate_deal_time(self, value):
        """deal_time校验"""
        time_validator(value)
        return value

    def to_representation(self, instance):
        data = super(SlaSerializer, self).to_representation(instance)
        data.update({"desc": _(data["desc"])})
        data.update({"name": _(data["name"])})
        return data


class ServiceSlaSerializer(serializers.ModelSerializer):
    """服务与SLA关联表序列化"""

    name = serializers.CharField(
        required=True, error_messages={"blank": _("协议名称不能为空")}, max_length=LEN_LONG
    )
    service_id = serializers.IntegerField(required=False, allow_null=True)
    lines = JSONField(required=False, initial=EMPTY_LIST)
    states = JSONField(required=False, initial=EMPTY_LIST)

    class Meta:
        model = ServiceSla
        fields = "__all__"


class ServiceSerializer(AuthModelSerializer):
    """服务序列化"""

    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=Service.objects.all(), message=_("服务名已存在，请重新输入")),
            # name_validator
        ],
    )
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )
    workflow_name = serializers.CharField(source="workflow.name", required=False)
    workflow = serializers.IntegerField(required=False, source="workflow.id")
    version_number = serializers.CharField(
        source="workflow.version_number", required=False
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    is_valid = serializers.BooleanField(required=False)
    display_type = serializers.ChoiceField(required=False, choices=DISPLAY_CHOICES)
    display_role = serializers.CharField(required=False, max_length=LEN_LONG)
    catalog_id = serializers.IntegerField(required=False)
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)
    source = serializers.ChoiceField(required=False, choices=SERVICE_SOURCE_CHOICES)
    owners = serializers.CharField(
        required=False, error_messages={"blank": _("服务负责人不能为空")}
    )
    # TODO sla开始节点结束节点交叉校验
    sla = ServiceSlaSerializer(required=False, many=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "key",
            "name",
            "desc",
            "workflow",
            "workflow_name",
            "version_number",
            "bounded_catalogs",
            "bounded_relations",
            "catalog_id",
            "is_valid",
            "display_type",
            "display_role",
            "owners",
            "can_ticket_agency",
            "sla",
            "source",
            "project_key",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS

    def __init__(self, instance=None, data=empty, **kwargs):
        super(ServiceSerializer, self).__init__(instance, data, **kwargs)
        self.favorite_service = self.get_favorite_users()

    def get_favorite_users(self):
        services = (
            [self.instance]
            if isinstance(self.instance, Service)
            else []
            if self.instance is None
            else self.instance
        )
        service_ids = [service.id for service in services]
        users = FavoriteService.objects.filter(service_id__in=service_ids).values(
            "service_id", "user"
        )
        service_user_map = {}
        for user in users:
            service_user_map.setdefault(user["service_id"], []).append(user["user"])
        return service_user_map

    @transaction.atomic
    def create(self, validated_data):
        """创建后立即绑定"""

        # 初始化一个流程
        work_flow_instance = self.init_work_flow(validated_data)

        # 创建一个新的流程版本
        version = work_flow_instance.create_version()

        validated_data["workflow"] = version
        validated_data["is_valid"] = False

        catalog_id = validated_data.pop("catalog_id", 0)
        sla_tasks = validated_data.pop("sla", [])

        instance = super(ServiceSerializer, self).create(validated_data)
        instance.bind_catalog(catalog_id, instance.project_key)
        instance.update_service_sla(sla_tasks)

        return instance

    def get_default_table_id(self):
        try:
            return Table.objects.get(name="默认", is_builtin=True).id
        except Table.DoesNotExist:
            return 1

    def init_work_flow(self, validated_data):
        work_flow_instance = Workflow.objects.create(
            name="{}_work_flow".format(validated_data["name"]),
            desc="",
            flow_type="other",
            notify_freq="0",
            is_biz_needed=False,
            is_iam_used=False,
            is_enabled=True,
            is_draft=False,
            table_id=self.get_default_table_id(),
            owners="",
            engine_version=DEFAULT_ENGINE_VERSION,
            creator=validated_data["creator"],
            updated_by=validated_data["updated_by"],
        )
        return work_flow_instance

    def update(self, instance, validated_data):
        """更新后重新绑定目录"""
        catalog_id = validated_data.pop("catalog_id", 0)
        sla_tasks = validated_data.pop("sla", [])
        with transaction.atomic():
            instance.key = validated_data["key"]
            instance.name = validated_data["name"]
            instance.desc = validated_data["desc"]
            instance.updated_by = validated_data["updated_by"]
            instance.save()
            instance.bind_catalog(catalog_id, instance.project_key)
            instance.update_service_sla(sla_tasks)

        return instance

    def to_internal_value(self, data):
        # TODO: 根据未来的校检逻辑可能会有所修改
        data = super(ServiceSerializer, self).to_internal_value(data)
        if "workflow" in data:
            data["workflow"] = data["workflow"]["id"]
        data["display_role"] = dotted_name(data.get("display_role", ""))
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])

        return data

    def to_representation(self, instance):
        data = super(ServiceSerializer, self).to_representation(instance)
        try:
            workflow_instance = Workflow.objects.get(id=instance.workflow.workflow_id)
        except Workflow.DoesNotExist:
            raise ServerError("当前服务绑定的流程已经被删除, service_name={}".format(instance.name))

        username = self.context["request"].user.username
        data["creator"] = transform_single_username(data["creator"])
        data["updated_by"] = transform_single_username(data["updated_by"])
        data["supervise_type"] = workflow_instance.supervise_type
        data["supervisor"] = workflow_instance.supervisor
        if "display_role" in data:
            data["display_role"] = ",".join(list_by_separator(data["display_role"]))
        data["first_state_id"] = workflow_instance.first_state.id
        data["workflow_id"] = instance.workflow.workflow_id
        data["is_biz_needed"] = workflow_instance.is_biz_needed
        data["notify"] = [
            {"type": notify.type, "name": notify.name}
            for notify in workflow_instance.notify.all()
        ]
        data["notify_rule"] = workflow_instance.notify_rule
        data["notify_freq"] = workflow_instance.notify_freq
        data["is_supervise_needed"] = workflow_instance.is_supervise_needed
        data["revoke_config"] = workflow_instance.revoke_config
        data["extras"] = workflow_instance.extras
        data["owners"] = ",".join(list_by_separator(data["owners"]))
        data["favorite"] = username in self.favorite_service.get(instance.id, [])
        return self.update_auth_actions(instance, data)


class ServiceListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=Service.objects.all(), message=_("服务名已存在，请重新输入")),
            # name_validator
        ],
    )
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        super(ServiceListSerializer, self).__init__(instance, data, **kwargs)
        service_ids = self.get_service_ids()
        self.favorite_service = self.get_favorite_users(service_ids)
        self.service_catalogs_map = self.get_service_catalogs(service_ids)

    def get_service_ids(self):
        """
        一次性获取所有的service.id,方便后面的查询
        return [service.id]
        """
        services = (
            [self.instance]
            if isinstance(self.instance, Service)
            else []
            if self.instance is None
            else self.instance
        )
        return [service["id"] for service in services]

    def get_service_catalogs(self, service_ids):
        """
        获取用户所有部门的catalogs
        """
        service_catalogs_map = {
            cs.service_id: [cs.catalog.name]
            for cs in CatalogService.objects.filter(service_id__in=service_ids)
        }
        return service_catalogs_map

    def get_favorite_users(self, service_ids):
        """
        获取用户最喜欢的服务
        """
        users = FavoriteService.objects.filter(service_id__in=service_ids).values(
            "service_id", "user"
        )
        service_user_map = {}
        for user in users:
            service_user_map.setdefault(user["service_id"], []).append(user["user"])
        return service_user_map

    def to_representation(self, instance):
        data = super(ServiceListSerializer, self).to_representation(instance)
        username = self.context["request"].user.username
        data["favorite"] = username in self.favorite_service.get(instance["id"], [])
        data["bounded_catalogs"] = self.service_catalogs_map.get(instance["id"], [])
        return data

    class Meta:
        model = Service
        fields = (
            "id",
            "key",
            "name",
        )


class CatalogServiceSerializer(serializers.ModelSerializer):
    """服务目录关联序列化"""

    class Meta:
        model = CatalogService
        fields = (
            "id",
            "catalog",
            "service",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS


class CatalogServiceEditSerializer(serializers.Serializer):
    """服务目录关联操作序列化"""

    catalog_id = serializers.IntegerField(min_value=1, required=True)
    services = serializers.ListField(allow_empty=False, required=True)

    def validate_services(self, value):
        """
        Check services
        """

        if not isinstance(value, list) and len(value) > 0:
            raise serializers.ValidationError(_("请选择至少一项服务"))

        if Service.objects.filter(id__in=value).count() != len(value):
            raise serializers.ValidationError(_("部分服务不存在"))

        return value

    def validate_catalog_id(self, value):
        """
        Check catalog_id
        """

        try:
            catalog = ServiceCatalog.objects.get(id=value)
            if catalog.level == 0:
                raise serializers.ValidationError(_("根目录不允许添加服务，选择其他目录"))
        except ServiceCatalog.DoesNotExist:
            raise serializers.ValidationError(_("指定的服务目录不存在"))

        return value


class DictDataSerializer(serializers.ModelSerializer):
    """数据字典数据项序列化"""

    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[key_validator],
    )
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
    )
    # validators=[name_validator])
    order = serializers.IntegerField(required=False, min_value=1)

    class Meta:
        model = DictData
        fields = (
            "id",
            "key",
            "name",
            "level",
            "order",
            "parent",
            "parent_key",
            "parent_name",
            "is_readonly",
            "is_builtin",
            "dict_table",
        )
        read_only_fields = (
            "id",
            "level",
            "is_readonly",
            "is_builtin",
            "parent_key",
            "parent_name",
        ) + model.FIELDS


class SysDictSerializer(DynamicFieldsModelSerializer):
    """数据字典序列化"""

    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=SysDict.objects.all(), message=_("编码已存在，请重新输入")),
            key_validator,
        ],
    )
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
    )
    owners = serializers.CharField(
        required=False, max_length=LEN_XX_LONG, allow_blank=True
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    class Meta:
        model = SysDict
        fields = (
            "id",
            "key",
            "name",
            "owners",
            "desc",
            "is_enabled",
            "is_readonly",
        ) + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS

    def to_internal_value(self, data):
        data = super(SysDictSerializer, self).to_internal_value(data)
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])
        return data

    def to_representation(self, instance):
        data = super(SysDictSerializer, self).to_representation(instance)
        data["name"] = _(data["name"])
        data["owners"] = normal_name(data.get("owners"))
        return data


class DictKeySerializer(serializers.Serializer):
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[key_validator],
    )
    service = serializers.ChoiceField(required=False, choices=SERVICE_CHOICE)
    view_type = serializers.ChoiceField(
        required=False, choices=["list", "tree", "sets"]
    )


class WorkFlowConfigSerializer(serializers.Serializer):
    is_revocable = serializers.BooleanField(required=True)
    revoke_config = serializers.DictField(required=True)
    notify = NotifySerializer(required=True, allow_null=True, many=True)
    notify_freq = serializers.IntegerField(required=False)  # 重试间隔
    notify_rule = serializers.ChoiceField(
        required=False, allow_blank=True, choices=NOTIFY_RULE_CHOICES
    )  # 重试规则
    extras = serializers.JSONField(required=False)
    is_supervise_needed = serializers.BooleanField(required=True)
    supervise_type = serializers.ChoiceField(required=True, choices=PROCESSOR_CHOICES)
    supervisor = serializers.CharField(
        required=True, max_length=LEN_LONG, allow_blank=True
    )
    is_auto_approve = serializers.BooleanField(required=True)


class ServiceConfigSerializer(serializers.Serializer):
    workflow_config = WorkFlowConfigSerializer(required=True)
    can_ticket_agency = serializers.BooleanField(required=True)
    display_type = serializers.ChoiceField(required=True, choices=DISPLAY_CHOICES)
    display_role = serializers.CharField(required=False, max_length=LEN_LONG)
    owners = serializers.CharField(
        required=False, error_messages={"blank": _("服务负责人不能为空")}
    )

    def validate(self, attrs):
        if attrs["display_type"] in [OPEN, INVISIBLE]:
            attrs["display_role"] = EMPTY_STRING
        else:
            if "display_role" not in attrs:
                raise ValidationError(_("display_role 为必填项"))
        return attrs


class WorkflowImportSerializer(serializers.Serializer):
    # 基础字段
    name = serializers.CharField(
        required=True,
        max_length=LEN_MIDDLE,
        error_messages={"blank": _("请输入流程名称!"), "max_length": _("流程名称长度不能大于120个字符")},
    )
    flow_type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    desc = serializers.CharField(
        required=True, max_length=LEN_LONG, min_length=1, allow_blank=True
    )
    owners = serializers.CharField(
        required=True, max_length=LEN_XX_LONG, allow_blank=True
    )
    # 基础模型
    table = serializers.DictField(required=True)
    version_number = serializers.CharField(required=True)
    version_message = serializers.CharField(required=True, allow_blank=True)
    states = serializers.DictField(required=True)
    transitions = serializers.DictField(required=True)
    triggers = serializers.ListField(required=True)
    fields = serializers.DictField(required=True)

    # 业务属性字段
    is_biz_needed = serializers.BooleanField(required=True)
    is_iam_used = serializers.BooleanField(required=True)
    is_task_needed = serializers.BooleanField(required=True)
    is_supervise_needed = serializers.BooleanField(required=True)
    supervise_type = serializers.ChoiceField(required=True, choices=PROCESSOR_CHOICES)
    engine_version = serializers.CharField(required=True)
    supervisor = serializers.CharField(
        required=True, max_length=LEN_LONG, allow_blank=True
    )
    is_enabled = serializers.BooleanField(required=True)
    is_draft = serializers.BooleanField(required=True)
    is_revocable = serializers.BooleanField(required=True)
    revoke_config = serializers.JSONField(required=True)
    notify = serializers.ListField(required=True)
    notify_rule = serializers.ChoiceField(
        required=True, allow_blank=True, choices=NOTIFY_RULE_CHOICES
    )
    notify_freq = serializers.IntegerField(default=EMPTY_INT)
    workflow_id = serializers.IntegerField(required=False)


class ServiceImportSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
    )
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    is_valid = serializers.BooleanField(required=True)
    display_type = serializers.ChoiceField(required=True, choices=DISPLAY_CHOICES)
    display_role = serializers.CharField(
        required=True, max_length=LEN_LONG, allow_blank=True
    )
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)
    source = serializers.ChoiceField(required=True, choices=SERVICE_SOURCE_CHOICES)
    owners = serializers.CharField(
        required=False, error_messages={"blank": _("服务负责人不能为空")}
    )
    workflow = WorkflowImportSerializer(required=True)

    catalog_id = serializers.IntegerField(required=False)

    def validate(self, attrs):

        project_key = attrs["project_key"]
        if not Project.objects.filter(key=project_key).exists():
            raise serializers.ValidationError(_("导入失败，project_key 对应的项目不存在"))

        catalog_id = attrs.get("catalog_id", None)
        if catalog_id is not None:
            if not ServiceCatalog.objects.filter(id=catalog_id).exists():
                raise serializers.ValidationError(_("导入失败，对应的服务目录不存在"))

        service_id = attrs.get("id", None)
        if service_id is not None:
            if not Service.objects.filter(id=service_id).exists():
                raise serializers.ValidationError(_("更新失败，对应的服务不存在"))

        return attrs
