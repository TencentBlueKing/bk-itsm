# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import post_save
from rest_framework import serializers
from django.utils.translation import ugettext as _

from itsm.component.exceptions import ParamError
from itsm.component.utils.basic import TempDisableSignal
from itsm.openapi.base_service.utils import WorkflowInitHandler
from itsm.service.models import ServiceCatalog, Service
from itsm.service.serializers import ServiceSerializer
from itsm.service.validators import key_validator
from itsm.workflow.models import (
    Workflow,
    DEFAULT_ENGINE_VERSION,
    LEN_LONG,
    Field,
    GlobalVariable,
    State,
    Table,
)
from itsm.workflow.serializers import (
    FieldSerializer,
    AuthModelSerializer,
    FieldValidator,
)
from itsm.workflow.signals.handlers import init_after_workflow_created


class OpenApiServiceSerializer(ServiceSerializer):
    key = serializers.CharField(
        required=False,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )
    workflow_meta = serializers.JSONField(required=False)

    @transaction.atomic
    def create(self, validated_data):
        """创建后立即绑定"""

        if "workflow_meta" in validated_data:
            workflow_meta = validated_data.pop("workflow_meta")
            if Workflow.objects.filter(name=workflow_meta["name"]).exists():
                raise serializers.ValidationError(
                    {str(_("参数校验失败")): _("系统中已存在同名流程，请尝试换个流程名称")}
                )
            with TempDisableSignal(post_save, init_after_workflow_created, Workflow):
                work_flow_instance = Workflow.objects.create(
                    name=workflow_meta["name"],
                    desc="",
                    flow_type="other",
                    notify_freq="0",
                    is_biz_needed=False,
                    is_iam_used=False,
                    is_enabled=True,
                    is_draft=False,
                    table_id=self.get_simple_table_id(),
                    owners="",
                    engine_version=DEFAULT_ENGINE_VERSION,
                    creator=validated_data["creator"],
                    updated_by=validated_data["updated_by"],
                )
                WorkflowInitHandler(work_flow_instance, workflow_meta).init_workflow()
        else:
            # 初始化一个流程
            work_flow_instance = self.init_work_flow(validated_data)

        # 创建一个新的流程版本
        version = work_flow_instance.create_version()

        validated_data["workflow"] = version
        validated_data["is_valid"] = False
        validated_data["key"] = "request"

        instance = super(ServiceSerializer, self).create(validated_data)
        if validated_data["project_key"] != "0":
            catalog_id = ServiceCatalog.objects.get(
                key="{}_FUWUFANKUI".format(instance.project_key)
            ).id
        else:
            catalog_id = ServiceCatalog.objects.get(key="FUWUFANKUI").id
        instance.bind_catalog(catalog_id, instance.project_key)

        return instance

    def get_simple_table_id(self):
        try:
            return Table.objects.get(name="简单", is_builtin=True).id
        except Table.DoesNotExist:
            return 1

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
            "workflow_meta",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS


class CustomFieldValidator(FieldValidator):
    def key_validate(self, value):
        """
        key的有效性校验
        """
        self.field_key_validate(value.get("key"))
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
    id = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.PrimaryKeyRelatedField(
        many=False, queryset=State.objects.all(), allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super(AuthModelSerializer, self).__init__(*args, **kwargs)
        self.resource_permissions = {}
        self.validators = [CustomFieldValidator(self.instance)]

    def to_representation(self, instance):
        data = super(serializers.ModelSerializer, self).to_representation(instance)
        return data


class ApiGwSerializer(serializers.Serializer):
    pass
