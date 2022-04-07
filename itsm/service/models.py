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

import operator
from functools import reduce
import six

import jsonfield
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q, Count
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from mptt.models import TreeForeignKey
from multiselectfield import MultiSelectField

from itsm.component.constants import (
    ADMIN,
    DEFAULT_STRING,
    DISPLAY_CHOICES,
    EMPTY_INT,
    EMPTY_LIST,
    EMPTY_STRING,
    FIRST_ORDER,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    SERVICE_CATEGORY,
    LEN_XX_LONG,
    TIME_DELTA,
    SERVICE_SOURCE_CHOICES,
    DEFAULT_PROJECT_PROJECT_KEY,
)
from itsm.component.db.models import BaseMpttModel
from itsm.component.drf.mixins import ObjectManagerMixin
from itsm.component.exceptions import DeleteError, ParamError, SlaParamError
from itsm.component.utils.basic import dotted_name, fill_tree_route, get_random_key
from itsm.component.utils.dimensions import fill_time_dimension
from itsm.openapi.service.serializers import WorkflowVersionFirstStateFieldSerializer
from itsm.role.models import UserRole
from itsm.service import managers


class Model(models.Model):
    """基础字段"""

    DISPLAY_FIELDS = (
        "is_builtin",
        "creator",
        "create_at",
        "updated_by",
        "update_at",
    )

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    end_at = models.DateTimeField(_("结束时间"), null=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)
    is_builtin = models.BooleanField(_("是否内置"), default=False)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    class Meta:
        abstract = True

    objects = models.Manager()
    _objects = models.Manager()

    auth_resource = {"resource_type": "system_settings", "resource_name": _("系统管理")}
    resource_operations = ["system_settings_manage"]

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()


class Favorite(models.Model):
    """
    服务收藏配置
    """

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, help_text=_("收藏的用户"), on_delete=models.CASCADE
    )
    name = models.CharField(_("收藏名称"), max_length=LEN_LONG)
    service = models.CharField(_("服务类型"), max_length=LEN_NORMAL)
    data = jsonfield.JSONField(_("收藏数据"), default=EMPTY_LIST)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "service"
        verbose_name = _("用户收藏")
        verbose_name_plural = _("用户收藏")

    def __unicode__(self):
        return "{}->{}".format(self.user, self.name)


class FavoriteService(models.Model):
    """
    服务收藏配置
    """

    user = models.CharField(_("收藏的用户"), max_length=LEN_LONG)
    service_id = models.IntegerField(_("服务标识"))
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        app_label = "service"
        verbose_name = _("用户收藏")
        verbose_name_plural = _("用户收藏")

    def __unicode__(self):
        return "{}->{}".format(self.user, self.service_id)


class ServiceCategory(Model):
    """
    服务类型：比如变更、事件
    相当于数据库 - DB
    """

    key = models.CharField(_("关键字"), max_length=LEN_NORMAL, unique=True)
    name = models.CharField(_("服务名称"), default="", max_length=LEN_LONG)
    desc = models.CharField(_("服务描述"), max_length=LEN_LONG)

    # type object 'ServiceCategory' has no attribute 'objects'
    # objects = models.Manager()

    class Meta:
        app_label = "service"
        verbose_name = _("服务类型")
        verbose_name_plural = _("服务类型")

    def __str__(self):
        return self.name

    @classmethod
    def init_service_data(cls, *args, **kwargs):
        """初始化服务类型"""

        print("init service data")
        for k, v in SERVICE_CATEGORY.items():
            cls.objects.get_or_create(
                defaults={"name": v, "desc": "{}类相关服务".format(v)}, **{"key": k}
            )

    @classmethod
    def get_service_keys(cls, upper=False):
        """获取服务关键字列表，支持转换为大写"""

        keys = cls.objects.values_list("key", flat=True)

        if upper:
            return [x.upper() for x in keys]

        return list(keys)


