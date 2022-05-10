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
import os

import jsonfield
import jsonschema
from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import ugettext as _

from common.log import logger
from itsm.component.constants import (
    EMPTY_DICT,
    EMPTY_LIST,
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_X_LONG,
    LEN_XX_LONG,
    ResponseCodeStatus,
    API_PERMISSION_ERROR_CODE,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.db import managers
from itsm.component.drf.mixins import ObjectManagerMixin
from itsm.component.esb.backend_component import bk
from itsm.component.exceptions import DeleteError, ParamError, IamPermissionDenied
from itsm.component.utils.conversion import (
    build_params_by_mako_template,
    params_type_conversion,
)
from itsm.component.utils.misc import find_json_file
from itsm.component.utils.bk_bunch import (  # noqa
    Bunch,
    bunchify,  # noqa
    unbunchify,  # noqa
)  # noqa


class Model(models.Model):
    """基础字段"""

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    objects = managers.Manager()
    _objects = models.Manager()

    auth_resource = {"resource_type": "flow_element", "resource_type_name": "流程元素"}
    resource_operations = ["flow_element_manage"]

    class Meta:
        app_label = "postman"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()


class RemoteSystem(Model):
    """
    第三方系统配置表
    """

    # 基本信息
    system_id = models.IntegerField(_("系统id"), default=0)
    name = models.CharField(_("系统名称"), max_length=LEN_NORMAL, null=False)
    code = models.CharField(_("系统编码"), max_length=LEN_NORMAL, null=False)
    desc = models.CharField(
        _("系统描述"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    owners = models.CharField(
        _("系统责任人"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True
    )
    contact_information = models.TextField(_("联系方式"), blank=True)
    is_builtin = models.BooleanField(_("是否内置系统"), default=False)

    # 公共配置信息
    domain = models.CharField(
        _("系统域名"), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    is_activated = models.BooleanField(_("是否启用"), default=False)
    headers = jsonfield.JSONField(
        _("系统公共头部"), default=EMPTY_LIST, null=True, blank=True
    )
    cookies = jsonfield.JSONField(
        _("系统公共cookies"), default=EMPTY_LIST, null=True, blank=True
    )
    variables = jsonfield.JSONField(
        _("系统变量"), default=EMPTY_LIST, null=True, blank=True
    )
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    class Meta:
        app_label = "postman"
        verbose_name = _("第三方系统配置")
        verbose_name_plural = _("第三方系统配置")

    def __unicode__(self):
        return "{}({})".format(self.name, self.code)

    def data_to_dict(self):
        data = model_to_dict(self)
        data.pop("id")
        data.update(
            headers=data["headers"],
            cookies=data["headers"],
            variables=data["headers"],
        )
        return data

    def delete(self, *args, **kwargs):
        if self.apis.exists():
            raise DeleteError(_("请先删除【{}】下的子数据项").format(self.name))
        if self.is_builtin:
            raise DeleteError(_("内置系统不可删除"))
        super(RemoteSystem, self).delete(*args, **kwargs)

    @classmethod
    def init_default_system(cls):
        file_path = os.path.join(
            settings.PROJECT_ROOT, "initials", "remote", "system", "remote_system.json"
        )
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()

        for sys in json.loads(data):
            if not sys["builtin"]:
                continue
            print("init_default_system: %s" % sys["label"])
            cls.objects.update_or_create(
                code=sys["name"].lower(),
                defaults={
                    "system_id": sys["id"],
                    "name": sys["label"],
                    "desc": "",
                    "is_builtin": True,
                    "is_activated": True,
                    "project_key": PUBLIC_PROJECT_PROJECT_KEY,
                },
            )

        remote_system_data = json.loads(data)
        remote_system_ids = [r["id"] for r in remote_system_data]
        for remote_system in cls.objects.filter(system_id__in=remote_system_ids):
            remote_system.project_key = PUBLIC_PROJECT_PROJECT_KEY
            remote_system.save()

        # 修复旧数据（小写转大写）
        for rs in cls.objects.filter(system_id__gt=0):
            rs.code = rs.code.upper()
            rs.save()


class RemoteApi(ObjectManagerMixin, Model):
    """
    第三方系统API请求配置表
    """

    # 基本信息
    remote_system = models.ForeignKey(
        "postman.RemoteSystem",
        help_text=_("对应的对接系统"),
        related_name="apis",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("API名称"), max_length=LEN_NORMAL, null=False)
    path = models.CharField(_("API路径"), max_length=LEN_X_LONG, null=False)
    version = models.CharField(_("API版本"), max_length=LEN_SHORT, null=True)
    func_name = models.CharField(_("API调用函数"), max_length=LEN_NORMAL, null=False)
    method = models.CharField(
        _("请求方法"),
        max_length=LEN_SHORT,
        choices=[("GET", "GET"), ("POST", "POST")],
        default="GET",
    )
    desc = models.CharField(_("描述"), max_length=LEN_LONG, default="")
    owners = models.CharField(_("负责人"), max_length=LEN_XX_LONG, default=EMPTY_STRING)

    # 参数格式
    req_headers = jsonfield.JSONField(
        _("headers参数"), default=EMPTY_LIST, null=True, blank=True
    )
    req_params = jsonfield.JSONField(
        _("query参数"), default=EMPTY_LIST, null=True, blank=True
    )
    req_body = jsonfield.JSONField(
        _("body参数"), default=EMPTY_DICT, null=True, blank=True
    )
    # 属性提取路径列表：data.attr1.attr2,data.attr1.attr3
    rsp_data = jsonfield.JSONField(
        _("rsp_data"), default=EMPTY_DICT, null=True, blank=True
    )
    before_req = models.TextField(_("request预处理代码"), default=EMPTY_STRING)
    map_code = models.TextField(_("response后处理代码"), default=EMPTY_STRING)
    is_activated = models.BooleanField(_("是否启用"), default=False)
    is_builtin = models.BooleanField(_("是否内置API"), default=False)
    read_only = models.BooleanField(_("只读"), default=False)

    auth_resource = {"resource_type": "public_api", "resource_type_name": "公共api"}
    resource_operations = ["public_api_view", "public_api_manage"]

    class Meta:
        app_label = "postman"
        verbose_name = _("第三方API配置")
        verbose_name_plural = _("第三方API配置")
        ordering = ("-create_at",)

    def __unicode__(self):
        return "{}({})".format(self.name, self.remote_system.name)

    @property
    def remote_system_name(self):
        return self.remote_system.name

    def delete(self, *args, **kwargs):
        if self.is_builtin:
            raise DeleteError(_("内置系统不可删除"))
        super(RemoteApi, self).delete(*args, **kwargs)

    def get_api_config(self, query_params=None, rsp_data=""):
        return {
            "system_code": self.remote_system.code,
            "system_domain": self.remote_system.domain,
            "path": self.path,
            "method": self.method,
            "func_name": getattr(self, "func_name"),
            "version": self.version,
            "rsp_data": rsp_data,
            "map_code": self.map_code,
            "before_req": self.before_req,
            "query_params": query_params or {},
        }

    @classmethod
    def init_default_remote_api(cls):

        apis_path = os.path.join(settings.PROJECT_ROOT, "initials", "remote", "apis")
        file_path = find_json_file(apis_path)
        for file in file_path:
            with open(file, "r") as f:
                data = f.read()
            for api in json.loads(data):
                try:
                    cls.restore_api(api, "system", True)
                except Exception as e:
                    logger.info("创建默认api失败：%s api name %s" % (str(e), api["name"]))

    def tag_data(self):
        """Api数据"""
        data = model_to_dict(
            self, exclude=["id", "req_headers", "req_params", "req_body", "rsp_data"]
        )

        data.update(
            req_headers=self.req_headers,
            req_params=self.req_params,
            req_body=self.req_body,
            rsp_data=self.rsp_data,
            creator="system",
            updated_by="system",
            system_info=self.remote_system.data_to_dict(),
            is_builtin=False,
            read_only=False,
        )

        return data

    @classmethod
    def restore_api(cls, item, operator="system", is_builtin=False):
        """导入Api接口，选择性添加系统"""

        system_info = item.pop("system_info", None)
        common = {"creator": operator, "updated_by": operator, "is_builtin": is_builtin}

        try:
            remote_system = RemoteSystem.objects.get(code=system_info["code"])
        except RemoteSystem.DoesNotExist:

            system_info.update(common)
            system_info.pop("admin", None)
            system_info["project_key"] = PUBLIC_PROJECT_PROJECT_KEY
            remote_system = RemoteSystem.objects.create(**system_info)

        item.update(common)
        item["remote_system"] = remote_system
        item.pop("is_deleted", None)
        if is_builtin:
            api, created = RemoteApi.objects.update_or_create(
                is_builtin=is_builtin, name=item["name"], defaults=item
            )
        else:
            api = RemoteApi.objects.create(**item)
        return api


class RemoteApiInstance(Model):
    """
    接口调用参数实例化
    """

    remote_api = models.ForeignKey(
        "postman.RemoteApi",
        help_text=_("api基础信息"),
        related_name="api_instances",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("配置名称"), max_length=LEN_SHORT, default="")
    desc = models.CharField(_("配置描述"), max_length=LEN_X_LONG, default="", null=True)

    req_params = jsonfield.JSONField(_("query实例化参数"), default=EMPTY_DICT)
    req_body = jsonfield.JSONField(_("body实例化参数"), default=EMPTY_DICT)
    rsp_data = models.CharField(_("返回参数"), max_length=LEN_XX_LONG, default="")
    succeed_conditions = jsonfield.JSONField(_("成功条件"), default=EMPTY_DICT)
    end_conditions = jsonfield.JSONField(
        _("结束条件（api节点可用）"), default=EMPTY_DICT, null=True, blank=True
    )
    need_poll = models.BooleanField(_("是否轮询"), default=False)
    map_code = models.TextField(_("response后处理代码"), default=EMPTY_STRING)
    before_req = models.TextField(_("request预处理代码"), default=EMPTY_STRING)

    remote_api_info = jsonfield.JSONField(_("remote_api_info"), default=EMPTY_DICT)

    class Meta:
        app_label = "postman"
        verbose_name = _("API配置参数实例")
        verbose_name_plural = _("API配置参数实例")

    def __unicode__(self):
        return _("{}配置实例({})").format(self.name, str(self.id))

    @property
    def remote_system_id(self):
        return self.remote_api.remote_system.id

    @classmethod
    def create_default_api_instance(cls, func_name, req_params, req_body, rsp_data):
        return cls.objects.create(
            remote_api=RemoteApi.objects.get(
                read_only=True, is_builtin=True, func_name=func_name
            ),
            req_params=req_params,
            req_body=req_body,
            rsp_data=rsp_data,
        )

    @classmethod
    def get_api_choice_by_instance_id(cls, api_instance_id, kv_relation, params):
        """todo: global context"""

        try:
            api_instance = cls._objects.get(id=api_instance_id)
        except RemoteApiInstance.DoesNotExist:
            raise ParamError(_("对应的api配置不存在，请查询"))

        return api_instance.get_api_choice(kv_relation, params)

    def tag_data(self):
        data = model_to_dict(self, exclude=["id"])
        data.update(
            req_params=data["req_params"],
            req_body=data["req_body"],
            succeed_conditions=data["succeed_conditions"],
            end_conditions=data["end_conditions"],
            remote_api_info=data["remote_api_info"],
        )
        return data

    def get_config(self):
        remote_api = self.remote_api
        return {
            "system_code": remote_api.remote_system.code,
            "system_domain": remote_api.remote_system.domain,
            "path": remote_api.path,
            "method": remote_api.method,
            "func_name": getattr(remote_api, "func_name"),
            "version": remote_api.version,
            "rsp_data": self.rsp_data,
            "map_code": self.map_code,
            "before_req": self.before_req,
            "query_params": self.req_body
            if remote_api.method == "POST"
            else self.req_params,
        }

    def get_api_choice(self, kv_relation, params):
        """
        获取api选项
        :param kv_relation: 返回数据属性关系
        :param params: 请求参数
        """

        api_config = self.get_config()
        result, query_params = build_params_by_mako_template(
            api_config["query_params"], params
        )
        # 构造参数不成功
        if not result:
            return {
                "result": False,
                "code": ResponseCodeStatus.OK,
                "message": query_params,
                "data": [],
            }

        remote_api = self.remote_api
        # 只对post方法进行参数转换和校验
        if remote_api.method == "POST":
            try:
                params_type_conversion(query_params, remote_api.req_body)
                jsonschema.validate(query_params, remote_api.req_body)
            except Exception as e:
                logger.error(
                    "get_api_choice query_params {}, remote_api.req_body {}".format(
                        query_params, remote_api.req_body
                    )
                )
                logger.error("get_api_choice err {}".format(e))
                return {
                    "result": False,
                    "code": ResponseCodeStatus.OK,
                    "message": str(e),
                    "data": [],
                }

        api_config["query_params"] = query_params
        rsp = bk.http(config=api_config)
        if not rsp["result"]:
            if rsp.get("code") == API_PERMISSION_ERROR_CODE:
                raise IamPermissionDenied(
                    data=rsp["permission"],
                    detail=_("用户没有对应的第三方系统接口【%s】权限" % api_config.get("path")),
                )
            return rsp

        rsp_data = rsp["data"].get(api_config["rsp_data"]) or []
        if not kv_relation:
            return {
                "result": True,
                "code": ResponseCodeStatus.OK,
                "message": "success",
                "data": [
                    {"key": index, "name": str(item)}
                    for index, item in enumerate(rsp_data)
                ],
            }

        try:
            data = []
            for item in rsp_data:
                exec(
                    "key = unbunchify(bunchify(item).{key})".format(
                        key=kv_relation["key"]
                    )
                )
                exec(
                    "name = unbunchify(bunchify(item).{name})".format(
                        name=kv_relation["name"]
                    )
                )
                data.append({"key": locals()["key"], "name": locals()["name"]})
            return {
                "result": True,
                "code": ResponseCodeStatus.OK,
                "message": "success",
                "data": data,
            }
        except (KeyError, AttributeError):
            return {
                "result": False,
                "code": ResponseCodeStatus.OK,
                "message": _("所选关键字与返回结果不匹配， 请联系管理员"),
                "data": [],
            }
