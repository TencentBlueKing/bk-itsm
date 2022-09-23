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

from multiprocessing.dummy import Pool as ThreadPool

import jsonfield
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import (
    ADMIN_STATICS_MANAGER_KEY,
    ADMIN_SUPERUSER_KEY,
    CACHE_5MIN,
    CACHE_30MIN,
    DEFAULT_BK_BIZ_ID,
    EMPTY_STRING,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_XX_LONG,
    ROLE_CHOICES,
    USER_ROLE_CHOICES,
    PREFIX_KEY,
    WORKFLOW_SUPERUSER_KEY,
    LEN_SHORT,
)
from itsm.component.drf.mixins import ObjectManagerMixin
from itsm.component.db import managers
from itsm.component.esb.esbclient import client_backend
from itsm.component.utils.basic import dotted_name, list_by_separator
from itsm.component.utils.client_backend_query import (
    get_bk_business,
    get_department_users,
    get_user_departments,
    get_user_leader,
)
from itsm.iadmin.contants import ORGANIZATION_KEY, SWITCH_ON
from itsm.iadmin.models import SystemSettings


class Model(models.Model):
    """基础字段"""

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    end_at = models.DateTimeField(_("结束时间"), null=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    _objects = models.Manager()

    class Meta:
        app_label = "role"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()


class RoleType(Model):
    """
    用户角色类型
    """

    name = models.CharField(_("角色名称"), max_length=LEN_NORMAL)
    type = models.CharField(_("角色类型"), max_length=LEN_NORMAL)
    is_processor = models.BooleanField(_("可否操作单据"), default=True)
    is_display = models.BooleanField(_("是否显示"), default=True)
    desc = models.CharField(
        _("角色描述"), max_length=LEN_MIDDLE, default=EMPTY_STRING, null=True, blank=True
    )

    objects = managers.Manager()

    auth_resource = {"resource_type": "system_settings", "resource_type_name": "系统配置"}
    resource_operations = ["system_settings_manage"]

    class Meta:
        app_label = "role"
        verbose_name = _("用户角色类型")
        verbose_name_plural = _("用户角色类型")

    def __unicode__(self):
        return "{}({})".format(self.name, self.pk)

    @classmethod
    def init_builtin_roles(cls, *args, **kwargs):
        for role in ROLE_CHOICES:
            try:
                RoleType.objects.get_or_create(
                    type=role[0],
                    defaults={
                        "name": role[1],
                        "desc": role[1],
                        "is_display": role[2],
                        "is_processor": role[3],
                    },
                )
            except BaseException as error:
                print(
                    "init builtin roles and user roles data role %s error %s"
                    % (role, str(error))
                )

    @classmethod
    def migrate_general_role_type(cls, *args, **kwargs):
        count = RoleType.objects.filter(type="GENERAL").update(name="自定义角色")
        print("migrate_general_role_type[GENERAL] count = {}".format(count))


class UserRole(ObjectManagerMixin, Model):
    """
    用户角色和权限表
    """

    role_type = models.CharField(_("对应角色类型"), max_length=LEN_NORMAL)
    role_key = models.CharField(
        _("角色唯一标识"), max_length=LEN_MIDDLE, default=EMPTY_STRING
    )
    name = models.CharField(_("角色命名"), max_length=LEN_NORMAL)
    members = models.CharField(_("角色组成人员"), max_length=LEN_XX_LONG)
    owners = models.CharField(_("负责人"), max_length=LEN_XX_LONG, default=EMPTY_STRING)
    access = models.CharField(_("对应服务"), max_length=LEN_MIDDLE)
    desc = models.CharField(
        _("用户角色描述"), max_length=LEN_MIDDLE, default=EMPTY_STRING, null=True, blank=True
    )
    is_builtin = models.BooleanField(_("是否内置"), default=False)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    objects = managers.Manager()

    need_auth_grant = True
    auth_resource = {"resource_type": "user_group", "resource_type_name": "用户组"}
    resource_operations = ["user_group_edit", "user_group_delete", "user_group_view"]

    class Meta:
        app_label = "role"
        verbose_name = _("用户角色和权限表")
        verbose_name_plural = _("用户角色和权限表")

    def __unicode__(self):
        return "{}({})".format(self.name, self.pk)

    @classmethod
    def init_builtin_user_roles(cls, *args, **kwargs):
        """用户管理角色初始化"""
        for role in USER_ROLE_CHOICES:
            members = role[4]
            if role[0] == "SUPERUSER":
                members = ",{},".format(",".join(settings.INIT_SUPERUSER))
            try:
                cls.objects.get_or_create(
                    defaults={
                        "desc": role[5],
                        "members": members,
                        "name": role[1],
                        "access": role[3],
                    },
                    **{"role_key": role[0], "role_type": role[2]}
                )
            except BaseException as error:
                print(
                    "init_builtin_user_roles error role %s error %s"
                    % (role, str(error))
                )

    @classmethod
    def has_access(cls, username, access, role_type="ADMIN"):
        return cls.objects.filter(
            role_type=role_type, members__contains=dotted_name(username), access=access
        ).exists()

    @classmethod
    def get_access_by_user(cls, username):
        """查询用户页面权限"""

        access_list = cls.objects.filter(
            members__contains=dotted_name(username), role_type="ADMIN"
        ).values_list("role_key", flat=True)

        return list(access_list)

    @classmethod
    def is_statics_manager(cls, username):
        return cls.objects.filter(
            members__contains=dotted_name(username), role_key=ADMIN_STATICS_MANAGER_KEY
        ).exists()

    @classmethod
    def is_workflow_manager(cls, username):
        """判断是否是流程管理员"""
        return cls.objects.filter(
            members__contains=dotted_name(username), role_key=WORKFLOW_SUPERUSER_KEY
        ).exists()

    @classmethod
    def is_itsm_superuser(cls, username):
        """判断是否itsm超级管理员"""
        return (
            dotted_name(username)
            in cls.objects.get(role_key=ADMIN_SUPERUSER_KEY).members
        )

    @classmethod
    def get_general_role_by_user(cls, username):
        return cls.objects.filter(members__contains=username).values("role_type", "id")

    @classmethod
    def get_cmdb_role_by_user(cls, username):
        """获取用户的cmdb角色
        返回示例：{
            u'secondline': {'bizs': [], 'role_id': 54},
            u'bk_biz_developer': {'bizs': [5], 'role_id': 10},
            u'bk_biz_maintainer': {'bizs': [2, 11], 'role_id': 13},
            u'operator': {'bizs': [2], 'role_id': 11},
        }
        """
        cache_key = "{}cmdb_roles_{}".format(PREFIX_KEY, username)
        cmdb_roles = cache.get(cache_key)
        if cmdb_roles:
            return cmdb_roles

        try:
            cmdb_roles = {
                item["role_key"]: {"role_id": item["id"], "bizs": set()}
                for item in cls.objects.filter(role_type="CMDB").values(
                    "role_key", "id"
                )
            }
            apps = cls.get_app_list_by_user(username, cmdb_roles)

            for app in apps:
                # 用户在哪些业务(bizs)下有哪些角色(key)的权限
                for key, value in list(app.items()):
                    if not (key in cmdb_roles and value):
                        continue
                    if username not in value.split(","):
                        continue
                    cmdb_roles[key]["bizs"].add(app["bk_biz_id"])

            cache.set(cache_key, cmdb_roles, CACHE_5MIN)

            return cmdb_roles
        except Exception as e:
            logger.error("get_cmdb_role_by_user exception: %s" % e)
            return {}

    @staticmethod
    def get_app_list_by_user(username, all_roles):
        """获取用户有权限的业务列表，即：在任何一个角色下存在该用户"""

        def _get_app_list_by_role(params=None):
            if params is None:
                params = {}
            apps = client_backend.cc.search_business(
                {
                    "bk_supplier_id": 0,
                    "fields": params["search_fields"],
                    "condition": {params["role"]: params["username"]},
                    "page": {"start": 0, "limit": 1000, "sort": ""},
                }
            ).get("info")

            return apps

        def _batch_get_apps():
            """多线程并发查询"""

            search_fields = [role for role in all_roles]
            search_fields.extend(["bk_biz_id", "bk_biz_name"])

            args_list = [
                {"role": role, "username": username, "search_fields": search_fields}
                for role in all_roles
            ]

            pool = ThreadPool(20)
            apps_map = pool.map(_get_app_list_by_role, args_list)
            pool.close()
            pool.join()

            return apps_map

        apps = []
        for item in _batch_get_apps():
            apps.extend(item)

        return apps

    @classmethod
    def update_cmdb_common_roles(cls):
        """创建或更新cmdb中业务模型下的通用角色"""

        cache_key = "{}cmdb_roles".format(PREFIX_KEY)
        cmdb_roles = cache.get(cache_key)
        if cmdb_roles is not None:
            return True

        try:
            # 查询通用角色列表
            res = client_backend.cc.search_object_attribute(
                {"bk_obj_id": "biz", "bk_supplier_account": "0"}
            )
            roles = {
                item["bk_property_id"]: item["bk_property_name"]
                for item in res
                if item["bk_property_group"] == "role"
            }

            for role in roles:
                cls.objects.update_or_create(
                    defaults={"name": roles[role]},
                    **{"role_type": "CMDB", "role_key": role}
                )

            cache.set(cache_key, roles, CACHE_5MIN)

            return True

        except Exception as error:
            logger.error("update_cmdb_common_roles error: %s" % error)
            return False

    @classmethod
    def get_users_by_type(cls, bk_biz_id, user_type, users, ticket=None):
        """
        通过角色类型获取人名，返回人名列表
        """

        if user_type in ["GENERAL", "CMDB"]:

            roles = UserRole.objects.filter(role_type=user_type)
            if users:
                role_ids = [role_id for role_id in str(users).split(",") if role_id]
                roles = roles.filter(id__in=role_ids)

            if user_type == "CMDB":
                if bk_biz_id == DEFAULT_BK_BIZ_ID:
                    return []

                cmdb_users = get_bk_business(
                    bk_biz_id, role_type=[role.role_key for role in roles]
                )
                return list_by_separator(cmdb_users)

            if user_type == "GENERAL":
                general_users = ",".join([role.members for role in roles])
                return list_by_separator(general_users)

        if user_type in ["PERSON", "EMPTY", "VARIABLE"] and users:
            return list_by_separator(users)

        if user_type == "STARTER":
            return [ticket.creator] if ticket else []

        if user_type == "ORGANIZATION":
            return get_department_users(users, recursive=True)

        if user_type == "STARTER_LEADER":
            # 获取到当前提单人的leader
            return get_user_leader(users)

        if user_type == "ASSIGN_LEADER":
            if ticket is not None:
                # 获取节点处理人的leader
                status = ticket.node_status.get(state_id=int(users))
                return get_user_leader(status.processed_user)

        if user_type == "IAM":
            iam_roles_dict = {}
            iam_roles = cls.objects.filter(role_type="IAM").values("id", "role_key")
            for role in iam_roles:
                iam_roles_dict[role["id"]] = role["role_key"]
            return [iam_roles_dict[int(user)] for user in users.strip(",").split(",")]

        return []

    @classmethod
    def get_user_roles(cls, username):
        """获取用户的所有角色信息"""
        cache_key = "user_roles_{}".format(username)
        ctx = cache.get(cache_key)
        if not ctx:
            roles = {
                "general": set(
                    [str(role["id"]) for role in cls.get_general_role_by_user(username)]
                )
            }
            bkuser_roles = BKUserRole.get_or_update_user_roles(username)
            roles["cmdb"] = {
                str(role["role_id"]): role["bizs"]
                for role in bkuser_roles["cmdb"].values()
            }
            roles["organization"] = bkuser_roles["organization"]
            cache.set(cache_key, roles, CACHE_30MIN)
        return cache.get(cache_key)

    @classmethod
    def get_role_name(cls, user_type, role_ids):
        roles = UserRole.objects.filter(role_type=user_type, id__in=role_ids).values(
            "id", "name"
        )
        return {str(role["id"]): role["name"] for role in roles}


class BKUserRole(models.Model):
    """记录每一位用户的CMDB角色/Organization角色"""

    roles_dict = {"cmdb": {}, "organization": []}

    username = models.CharField(
        _("蓝鲸用户username"), max_length=LEN_NORMAL, default=EMPTY_STRING
    )
    roles = jsonfield.JSONField(_("用户角色"), default=roles_dict, null=True, blank=True)
    uid = models.CharField(
        _("用户uid"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True
    )
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "role"
        verbose_name = _("蓝鲸用户角色表")
        verbose_name_plural = _("蓝鲸用户角色表")

    def __unicode__(self):
        return self.username

    @classmethod
    def get_or_update_user_roles(cls, username):
        """更新个人角色"""

        roles = {
            "cmdb": {},
            "organization": [],
        }
        # 更新cmdb角色
        cmdb_roles = UserRole.get_cmdb_role_by_user(username)
        roles.update(cmdb=cmdb_roles)

        # 更新组织架构角色
        if SystemSettings.objects.get(key=ORGANIZATION_KEY).value == SWITCH_ON:
            departments = get_user_departments(username, id_only=True)
            roles.update(organization=departments)

        BKUserRole.objects.update_or_create(
            username=username, defaults={"roles": roles}
        )

        return roles

    @classmethod
    def get_user_organization(cls, username):
        return cls.get_or_update_user_roles(username)["organization"]
