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
import datetime
import json
import os

from django.conf import settings
from django.db import transaction
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import (
    BUILTIN_SYSDICT_LIST,
    DEFAULT_ENGINE_VERSION,
    BKBASE_CATALOG_KEY,
)
from itsm.component.constants import BUILTIN_SERVICES, OPEN, DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.db import managers
from itsm.component.utils.basic import dotted_name


class CatalogQuerySet(QuerySet):
    def select_related_common(self):
        return self.select_related("parent")


class SlaManager(managers.Manager):
    """Sla管理器"""

    pass


class CatalogServiceManager(managers.Manager):
    """服务目录管理器"""

    pass


class ServiceManager(managers.Manager):
    """Service管理器"""

    def init_builtin_services(self):
        from django.db.models import Q
        from itsm.workflow.models import Workflow

        for builtin_service in BUILTIN_SERVICES:

            try:
                original_workflow = Workflow.objects.get(
                    name=builtin_service["flow_name"], is_builtin=True
                )
            except Workflow.DoesNotExist:
                continue
            if self.filter(
                Q(workflow__workflow_id=original_workflow.id)
                | Q(name=builtin_service["name"])
            ).exists():
                # 关联的流程已经存在，不再做初始化
                continue

            self.create(
                name=builtin_service["name"],
                display_type=builtin_service.get("display_type", OPEN),
                display_role=dotted_name(builtin_service.get("display_role", "")),
                key="request",
                desc=builtin_service.get("desc", "内置服务"),
                workflow=original_workflow.create_version(),
            )

    def init_iam_services(self):
        from itsm.workflow.models import Workflow
        from itsm.component.constants import BUILTIN_IAM_SERVICES

        for builtin_service in BUILTIN_IAM_SERVICES:
            original_workflow = Workflow.objects.get(
                name=builtin_service["flow_name"], is_iam_used=True
            )
            obj = self.filter(
                workflow__workflow_id=original_workflow.id, name=builtin_service["name"]
            ).first()
            if not obj:
                obj = self.create(
                    name=builtin_service["name"],
                    display_type=builtin_service["display_type"],
                    display_role=dotted_name(builtin_service.get("display_role", "")),
                    key="request",
                    desc=builtin_service.get("desc", "内置服务"),
                    workflow=original_workflow.create_version(),
                )

            if builtin_service.get("bind"):
                obj.display_role = dotted_name(builtin_service.get("display_role", ""))
                obj.bind_catalog_by_key(builtin_service["bind"])
                obj.save()

    def init_bkbase_services(self):
        from itsm.workflow.models import Workflow
        from itsm.component.constants import BUILTIN_BKBASE_SERVICES
        from itsm.service.models import ServiceCatalog

        def create_service_catalog():
            bk_base_catalog = ServiceCatalog.objects.filter(
                name="蓝鲸基础平台", project_key="0"
            ).first()
            if bk_base_catalog is not None:
                print("蓝鲸基础平台 已存在, catalog_id = {}".format(bk_base_catalog))
                return bk_base_catalog.id
            root_catalog = ServiceCatalog.objects.get(key="root", project_key="0")
            new_catalog = root_catalog.create_catalog(
                name="蓝鲸基础平台", key=BKBASE_CATALOG_KEY, parent=root_catalog
            )
            return new_catalog.id

        bk_base_catalog_id = create_service_catalog()
        for builtin_service in BUILTIN_BKBASE_SERVICES:
            original_workflow = Workflow.objects.filter(
                name=builtin_service["flow_name"]
            ).first()

            obj = self.filter(name=builtin_service["name"]).first()
            if not obj:
                obj = self.create(
                    name=builtin_service["name"],
                    display_type=builtin_service["display_type"],
                    display_role=dotted_name(builtin_service.get("display_role", "")),
                    key="request",
                    desc=builtin_service.get("desc", "内置服务"),
                    workflow=original_workflow.create_version(),
                )

                if builtin_service.get("bind"):
                    obj.display_role = dotted_name(
                        builtin_service.get("display_role", "")
                    )
                    obj.bind_catalog(catalog_id=bk_base_catalog_id)
                    obj.save()
            else:
                obj.bind_catalog(catalog_id=bk_base_catalog_id)

    def insert_services(self, services, catalog=None):
        from itsm.workflow.models import Workflow

        if not services:
            return {"result": True, "message": "success"}
        all_flow_name = [new_service["flow_name"] for new_service in services]
        all_service_name = [new_service["name"] for new_service in services]

        all_original_workflow = {
            flow.name: flow for flow in Workflow.objects.filter(name__in=all_flow_name)
        }

        existed_services = self.filter(name__in=all_service_name).values_list(
            "name", flat=True
        )

        for new_service in services:
            original_workflow = all_original_workflow.get(new_service["flow_name"])
            if original_workflow is None or new_service["name"] in existed_services:
                # 流程不存在, 可以忽略
                # 导入的服务已经存在，忽略不处理
                continue

            instance = self.create(
                name=new_service["name"],
                display_type=new_service.get("display_type", OPEN),
                display_role=dotted_name(new_service.get("display_role", "")),
                key="request",
                desc=new_service.get("desc", "内置服务"),
                workflow=original_workflow.create_version(),
            )
            if new_service.get("bind_default_catalog"):
                print(
                    "bind service {name} to {catalog}".format(
                        name=instance.name, catalog=catalog.name
                    )
                )
                instance.bind_catalog(catalog.id)

        if existed_services:
            return {
                "result": False,
                "message": "Partial failed, the following services already exist: {} ".format(
                    ",".join(existed_services)
                ),
            }
        return {"result": True, "message": "success"}

    def upgrade_services_flow(self, **kwargs):

        """更新现有服务绑定的流程版本"""

        print("-------------------upgrade_services_flow------------------------\n")
        from itsm.workflow.models import WorkflowVersion

        print("migrate service bind and non bind workflows")

        flow_services = {}
        for service in self.all():
            if service.workflow.engine_version == DEFAULT_ENGINE_VERSION:
                print("skip pipeline version flow")
                continue

            flow_services.setdefault(service.workflow.id, []).append(service.id)
        print(
            ("group services by flow version: %s" % json.dumps(flow_services, indent=2))
        )

        for old_flow_id, services in list(flow_services.items()):
            # upgrade old flow version to pipeline version
            print("upgrade flow version(%s) for services: %s" % (old_flow_id, services))
            (
                new_flow,
                states_map,
                transitions_map,
            ) = WorkflowVersion.objects.upgrade_version(
                old_flow_id, for_migrate=True, **kwargs
            )
            self.filter(id__in=services).update(workflow=new_flow)

        # upgrade old non bind flow version to pipeline version
        for non_bind_flow in WorkflowVersion.objects.exclude(
            engine_version=DEFAULT_ENGINE_VERSION
        ):
            print("upgrade non_bind_flows version: %s" % non_bind_flow)
            WorkflowVersion.objects.upgrade_version(non_bind_flow.id, **kwargs)

    def get_or_create_service_and_catalog_from_version(self, *args, **kwargs):

        """创建服务条目并绑定到服务目录
        排除草稿流程，仅创建有效流程的服务项
        """

        from itsm.workflow.models import WorkflowVersion
        from itsm.service.models import OldSla, ServiceCatalog, CatalogService

        ver_for_service = {}

        print("Service.get_or_create_service_and_catalog_from_version")
        for ver in WorkflowVersion._objects.all():
            # 排除草稿流程
            if ver.is_draft:
                print("skip draft workflow version: %s(%s)" % (ver.name, ver.flow_type))
                continue

            print("create service item for version: %s(%s)" % (ver.name, ver.flow_type))
            obj, created = self.get_or_create(
                defaults={
                    "key": ver.flow_type,
                    "sla": OldSla.objects.get(name="三级", level=1),
                    "desc": ver.desc,
                    "is_deleted": ver.is_deleted,
                },
                **{"name": ver.name, "workflow": ver},  # noqa
            )

            # 关联目录
            try:
                catalog = ServiceCatalog._objects.get(
                    key=ver.extras["service_property"]
                    .get("public", {})
                    .get("service_category")
                )

                catalog_service, created = CatalogService.objects.get_or_create(
                    service=obj, catalog=catalog
                )

                ver_for_service[ver.pk] = catalog_service

                print(
                    "create service({}) and bind catalog({})".format(obj.id, catalog.id)
                )
            except ServiceCatalog.DoesNotExist:
                print("catalog not found: {} - {}".format(ver.id, ver.name))

        return ver_for_service

    def clone(self, tag_data, username, catalog_id=None):
        from itsm.workflow.models import Workflow

        def get_catalog_id(project_key):
            from itsm.service.models import ServiceCatalog

            if project_key == DEFAULT_PROJECT_PROJECT_KEY:
                key = "FUWUFANKUI"
            else:
                key = "{}_FUWUFANKUI".format(project_key)
            catalog_id = ServiceCatalog.objects.get(key=key).id
            return catalog_id

        logger.info("正在开始克隆服务，name={}".format(tag_data["name"]))
        with transaction.atomic():
            workflow_tag_data = tag_data.pop("workflow")
            workflow_tag_data["is_builtin"] = False
            task_settings = []
            if workflow_tag_data.get("extras", {}).get("task_settings"):
                task_settings = workflow_tag_data["extras"].pop("task_settings")
            workflow, state_map, _ = Workflow.objects.clone(workflow_tag_data, username)
            self.clone_task_settings(workflow, task_settings, state_map)
            version = workflow.create_version()
            tag_data["workflow_id"] = version.id
            version_number = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            tag_data["name"] = "{}_copy_{}".format(tag_data["name"], version_number)
            tag_data["creator"] = tag_data["updated_by"] = username
            service = self.create(**tag_data)
            project_key = tag_data["project_key"]
            if catalog_id is None:
                catalog_id = get_catalog_id(project_key=project_key)
            service.bind_catalog(catalog_id, project_key)
            return service
        return None

    def clone_task_settings(self, workflow, task_settings, state_map):
        """
        task_settings = [
            {
                "create_task_state": 97,
                "task_schema_id": 1,
                "execute_task_state": 97,
                "need_task_finished": true,
                "execute_can_create": true
            }
        ],
        state_map = {84: 138, 85: 139, 86: 140, 96: 141, 97: 142}
        """
        if task_settings:
            for task_setting in task_settings:
                create_task_state = task_setting["create_task_state"]
                task_setting["create_task_state"] = state_map.get(create_task_state)
                execute_task_state = task_setting["execute_task_state"]
                task_setting["execute_task_state"] = state_map.get(execute_task_state)
            workflow.extras["task_settings"] = task_settings
            workflow.create_task(task_settings)
            workflow.save()


