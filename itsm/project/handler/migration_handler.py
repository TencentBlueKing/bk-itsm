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

from abc import abstractmethod

from django.db import transaction
from django.utils.translation import ugettext as _

from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.exceptions import ResourceTypeNotFound, ProjectNotFound, NoMigratePermission
from itsm.project.handler.utils import MigrateIamRequest
from itsm.project.models import Project
from itsm.service.models import Service, CatalogService, ServiceCatalog
from itsm.ticket.models import Ticket, UserRole

GRANT = "grant"
REVOKE = "revoke"


class MigrationHandlerBase(object):
    resource_type = None

    @abstractmethod
    def handler(self, resource_id, old_project_key, new_project_key, request):
        """
        迁移处理逻辑
        """

    def grant_or_revoke_instance_permission(self, request, actions, obj, operate):
        iam = MigrateIamRequest(request)
        resources = [{
            "resource_id": obj.id,
            "resource_name": obj.name,
            "resource_type": obj.auth_resource.get("resource_type"),
            "resource_type_name": obj.auth_resource.get("resource_type_name"),
        }]
        iam.grant_or_revoke_instance_permission(actions, resources, operate=operate,
                                                project_key=obj.project_key)

    def grant_or_revoke_permit_with_project(self, request, actions, project_key, operate):
        iam = MigrateIamRequest(request)
        iam.grant_or_revoke_permit_with_project(actions, operate, project_key)

    def iam_auth(self, request, apply_actions, obj=None, project_key=DEFAULT_PROJECT_PROJECT_KEY):

        resources = []
        if obj:
            resources.append(
                {
                    "resource_id": obj.id,
                    "resource_name": getattr(obj, "name"),
                    "resource_type": obj.auth_resource['resource_type'],
                    "creator": obj.creator,
                }
            )

        iam_client = MigrateIamRequest(request)
        if resources:
            auth_actions = iam_client.batch_resource_multi_actions_allowed(set(apply_actions),
                                                                           resources,
                                                                           project_key=project_key)
            auth_actions = auth_actions.get(resources[0]['resource_id'], {})
        else:
            auth_actions = iam_client.resource_multi_actions_allowed(apply_actions, [])

        if self.auth_result(auth_actions, apply_actions):
            return True

        return False

    @staticmethod
    def auth_result(auth_actions, actions):
        """
        认证结果解析
        """
        denied_actions = []
        for action, result in auth_actions.items():
            if action in actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0


class ServiceMigrationHandler(MigrationHandlerBase):
    resource_type = "service"

    def handler(self, resource_id, old_project_key, new_project_key, request):
        ready_migrate_service = Service.objects.filter(project_key=old_project_key,
                                                       id=resource_id).first()

        # 如果在默认项目下搜索不到该服务，则证明已经被迁移过了或者数据有问题，此时不进行迁移
        if ready_migrate_service is None:
            return
        actions = ["service_manage", "ticket_view"]

        # 鉴权，用户是否有该资源的service_manage权限，有的话才可以进行迁移
        if not self.iam_auth(request, actions, ready_migrate_service, old_project_key):
            raise NoMigratePermission(_("您当前没有权限迁移该服务，您在权限中心没有该服务的权限，service_name={}".
                                        format(ready_migrate_service.name)))

        # 先回收权限
        self.grant_or_revoke_instance_permission(request, actions,
                                                 ready_migrate_service, REVOKE)

        # 获取该项目获取的catalog名称
        catalog_name = ready_migrate_service.bounded_catalogs[0]

        # 如果对应的服务目录本身就有
        new_project_catalog = ServiceCatalog.objects.filter(project_key=new_project_key,
                                                            name=catalog_name).first()

        if new_project_catalog is None:
            # 同步相关目录
            service_catalog = ServiceCatalog.objects.filter(
                id=ready_migrate_service.catalog_id).first()
            path_list = list(service_catalog.get_ancestors())
            path_list.append(service_catalog)
            # 新生成的节点树的最后一个节点
            new_project_catalog = self.sync_catalog_tree(path_list, new_project_key)

        with transaction.atomic():
            catalog_service = CatalogService.objects.filter(
                service=ready_migrate_service).first()
            catalog_service.catalog = new_project_catalog
            catalog_service.save()
            ready_migrate_service.project_key = new_project_key
            ready_migrate_service.save()

        # 同步单据
        with transaction.atomic():
            tickets = Ticket.objects.filter(service_id=ready_migrate_service.id)
            for ticket in tickets:
                ticket.project_key = new_project_key
                ticket.save()

        # 权限中心授权
        actions = ["service_manage", "service_view", "ticket_view"]
        self.grant_or_revoke_instance_permission(request, actions, ready_migrate_service, "grant")

    def sync_catalog_tree(self, path_list, new_project_key):
        # 同步该目录
        same_catalog = self.find_same_node(path_list, new_project_key)
        same_catalog_index = path_list.index(same_catalog)
        service_catalog = ServiceCatalog.objects.filter(project_key=new_project_key,
                                                        name=same_catalog.name).first()
        for catalog in path_list[same_catalog_index + 1:]:
            service_catalog = ServiceCatalog.create_catalog(name=catalog.name,
                                                            parent=service_catalog,
                                                            project_key=new_project_key)
        return service_catalog

    def find_same_node(self, path_list, new_project_key):
        """
        找到两个项目 服务目录的第一个共同的目录
        """
        for catalog in reversed(path_list):
            if ServiceCatalog.objects.filter(project_key=new_project_key,
                                             name=catalog.name).exists():
                return catalog


class UserGroupMigrationHandler(MigrationHandlerBase):
    resource_type = "user_group"

    def handler(self, resource_id, old_project_key, new_project_key, request):

        user_role = UserRole.objects.filter(project_key=old_project_key,
                                            id=resource_id).first()

        if user_role is None:
            return

        if not request.user.username == user_role.creator:
            raise NoMigratePermission("权限迁移失败，请联系该用户组创建者进行迁移")
        actions = ["user_group_view", "user_group_edit", "user_group_delete"]
        user_role.auth_resource = {"resource_type": "user_group", "resource_type_name": "用户组"}
        # 取消实例级别的授权
        self.grant_or_revoke_instance_permission(request, actions, user_role, REVOKE)

        with transaction.atomic():
            user_role.project_key = new_project_key
            user_role.save()
            
        user_role.auth_resource = {"resource_type": "user_group", "resource_type_name": "用户组"}
        actions = ["user_group_view", "user_group_edit", "user_group_delete"]
        self.grant_or_revoke_instance_permission(request, actions, user_role, GRANT)


class MigrationHandlerDispatcher(object):
    MIGRATIONS_HANDLER_CLASS = [
        ServiceMigrationHandler,
        UserGroupMigrationHandler,
    ]

    # 保留映射变量，便于直接从 object_class 找到对象定义
    MIGRATIONS_HANDLER_CLASS_DICT = dict(
        [(_object.resource_type, _object()) for _object in MIGRATIONS_HANDLER_CLASS])

    def __init__(self, resource_type):
        self.resource_type = resource_type

    def migrate(self, resource_id, old_project_key, new_project_key, request):
        """
        
        """
        if not Project.objects.filter(key=old_project_key).exists():
            raise ProjectNotFound()

        if not Project.objects.filter(key=new_project_key).exists():
            raise ProjectNotFound()

        if self.resource_type not in self.MIGRATIONS_HANDLER_CLASS_DICT:
            raise ResourceTypeNotFound()

        self.MIGRATIONS_HANDLER_CLASS_DICT[self.resource_type].handler(resource_id,
                                                                       old_project_key,
                                                                       new_project_key,
                                                                       request)