class OldSla(Model):
    """
    服务级别
    """

    level_choices = [
        (1, _("低")),
        (2, _("中")),
        (3, _("高")),
    ]
    name = models.CharField(_("名称"), max_length=LEN_LONG)
    key = models.CharField(_("级别关键字"), max_length=LEN_LONG, default=EMPTY_STRING)
    level = models.IntegerField(_("级别"), choices=level_choices, default=1)
    resp_time = models.CharField(_("响应时间要求"), max_length=LEN_NORMAL)
    deal_time = models.CharField(_("解决时间要求"), max_length=LEN_NORMAL)
    desc = models.CharField(
        _("描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )

    objects = managers.SlaManager()

    class Meta:
        app_label = "service"
        verbose_name = _("服务级别")
        verbose_name_plural = _("服务级别")

    def __unicode__(self):
        return "{}({})".format(self.name, self.level)

    @classmethod
    def get_unique_key(cls, name):
        """生成唯一的key"""

        key = get_random_key(name)
        retry = 0

        while retry < 60:
            # 满足条件，退出循环，且retry<60
            if not cls.objects.filter(key=key).exists():
                break

            key = get_random_key(name)
            retry += 1
        else:
            # 尝试60次一直重复，则放弃生成key
            return "##Err##"

        return key


class Service(ObjectManagerMixin, Model):
    """
    服务
    """

    key = models.CharField(_("服务编号"), max_length=LEN_NORMAL, default=DEFAULT_STRING)
    name = models.CharField(_("服务名称"), max_length=LEN_LONG)
    desc = models.CharField(_("服务描述"), max_length=LEN_LONG, default=EMPTY_STRING)

    workflow = models.ForeignKey(
        "workflow.WorkflowVersion",
        related_name="services",
        help_text=_("关联流程版本"),
        on_delete=models.CASCADE,
    )

    owners = models.TextField(help_text=_("服务负责人"), default=ADMIN)

    can_ticket_agency = models.BooleanField(_("是否可以代提单"), default=False)
    is_valid = models.BooleanField(_("是否有效"), default=True)

    display_type = models.CharField(
        _("可见范围类型"), max_length=LEN_SHORT, choices=DISPLAY_CHOICES, default="OPEN"
    )
    display_role = models.CharField(
        _("可见范围"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )

    source = models.CharField(
        _("来源"),
        max_length=LEN_SHORT,
        choices=SERVICE_SOURCE_CHOICES,
        null=True,
        default=None,
    )
    objects = managers.ServiceManager()

    need_auth_grant = True
    auth_resource = {"resource_type": "service", "resource_type_name": "服务"}
    resource_operations = ["service_manage"]

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "service"
        verbose_name = _("服务")
        verbose_name_plural = _("服务")

    # ========================================== property ====================================================

    @property
    def is_service_bound(self):
        """是否绑定了目录"""
        return CatalogService.is_service_bound(self)

    @property
    def catalog_id(self):
        """绑定的目录ID"""
        last_bound = CatalogService.objects.filter(service=self).last()
        return last_bound.catalog.id if last_bound else 0

    @property
    def bounded_catalogs(self):
        """绑定了的目录"""
        return CatalogService.bounded_catalogs(self)

    @property
    def bounded_relations(self):
        """绑定了的目录"""
        return CatalogService.bounded_relations(self)

    @property
    def first_state_id(self):
        state_id = None
        for key, item in self.workflow.states.items():
            if item["is_builtin"] and item["type"] == "NORMAL":
                state_id = key
        return state_id

    @property
    def service_type(self):
        return self.key

    @property
    def first_state_fields(self):
        """
        获取第一个节点的字段，提供给open api使用
        """

        return WorkflowVersionFirstStateFieldSerializer(
            self.workflow.get_first_state_fields(), many=True
        ).data

    @property
    def sla(self):
        return ServiceSla.objects.filter(service_id=self.id)

    # ======================================== classmethod ===================================================

    @classmethod
    def get_valid_and_permission_service(cls, username):
        """获取有效的/有权限的service"""
        conditions = cls.permission_filter(username)
        services = cls.objects.filter(reduce(operator.or_, conditions), is_valid=True)
        return services

    @classmethod
    def permission_filter(cls, username):
        conditions = [Q(display_type__in=["OPEN", "API"])]

        # 组织角色
        for organization in UserRole.get_user_roles(username)["organization"]:
            conditions.append(
                Q(display_type="ORGANIZATION") & Q(display_role__contains=organization)
            )

        # 通用角色
        for role in UserRole.get_general_role_by_user(dotted_name(username)):
            conditions.append(
                Q(display_type=role["role_type"]) & Q(display_role__contains=role["id"])
            )

        return conditions

    @classmethod
    def is_service_owner(cls, service_id, username):
        try:
            service = cls._objects.get(id=service_id)
        except cls.DoesNotExist:
            raise ParamError(_("您所请求的服务不存在"))

        return service.is_obj_manager(username)

    # ========================================== method ====================================================

    def bind_catalog(self, catalog_id, project_key=DEFAULT_PROJECT_PROJECT_KEY):
        """绑定服务到目录上"""

        if catalog_id is None or catalog_id == 0:
            return {"result": False, "message": "目录不能为空"}

        return CatalogService.bind_service_to_catalog(self.id, catalog_id, project_key)

    def bind_catalog_by_key(self, key):
        """绑定服务到目录上"""

        catalog_id = ServiceCatalog.objects.get(key=key).id

        return CatalogService.bind_service_to_catalog(self.id, catalog_id)

    def add_favorite(self, username):
        exist = FavoriteService.objects.filter(
            service_id=self.id, user=username
        ).exists()
        if not exist:
            FavoriteService.objects.create(service_id=self.id, user=username)

    def delete_favorite(self, username):
        FavoriteService.objects.filter(service_id=self.id, user=username).delete()

    @classmethod
    def get_count(cls, scope=None, project_queryset=Q()):
        services = Service.objects.filter(project_queryset)
        if scope:
            services = services.filter(create_at__range=scope)
        return services.count()

    @classmethod
    def get_service_statistics(cls, time_delta, data, project_key=None):
        project_query = Q(project_key=project_key) if project_key else Q()
        data_str = TIME_DELTA[time_delta].format(field_name="create_at")
        info = (
            cls.objects.filter(project_query)
            .filter(**data)
            .extra(select={"date_str": data_str})
            .values("date_str")
            .annotate(count=Count("id"))
            .order_by("date_str")
        )
        dates_range = fill_time_dimension(
            data["create_at__gte"], data["create_at__lte"], info, time_delta
        )
        return dates_range

    def update_service_sla(self, sla_tasks):
        """创建/更新服务时，更新ServiceSla"""
        ServiceSla.objects.filter(service_id=self.id).delete()
        for task in sla_tasks:
            task.update(service_id=self.id)
        ServiceSla.objects.bulk_create([ServiceSla(**task) for task in sla_tasks])

    def update_service_configs(self, service_config):
        self.can_ticket_agency = service_config["can_ticket_agency"]
        self.display_type = service_config["display_type"]
        self.display_role = dotted_name(service_config.get("display_role", ""))
        self.workflow_id = service_config["workflow_id"]
        if "owners" in service_config:
            self.owners = dotted_name(service_config["owners"])
        self.is_valid = True
        self.save()

    def sla_validate(self):
        from itsm.workflow.models import Workflow

        for sla in self.sla:
            start_node_id = sla.start_node_id
            end_node_id = sla.end_node_id
            workflow = Workflow.objects.get(id=self.workflow.workflow_id)
            state_count = workflow.states.filter(
                id__in=[start_node_id, end_node_id]
            ).count()
            if state_count != 2:
                ServiceSla.objects.filter(service_id=self.id).delete()
                raise SlaParamError("检测到您的流程节点发生改变，请您重新配置sla")
            try:
                workflow.can_bind_sla()
            except Exception as e:
                sla.delete()
                raise e

    @classmethod
    def validate_service_name(cls, service_name):
        return cls.objects.filter(name=service_name).exists()

    def tag_data(self):
        from itsm.workflow.models import Workflow

        workflow = Workflow.objects.get(id=self.workflow.workflow_id)
        return {
            "key": self.key,
            "name": self.name,
            "desc": self.desc,
            "workflow": workflow.tag_data(need_tag_task=True),
            "owners": self.owners,
            "can_ticket_agency": self.can_ticket_agency,
            "is_valid": self.is_valid,
            "display_type": self.display_type,
            "display_role": self.display_role,
            "source": "custom",
            "project_key": self.project_key,
        }


class ServiceSla(models.Model):
    """服务与SLA关联表"""

    service_id = models.IntegerField(_("服务ID"))
    start_node_id = models.IntegerField(_("计时开始节点ID"))
    end_node_id = models.IntegerField(_("计时结束节点ID"))
    name = models.CharField(_("任务名称"), max_length=LEN_LONG)
    sla_id = models.IntegerField(_("SLA协议 ID"))
    color = models.CharField(_("颜色标志"), max_length=LEN_SHORT, default=EMPTY_STRING)
    lines = jsonfield.JSONField(_("线条列表"), default=EMPTY_LIST)
    states = jsonfield.JSONField(_("节点列表"), default=EMPTY_LIST)

    class Meta:
        app_label = "service"
        verbose_name = _("服务与SLA关联表")
        verbose_name_plural = _("服务与SLA关联表")


class ServiceCatalog(BaseMpttModel):
    """服务目录"""

    key = models.CharField(_("目录关键字"), max_length=LEN_LONG, unique=True)
    name = models.CharField(_("目录名称"), max_length=LEN_NORMAL)
    desc = models.CharField(
        _("目录描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    order = models.IntegerField(_("节点顺序"), default=FIRST_ORDER)
    xt_only = models.BooleanField(_("特殊过滤"), default=False)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("上级目录"),
        null=True,
        blank=True,
        related_name="children",
    )
    route = jsonfield.JSONField(_("前置路径集合"), default=EMPTY_LIST)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    objects = managers.ServiceCatalogManager()

    auth_resource = {"resource_type": "system_settings", "resource_name": _("流程元素")}
    resource_operations = ["system_settings_manage"]

    class Meta:
        app_label = "service"
        verbose_name_plural = _("服务目录")
        verbose_name = _("服务目录")
        ordering = ("order",)

    class MPTTMeta:
        parent_attr = "parent"
        order_insertion_by = ["name"]

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """自动填充key"""

        # 创建目录时若key为空则自动生成key
        if self.pk is None and not self.key:
            self.key = get_random_key(self.name)

        # get_ancestors不能用于未创建的实例
        if self.parent:
            self.route = list(
                self.parent.get_ancestors(include_self=True).values("id", "name")
            )

        return super(ServiceCatalog, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if (
            not self.is_leaf_node()
            and self.get_children().filter(is_deleted=False).exists()
        ):
            raise DeleteError(_("请先删除【{}】下的子目录").format(self.name))

        super(ServiceCatalog, self).delete(*args, **kwargs)

    @cached_property
    def parent_name(self):
        """用箭头连接的上层目录"""
        return ">".join([c.name for c in self.get_ancestors()])

    @cached_property
    def link_parent_name_ex_root(self):
        """连接父级名称，不包括根节点"""
        parent_name = self.parent_name.split(">")[1:]
        parent_name.append(self.name)
        return ">".join(parent_name)

    @cached_property
    def parent_key(self):
        """上层目录key"""
        return self.parent.key

    @cached_property
    def included_services_count(self):
        """获取目录树下的services数目（去重）"""
        return (
            CatalogService.objects.filter(
                catalog__in=self.get_descendants(include_self=True),
                service__is_deleted=False,
            )
            .values("service")
            .distinct()
            .count()
        )

    @classmethod
    def get_descendant_ids(cls, catalog_id):
        if not catalog_id:
            return []
        try:
            node = cls.objects.get(id=catalog_id)
        except cls.DoesNotExist:
            return []
        return [child.id for child in node.get_descendants(include_self=True)]

    @staticmethod
    def subtree(node, catalogs=None, show_deleted=False, catalog_count=None):
        """获取以node为根的子树"""

        # 根据catalogs列表筛选
        node_children = node.get_children()
        node_children = node_children.exclude(key="approve_service_catalog")
        # 展示删掉的目录
        if not show_deleted:
            node_children = node_children.filter(is_deleted=False)

        if catalogs:
            node_children = node_children.filter(id__in=catalogs)

        # 递归查询，sql查询次数过多 TODO
        children = [
            node.subtree(child, catalogs, show_deleted, catalog_count)
            for child in node_children
        ]

        data = {
            "id": node.id,
            "key": node.key,
            "name": _("{} (已删除)").format(node.name) if node.is_deleted else node.name,
            "is_deleted": node.is_deleted,
            "level": node.level,
            "desc": node.desc,
            "parent_id": getattr(node.parent, "id", ""),
            "parent_name": getattr(node.parent, "name", ""),
            # 默认展开一级
            "expanded": node.level == 0,
            "children": children,
            "route": node.route,
            # 配合前端，设置图标
            "openedIcon": "icon-folder-open",
            "closedIcon": "icon-folder",
            "icon": "icon-folder",
        }

        if catalog_count:
            data["service_count"] = catalog_count.get(data["id"], 0)

        return data

    @classmethod
    def annotate_catalog_count(cls, project_key):
        """
        计算每一节目录下的服务数量
        """
        catalog_count = {}
        catalogs = ServiceCatalog.objects.filter(project_key=project_key)
        for catalog in catalogs:
            catalog_count[catalog.id] = catalog.included_services_count

        return catalog_count

    @classmethod
    def tree_data(
        cls,
        request,
        key="",
        show_deleted=False,
        project_key=DEFAULT_PROJECT_PROJECT_KEY,
    ):
        """
        服务目录树
        根据服务编码过滤服务目录
        """
        catalog_count = cls.annotate_catalog_count(project_key)

        def _catalog_services_filter(key, request, show_deleted):
            if key == "global":
                catalog_services = CatalogService._objects.select_related(
                    "service", "catalog"
                ).filter(project_key=project_key)
            else:
                catalog_services = CatalogService._objects.select_related(
                    "service", "catalog"
                ).filter(service__key=key, project_key=project_key)

            # 支持：服务被移除或者被删除后，仍然需要查看历史目录并查询单据
            if not show_deleted:
                catalog_services = catalog_services.filter(
                    is_deleted=False, service__is_deleted=False
                )

            # 服务展示过滤
            if UserRole.is_itsm_superuser(
                request.user.username
            ) or UserRole.is_statics_manager(request.user.username):
                return catalog_services

            c_s = catalog_services.filter(service__is_valid=True)

            # 根据组织架构/通用角色过滤服务
            service_ids = Service.get_valid_and_permission_service(
                request.user.username
            ).values_list("id", flat=True)
            c_s = c_s.filter(service_id__in=service_ids)

            # 特殊过滤
            if request.META.get("HTTP_X_TIF_UID", "NO_HEADER") == request.COOKIES.get(
                "xt_uid", "NO_COOKIE"
            ):
                return c_s.filter(catalog__xt_only=True)

            return c_s.filter(catalog__xt_only=False)

        catalog_services = _catalog_services_filter(key, request, show_deleted)
        catalogs = set()
        for cs in catalog_services:
            for parent in cs.catalog.route:
                catalogs.add(parent["id"])
            catalogs.add(cs.catalog.id)

        # 目录中没有服务编码相关的服务
        if key and not catalogs:
            return []

        roots = cls.objects.filter(
            level=0, is_deleted=False, project_key=project_key
        ).order_by("order")
        if catalogs:
            roots = roots.filter(id__in=catalogs)

        roots = roots.order_by("lft", "id")

        tree = [
            cls.subtree(root, catalogs, show_deleted, catalog_count) for root in roots
        ]

        return tree

    @transaction.atomic
    def delete_subtree(self):
        for descendant in self.get_descendants(include_self=True).order_by("-level"):
            # delete directory's files
            descendant.delete()

    @classmethod
    def create_root(cls, key, name, is_deleted, **kwargs):
        return cls.create_catalog(key=key, name=name, is_deleted=is_deleted, **kwargs)

    @classmethod
    @transaction.atomic
    def create_catalog(cls, name, key=None, parent=None, is_deleted=False, **kwargs):
        """
        Creates a new catalog
        """

        # 通过其他手段获取parent
        if parent is None and kwargs.get("parent_key"):
            parent = cls.objects.get(key=kwargs.get("parent_key"))

        project_key = kwargs.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        # 自动生成key
        if key is None:
            key = get_random_key(name)

        new_catalog, _ = cls._objects.get_or_create(
            defaults={
                "name": name,
                "parent": parent,
            },
            **{"key": key, "is_deleted": is_deleted, "project_key": project_key}
        )

        return new_catalog

    # ============================================== openapi =============================================
    @classmethod
    def open_api_subtree(cls, node, catalogs=None):
        """获取以node为根的子树"""

        node_children = (
            node.get_children().filter(is_deleted=False).order_by("-create_at")
        )

        if catalogs:
            node_children = node_children.filter(id__in=catalogs).order_by("-create_at")

        children = [node.open_api_subtree(child) for child in node_children]

        data = {
            "id": node.id,
            "key": node.key,
            "name": node.name,
            "level": node.level,
            "desc": node.desc,
            "children": children,
        }

        return data

    @classmethod
    def open_api_tree_data(
        cls, service_key=None, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        """
        服务目录树
        根据服务编码过滤服务目录
        """

        catalog_services = CatalogService.objects.filter(project_key=project_key).all()
        if service_key:
            catalog_services = CatalogService.objects.filter(
                service__key=service_key, project_key=project_key
            )

        catalogs = set()
        for cs in catalog_services:
            for parent in cs.catalog.get_ancestors():
                catalogs.add(parent.id)
            catalogs.add(cs.catalog.id)

        # 目录中没有服务编码相关的服务
        if service_key and not catalogs:
            return []

        roots = cls.objects.filter(level=0, is_deleted=False)
        if catalogs:
            roots = roots.filter(id__in=catalogs)

        roots = roots.order_by("lft", "id")

        tree = [cls.open_api_subtree(root, catalogs) for root in roots]

        return tree


class CatalogService(Model):
    """服务关联目录"""

    catalog = models.ForeignKey(
        "ServiceCatalog", help_text=_("关联服务目录"), on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        "Service", help_text=_("关联服务条目"), on_delete=models.CASCADE
    )
    order = models.IntegerField("service序列", default=FIRST_ORDER)
    auth_resource = {}
    resource_operations = []

    objects = managers.CatalogServiceManager()

    class Meta:
        app_label = "service"
        verbose_name = _("服务分类表")
        verbose_name_plural = _("服务分类表")

    @classmethod
    def is_service_bound(cls, service):
        """服务是否被绑定到目录"""
        return cls.objects.filter(service=service).exists()

    @classmethod
    def bounded_catalogs(cls, service):
        """服务绑定了目录"""
        return [cs.catalog.name for cs in cls.objects.filter(service=service)]

    @classmethod
    def bounded_relations(cls, service):
        """服务绑定了目录"""
        return [
            {
                "bond_id": cs.id,
                "catalog_id": cs.catalog.id,
                "catalog_name": cs.catalog.name,
            }
            for cs in cls.objects.filter(service=service)
        ]

    @classmethod
    def bind_service_to_catalog(
        cls, service_id, catalog_id, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        """绑定服务到目录上，目录已被占用，则返回False"""
        # 目录没有改变
        if cls.objects.filter(service_id=service_id, catalog_id=catalog_id).exists():
            return {"result": True, "message": "目录没有改变，无需重复绑定"}

        # 解除服务和其他目录的绑定
        cls.objects.filter(service_id=service_id).delete()
        obj, created = cls.objects.update_or_create(
            service_id=service_id, catalog_id=catalog_id, project_key=project_key
        )

        return {"result": True, "created": created, "message": "目录绑定成功"}


class SysDict(ObjectManagerMixin, Model):
    """系统数据字典"""

    key = models.CharField(_("编码"), max_length=LEN_LONG)
    name = models.CharField(_("名称"), max_length=LEN_LONG)
    desc = models.CharField(
        _("描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    owners = models.CharField(_("负责人"), max_length=LEN_XX_LONG, default=EMPTY_STRING)
    is_enabled = models.BooleanField(_("是否启用"), default=True)
    is_readonly = models.BooleanField(_("是否只读"), default=False)
    is_show = models.BooleanField(
        _("是否显示"), default=True
    )  # 应用场景: 部分系统内置数据字典, 不在数据字段管理页面显示
    objects = managers.SysDictManager()

    auth_resource = {"resource_type": "flow_element", "resource_name": _("流程元素")}
    resource_operations = ["flow_element_manage"]

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "service"
        verbose_name = _("数据字典")
        verbose_name_plural = _("数据字典")

    def delete(self, *args, **kwargs):
        from itsm.workflow.models import Field

        field_values = Field.objects.filter(
            is_deleted=False, source_uri=self.key
        ).values_list("workflow__name", "state__name", "name")
        if field_values.exists():
            raise DeleteError(
                _("以下流程模板中正在使用该字典，请先删除：{}").format(
                    ",".join(["->".join(field) for field in field_values])
                )
            )

        self.dict_data.all().update(is_deleted=True)

        super(SysDict, self).delete(*args, **kwargs)

    @classmethod
    def sets_data(cls, key=""):
        """字典数据的集合视图"""

        data = SysDict.objects.get(key=key).dict_data.filter(is_deleted=False)

        return {item.key for item in data}

    @classmethod
    def list_data(cls, key="", fields=None):
        """字典数据的列表视图
        :param fields: 显示字段, 默认为["id", "key", "name"]
        """
        fields = ["id", "key", "name"] if fields is None else fields

        dict_datas = (
            SysDict.objects.get(key=key)
            .dict_data.filter(is_deleted=False)
            .order_by("order")
        )

        if key == "PRIORITY":
            return [
                dict(
                    [
                        (field, getattr(dict_data, field))
                        for field in fields
                        if hasattr(dict_data, field)
                    ]
                )
                for dict_data in dict_datas
                if dict_data.key in ["1", "2", "3"]
            ]

        return [
            dict(
                [
                    (field, getattr(dict_data, field))
                    for field in fields
                    if hasattr(dict_data, field)
                ]
            )
            for dict_data in dict_datas
        ]

    @classmethod
    def tree_data(cls, key=""):
        """字典数据的树状视图"""

        roots = SysDict.objects.get(key=key).dict_data.filter(level=0, is_deleted=False)
        roots = roots.order_by("lft", "id")
        tree = [DictData.subtree(root) for root in roots]
        for sub_tree in tree:
            fill_tree_route(sub_tree)
        return tree

    @classmethod
    def get_data_by_key(cls, key, view_type="list"):
        """根据字典表编码获取字典数据（支持列表视图和树状视图）"""
        try:
            if view_type == "tree":
                return cls.tree_data(key)
            elif view_type == "sets":
                return cls.sets_data(key)
            else:
                return cls.list_data(key)
        except SysDict.DoesNotExist:
            raise ParamError(_("数据字典不存在，请检查字典编码: %s") % key)


class DictData(BaseMpttModel):
    """字典数据"""

    dict_table = models.ForeignKey(
        to=SysDict,
        related_name="dict_data",
        help_text=_("关联字典项"),
        on_delete=models.CASCADE,
    )
    key = models.CharField(_("编码"), max_length=LEN_LONG)
    name = models.CharField(_("名称"), max_length=LEN_LONG)
    order = models.IntegerField(_("顺序"), default=EMPTY_INT)
    is_readonly = models.BooleanField(_("是否只读（不可编辑）"), default=False)
    is_builtin = models.BooleanField(_("是否内置（不可删除）"), default=False)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("上级目录"),
        null=True,
        blank=True,
        related_name="children",
    )

    auth_resource = {"resource_type": "flow_element", "resource_name": _("流程元素")}
    resource_operations = ["flow_element_manage"]

    def __unicode__(self):
        return "{}({})".format(self.name, self.key)

    def delete(self, *args, **kwargs):
        if (
            not self.is_leaf_node()
            and self.get_children().filter(is_deleted=False).count() > 0
        ):
            raise DeleteError(_("请先删除【{}】下的子数据项").format(self.name))

        super(DictData, self).delete(*args, **kwargs)

    class Meta:
        ordering = ("order",)
        unique_together = ("dict_table", "key")
        app_label = "service"
        verbose_name = _("字典数据")
        verbose_name_plural = _("字典数据")

    class MPTTMeta:
        parent_attr = "parent"
        order_insertion_by = ["name"]

    @cached_property
    def parent_name(self):
        """用箭头连接的父级的名称"""
        return "->".join([c.name for c in self.get_ancestors()])

    @cached_property
    def parent_key(self):
        """父级的key"""
        return self.parent.key

    @classmethod
    @transaction.atomic
    def create_item(
        cls,
        dict_table,
        key,
        name,
        order=0,
        parent=None,
        is_deleted=False,
        is_readonly=False,
        is_builtin=False,
    ):
        """
        Create a new dict data item
        """

        new_item, _ = cls._objects.get_or_create(
            defaults={
                "creator": "system",
                "updated_by": "system",
                "name": name,
                "order": order,
                "parent": parent,
                "is_deleted": is_deleted,
                "is_readonly": is_readonly,
                "is_builtin": is_builtin,
            },
            **{
                "key": key,
                "dict_table": dict_table,
            }
        )

        return new_item

    @classmethod
    def create_builtin_dicts_data(cls, dict_table, data_dict):
        """字典数据转换为表记录"""

        objs = []
        for k, v in six.iteritems(data_dict):
            obj = cls.create_item(dict_table, key=k, name=v, is_builtin=True)
            objs.append(obj)

        return objs

    @classmethod
    def create_builtin_dicts_ordered_data(cls, dict_table, data_list):
        """字典数据转换为表记录"""

        objs = []
        for k, v, o in data_list:
            obj = cls.create_item(dict_table, key=k, name=v, order=o, is_builtin=True)
            objs.append(obj)

        return objs

    @staticmethod
    def subtree(node):
        """获取以node为根的子树"""

        # 获取直接子级
        node_children = node.get_children().filter(is_deleted=False)

        # 递归查询，sql查询次数过多 TODO
        children = [node.subtree(child) for child in node_children]

        return {
            "id": node.id,
            "key": node.key,
            "name": node.name,
            "level": node.level,
            "parent_id": getattr(node.parent, "id", None),
            "parent_key": getattr(node.parent, "key", ""),
            "children": children,
        }

    @classmethod
    def active_dict_data(cls, keys, dict_table):
        """批量激活字典"""

        for key in keys:
            cls._objects.update_or_create(
                defaults={"is_deleted": False}, key=key, dict_table=dict_table
            )


# deprecated models
class ServiceProperty(Model):
    """
    服务公共属性
    相当于数据库中的表 - Table
    """

    service_category = models.ForeignKey(
        ServiceCategory,
        help_text=_("关联服务类别"),
        related_name="properties",
        on_delete=models.CASCADE,
    )
    key = models.CharField(_("默认为名称拼音，唯一存在，如果有一样的，则通过拼音+随机字符匹配"), max_length=LEN_SHORT)
    pk_key = models.CharField(_("fields中的主键的key"), max_length=LEN_SHORT, default="")
    cascade_key = models.CharField(
        _("fields中的级联外键的key"), max_length=LEN_SHORT, default=""
    )
    is_cascade = models.BooleanField(_("判断是否为级联属性"), default=False)
    name = models.CharField(_("服务属性名称"), default="", max_length=LEN_LONG)
    desc = models.CharField(_("属性描述"), max_length=LEN_LONG)
    fields = jsonfield.JSONField(
        _("属性包含的字段"), default=EMPTY_LIST, null=True, blank=True
    )

    class Meta:
        app_label = "service"
        verbose_name = _("服务属性")
        verbose_name_plural = _("服务属性")

    def __unicode__(self):
        return "{}({})".format(self.name, self.key)

    @property
    def allowed_fields(self):
        return [field["key"] for field in self.fields]

    def get_pk_from_fields(self):
        """从fields中获取主键的key"""
        for field in self.fields:
            if field.get("pk", False):
                return field["key"]

        return ""

    def get_depend_on_from_fields(self):
        """从fields中获取外键的"""
        for field in self.fields:
            if field.get("depend_on") == self.key:
                return field["key"]

        return ""

    def to_internal_value(self, is_update=False, data=None):
        """表单数据转换及参数过滤
        返回数据格式：
        validate_data = {
            'pk_value': u'',
            'data': {u'desc': u'',
                     u'name': u'',
                     u'parent_key': u'',
                     u'level': 2},
            'updated_by': u'admin'
        }
        """

        if data is None:
            data = {}
        validate_data = {}

        # 属性过滤，以记录中的fields为准
        for field in self.fields:
            if field["key"] not in data:
                continue
            validate_data[field["key"]] = data[field["key"]]

        validate_data = {"data": validate_data}

        # 创建后不允许更新主键的key
        if not is_update:
            validate_data.update(key=get_random_key(validate_data["data"][self.pk_key]))

        pk_value = data.get(self.pk_key)
        # 从data中获取服务属性名称
        if pk_value:
            validate_data.update(pk_value=pk_value)

        return validate_data


class PropertyRecord(Model):
    """
    服务公共属性记录
    相当于数据库表记录 - Records
    """

    display_role_choice = (("all", _("全部")), ("xt", _("协同办公")))
    service_property = models.ForeignKey(
        ServiceProperty,
        help_text=_("关联服务属性"),
        related_name="records",
        on_delete=models.CASCADE,
    )
    key = models.CharField(_("对应的唯一属性key"), max_length=LEN_LONG)
    pk_value = models.CharField(
        _("对应的主键名，为属性设置的主键信息"),
        max_length=LEN_NORMAL,
        default=EMPTY_STRING,
        null=True,
        blank=True,
    )
    flows = jsonfield.JSONField(
        _("关联了对应属性的workflow的id集合"), default=EMPTY_LIST, null=True, blank=True
    )
    # 记录中tickets长度大于4G(longtext)时会触发问题
    tickets = jsonfield.JSONField(
        _("关联了对应属性的ticket的id集合"), default=EMPTY_LIST, null=True, blank=True
    )
    data = jsonfield.JSONField(_("对应属性字段的值"), null=True, blank=True)
    display_role = MultiSelectField(
        _("可展示的用户"), default=["all"], max_length=LEN_NORMAL, choices=display_role_choice
    )

    # objects = managers.Manager()

    class Meta:
        app_label = "service"
        verbose_name = _("服务属性记录")
        verbose_name_plural = _("服务属性记录")
        ordering = ("-id",)

    def __unicode__(self):
        return self.key

    def get_parent_info(self):
        """获取上一级级联信息"""

        if not self.service_property.is_cascade:
            return []

        for field in self.service_property.fields:
            if field.get("depend_on") == self.service_property.key:
                parent_key = field["key"]
                break
        else:
            return []

        return self.get_parents(parent_key, parent_info=[])

    def get_parents(self, parent_key, parent_info=None):
        """递归查询父级属性，返回列表：[子级<-父级1<-父级1的父级...]"""

        if parent_info is None:
            parent_info = []

        try:
            record = self.service_property.records.get(key=self.data.get(parent_key))
        except PropertyRecord.DoesNotExist:
            return parent_info

        parent_info.append({"key": record.key, "pk_value": record.pk_value})

        record.get_parents(parent_key, parent_info)

        return parent_info

    def get_children(self):
        """获取所有子孙节点"""

        children = []
        for child in self.service_property.records.filter(is_deleted=False):
            # 拿到该记录的所有父记录
            child_parents = [item["key"] for item in child.get_parent_info()]

            # 如果我是你的老子或者我是你老子的老子，那么你就是我的孩子
            if self.key in child_parents:
                children.append(child)

        return children

    @property
    def name(self):
        return self.pk_value