class SysDictManager(managers.Manager):
    """Datadict管理器"""

    def init_builtin_dicts(self, *args, **kwargs):
        """初始化内置数据字典：可重入"""

        print("SysDict.init_builtin_dicts")
        from itsm.service.models import DictData

        for builtin_dict in BUILTIN_SYSDICT_LIST:
            obj, created = self.get_or_create(
                defaults={
                    "is_builtin": True,
                    "name": builtin_dict["name"],
                    "updated_by": "system",
                    "creator": "system",
                    "is_show": builtin_dict["is_show"],
                },
                **{"key": builtin_dict["key"]},
            )

            if builtin_dict["init_by"] == "jsonfile":
                json_file_path = os.path.join(
                    settings.PROJECT_ROOT, "initials", builtin_dict["items"]
                )

                with open(json_file_path) as json_file:
                    json_data = json.loads(json_file.read())
            else:
                json_data = builtin_dict["items"]

            # 支持两种数据格式的初始化
            if isinstance(json_data, dict):
                DictData.create_builtin_dicts_data(obj, json_data)
            elif isinstance(json_data, list):
                DictData.create_builtin_dicts_ordered_data(obj, json_data)

    def init_change_type_from_property(self):
        """迁移变更类型到数据字典：CHANGE_TYPE"""

        if self.model._objects.exists():
            print("Service exists, skip init_change_type_from_property")
            return

        print("Service.init_change_type_from_property")
        from itsm.service.models import ServiceProperty, PropertyRecord, DictData

        change_type = self.get(key="CHANGE_TYPE")

        try:
            property = ServiceProperty.objects.get(key="change_type")
            for record in PropertyRecord.objects.filter(service_property=property):
                DictData.create_item(
                    dict_table=change_type,
                    key=record.key,
                    name=record.data.get("level"),
                    is_deleted=record.is_deleted,
                    is_readonly=True,
                )
        except ServiceProperty.DoesNotExist:
            # 全新安装，不需要迁移数据
            pass

    def init_event_type_from_property(self):
        """迁移事件类型到数据字典：CHANGE_TYPE"""

        if self.model._objects.exists():
            print("Service exists, skip init_event_type_from_property")
            return

        print("Service.init_event_type_from_property")
        from itsm.service.models import ServiceProperty, PropertyRecord, DictData

        event_type = self.get(key="EVENT_TYPE")
        event_type_fault = event_type.dict_data.get(key="fault")

        try:
            property = ServiceProperty.objects.get(key="event_type")

            for record in PropertyRecord.objects.filter(service_property=property):
                if record.data.get("level") == 2:
                    item_level2 = DictData.create_item(
                        dict_table=event_type,
                        key=record.key,
                        name=record.data.get("name"),
                        is_deleted=record.is_deleted,
                        is_readonly=True,
                        parent=event_type_fault,
                    )

                    for record in PropertyRecord.objects.filter(
                        service_property=property
                    ):
                        if record.data.get("level") == 3:
                            DictData.create_item(
                                dict_table=event_type,
                                key=record.key,
                                name=record.data.get("name"),
                                is_deleted=record.is_deleted,
                                is_readonly=True,
                                parent=item_level2,
                            )
        except ServiceProperty.DoesNotExist:
            # 全新安装，不需要迁移数据
            pass


