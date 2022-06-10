# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework import serializers
from django.utils.translation import ugettext as _

from itsm.component.exceptions import ParamError
from itsm.service.models import ServiceCatalog
from itsm.service.serializers import ServiceSerializer
from itsm.service.validators import key_validator
from itsm.workflow.models import (
    Workflow,
    DEFAULT_ENGINE_VERSION,
    LEN_LONG,
    Field,
    GlobalVariable,
)
from itsm.workflow.serializers import (
    FieldSerializer,
    AuthModelSerializer,
    FieldValidator,
)


class OpenApiServiceSerializer(ServiceSerializer):
    key = serializers.CharField(
        required=False,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )

    @transaction.atomic
    def create(self, validated_data):
        """创建后立即绑定"""

        # 初始化一个流程
        work_flow_instance = self.init_work_flow(validated_data)

        # 创建一个新的流程版本
        version = work_flow_instance.create_version()

        validated_data["workflow"] = version
        validated_data["is_valid"] = False
        validated_data["key"] = "request"

        instance = super(ServiceSerializer, self).create(validated_data)
        catalog_id = ServiceCatalog.objects.get(
            key="{}_FUWUFANKUI".format(instance.project_key)
        ).id
        instance.bind_catalog(catalog_id, instance.project_key)

        return instance

    def init_work_flow(self, validated_data):
        if Workflow.objects.filter(name=validated_data["name"]).exists():
            raise serializers.ValidationError(
                {str(_("参数校验失败")): _("系统中已存在同名流程，请尝试换个流程名称")}
            )
        work_flow_instance = Workflow.objects.create(
            name=validated_data["name"],
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


class CustomFieldValidator(FieldValidator):
    def key_validate(self, value):
        """
        key的有效性校验
        """
        self.field_key_validate(value.get("key"))

        if value.get("state_id") is None and not value.get("is_builtin", False):
            raise ParamError(_("非内置字段state_id不允许为空"))

        if value.get("id") is None:
            if (
                Field.objects.filter(
                    workflow_id=value.get("workflow"), key=value.get("key")
                ).exists()
                or GlobalVariable.objects.filter(
                    flow_id=value.get("workflow").id, key=value.get("key")
                ).exists()
            ):
                raise ParamError(_("当前流程已存在唯一标识【{}】，请重新输入").format(value.get("key")))


class BatchSaveFieldSerializer(FieldSerializer):
    id = serializers.IntegerField(required=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        super(AuthModelSerializer, self).__init__(*args, **kwargs)
        self.resource_permissions = {}
        self.validators = [CustomFieldValidator(self.instance)]

    def to_representation(self, instance):
        data = super(serializers.ModelSerializer, self).to_representation(instance)
        return data