class BaseMpttManager(managers.BaseTreeManager):
    pass


class DictDataManager(BaseMpttManager):
    pass


class ServiceCatalogManager(BaseMpttManager):
    """服务目录管理器"""

    def migrate_from_service_category(self):
        """服务目录、数据字典概念引入后的数据迁移"""

        if self.model._objects.exists():
            print("ServiceCatalog exists, skip migrate_from_service_category")
            return

        from itsm.service.models import ServiceProperty

        try:
            service_category = ServiceProperty._objects.get(key="service_category")
        except ServiceProperty.DoesNotExist:
            print("skip migrate_from_service_category")
            return

        from itsm.service.models import PropertyRecord

        service_categories = PropertyRecord._objects.filter(
            service_property=service_category
        )

        if self.filter(key="root", is_deleted=False).exists():
            print("skip exist migrate_from_service_category")
            return

        root = self.model.create_root(key="root", name=_("根目录"), is_deleted=False)

        print("migrate service_category to service_catalog")
        for level1 in service_categories:
            if level1.data.get("level") == 1:
                grandfather = self.model.create_catalog(
                    key=level1.key,
                    name=level1.data.get("name"),
                    parent=root,
                    is_deleted=level1.is_deleted,
                )
                for level2 in service_categories:
                    if (
                        level2.data.get("level") == 2
                        and level2.data.get("parent_key") == grandfather.key
                    ):
                        father = self.model.create_catalog(
                            key=level2.key,
                            name=level2.data.get("name"),
                            parent=grandfather,
                            is_deleted=level2.is_deleted,
                        )
                        for level3 in service_categories:
                            if (
                                level3.data.get("level") == 3
                                and level3.data.get("parent_key") == father.key
                            ):
                                self.model.create_catalog(
                                    key=level3.key,
                                    name=level3.data.get("name"),
                                    parent=father,
                                    is_deleted=level3.is_deleted,
                                )

    def init_default_catalog(self, catalog, ignore_exists=False):

        if self.model._objects.exists() and not ignore_exists:
            print("ServiceCatalog exists, skip init ServiceCatalog")
            return

        level_1 = [item for item in catalog if item["level"] == 1]
        level_2 = [item for item in catalog if item["level"] == 2]
        # 预留支持3级
        level_3 = [item for item in catalog if item["level"] == 3]
        root = self.model.create_root(key="root", name=_("根目录"), is_deleted=False)
        for level1 in level_1:
            l_1 = self.model.create_catalog(
                key=level1["key"], name=level1["name"], parent=root
            )
            for level2 in level_2:
                if l_1.key == level2["parent_key"]:
                    l_2 = self.model.create_catalog(
                        key=level2["key"], name=level2["name"], parent=l_1
                    )
                    for level3 in level_3:
                        if l_2.key == level3["parent_key"]:
                            self.model.create_catalog(
                                key=level3["key"], name=level3["name"], parent=l_2
                            )
