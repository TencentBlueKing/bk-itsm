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

from itertools import chain

import jsonfield
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    BASE_MODEL,
    DEFAULT_STRING,
    EMPTY,
    EMPTY_DICT,
    EMPTY_LIST,
    EMPTY_STRING,
    LAYOUT_CHOICES,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_XX_LONG,
    SHOW_BY_CONDITION,
    SHOW_DIRECTLY,
    SOURCE_CHOICES,
    TYPE_CHOICES,
    VALIDATE_CHOICES,
)
from itsm.component.utils.basic import create_version_number
from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.workflow import managers

from .base import Model
from ...project.models import Project


class BaseField(Model):
    """基础字段
    meta:
      code: approve_result  # 审批结果

    regex_config:
      rule:  # 校验规则
        expressions: [{"condition":"==","key":"key1","source":"field","type":"TEXT","value":"value1"}]  # 表达式
        type: "and"  # 表达式关系，and/or
    """

    is_builtin = models.BooleanField(_("是否是内置字段"), default=False)
    is_readonly = models.BooleanField(_("是否只读"), default=False)
    is_valid = models.BooleanField(_("是否生效"), default=True)
    display = models.BooleanField(_("是否显示在单据列表中"), default=False)

    source_type = models.CharField(_("数据来源类型"), max_length=LEN_SHORT, choices=SOURCE_CHOICES,
                                   default="CUSTOM")
    source_uri = models.CharField(_("接口uri"), max_length=LEN_LONG, default=EMPTY_STRING, null=True,
                                  blank=True)
    api_instance_id = models.IntegerField(_('api实例主键'), default=0, null=True, blank=True)
    kv_relation = jsonfield.JSONCharField(_("源数据的kv关系配置"), default=EMPTY_DICT,
                                          max_length=LEN_NORMAL)
    type = models.CharField(_("字段类型"), max_length=LEN_SHORT, choices=TYPE_CHOICES, default="STRING")

    key = models.CharField(_("字段标识"), max_length=LEN_LONG)
    name = models.CharField(_("字段名"), max_length=LEN_NORMAL)

    layout = models.CharField(_("布局"), max_length=LEN_SHORT, choices=LAYOUT_CHOICES,
                              default="COL_6")

    validate_type = models.CharField(_("校验规则"), max_length=LEN_SHORT, choices=VALIDATE_CHOICES,
                                     default="REQUIRE")

    show_type = models.IntegerField(
        _('显示条件类型'), choices=[(SHOW_DIRECTLY, '直接显示'), (SHOW_BY_CONDITION, '根据条件判断')],
        default=SHOW_DIRECTLY
    )
    show_conditions = jsonfield.JSONField(_("字段的显示条件"), default=EMPTY_DICT)

    regex = models.CharField(_("正则校验规则关键字"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True,
                             blank=True)
    '''
    regex_config.rule: dict 校验规则
    regex_config.rule.expressions: []dict 表达式
    regex_config.rule.type: string 表达式关系，and/or
    {
        "rule": {
            "expressions":[{"condition":"==","key":"key1","source":"field","type":"TEXT","value":"value1"}],
            "type":"and"
        }
    }
    '''
    regex_config = jsonfield.JSONCharField(_('正则校验规则配置'), max_length=LEN_LONG, default=EMPTY_DICT)
    custom_regex = models.CharField(_("自定义正则规则"), max_length=LEN_MIDDLE, default=EMPTY_STRING,
                                    null=True, blank=True)
    desc = models.CharField(_("字段填写说明"), max_length=LEN_MIDDLE, default=EMPTY_STRING, null=True,
                            blank=True)
    tips = models.CharField(_("字段展示说明"), max_length=LEN_MIDDLE, default=EMPTY_STRING, null=True,
                            blank=True)
    is_tips = models.BooleanField(_('额外提示'), default=False)
    default = models.CharField(_("默认值"), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True,
                               blank=True)
    choice = jsonfield.JSONField(_("选项"), default=EMPTY_LIST)
    related_fields = jsonfield.JSONField(_("级联字段"), default=EMPTY_DICT, null=True, blank=True)
    meta = jsonfield.JSONField(_("复杂描述信息"), default=EMPTY_DICT)

    class Meta:
        abstract = True

    @property
    def api_instance(self):
        try:
            return RemoteApiInstance.objects.get(id=self.api_instance_id)
        except RemoteApiInstance.DoesNotExist:
            return None

    def tag_data(self, fields=None, exclude=None):
        """获取field快照数据"""

        opts = self._meta
        data = {}

        _exclude = list(self.FIELDS)
        if exclude:
            _exclude.extend(exclude)

        for f in chain(opts.concrete_fields, opts.private_fields):
            if not getattr(f, 'editable', False):
                continue
            if fields and f.name not in fields:
                continue
            if _exclude and f.name in _exclude:
                continue

            if isinstance(f, models.ForeignKey):
                data['{}_id'.format(f.name)] = getattr(getattr(self, f.name), 'id', '')
            else:
                data[f.name] = getattr(self, f.name, '')

            if self.source_type == 'API':
                api_instance_info = RemoteApiInstance.objects.get(
                    id=self.api_instance_id).tag_data()
                remote_api_info = RemoteApi.objects.get(
                    id=api_instance_info['remote_api']).tag_data()
                data['api_info'] = {
                    'api_instance_info': api_instance_info,
                    'remote_api_info': remote_api_info,
                }

        return data


class Field(BaseField):
    """字段表"""

    SOURCE = [('CUSTOM', '自定义添加'), ('TABLE', '基础模型添加')]

    workflow = models.ForeignKey('workflow.Workflow', help_text=_("关联流程"), related_name="fields",
                                 on_delete=models.CASCADE)
    state = models.ForeignKey('workflow.State', help_text=_("关联流程"), related_name="state_fields",
                              null=True, blank=True, on_delete=models.CASCADE)
    source = models.CharField(_('添加方式'), max_length=LEN_SHORT, choices=SOURCE, default='CUSTOM')

    objects = managers.FieldManager()
    _objects = models.Manager()

    class Meta:
        app_label = 'workflow'
        verbose_name = _("字段表")
        verbose_name_plural = _("字段表")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type)

    def tag_data(self, fields=None, exclude=None):
        """获取流程字段快照数据"""

        data = super(Field, self).tag_data(fields, exclude)
        return data

    def clone(self, key=None):
        self.id = None
        self.save()

        if key:
            self.key = key
            self.save()
        return self


class TemplateField(BaseField):
    """字段库"""

    flow_type = models.CharField(_("流程分类"), max_length=LEN_NORMAL, default=DEFAULT_STRING)
    project_key = models.CharField(_("项目key"), max_length=LEN_SHORT, null=False, default=0)

    objects = managers.TemplateFieldManager()

    auth_resource = {"resource_type": "field", "resource_type_name": "字段"}
    resource_operations = ["field_view", "field_edit", "field_delete"]
    public_field_resource_operations = ["public_field_view", "public_field_edit",
                                        "public_field_delete"]

    need_auth_grant = True

    class Meta:
        app_label = "workflow"
        verbose_name = _("字段库")
        verbose_name_plural = _("字段库")

    def __unicode__(self):
        return "{}({})".format(self.name, self.type)

    def tag_data(self, fields=None, exclude=None):
        """获取公共字段快照数据"""
        data = super(TemplateField, self).tag_data(fields, exclude)
        data.update(flow_type=self.flow_type, source=BASE_MODEL)
        return data

    @property
    def project(self):
        return Project.objects.get(key=self.project_key)


class Table(Model):
    """
    基础模型
    """

    fields = models.ManyToManyField(TemplateField, help_text=_('关联的公共字段'), related_name="tables")
    name = models.CharField(_('模型名称'), max_length=LEN_LONG)
    desc = models.CharField(_('基础模型描述'), max_length=LEN_LONG, null=True, blank=True)
    fields_order = jsonfield.JSONField(_('字段排序'), default=[])

    is_builtin = models.BooleanField(_('是否内置字段'), default=False)

    version = models.CharField(_("Table版本：空"), max_length=LEN_NORMAL, null=True, blank=True,
                               default=EMPTY)

    objects = managers.TableManager()

    class Meta:
        app_label = 'workflow'
        verbose_name = _('基础模型')
        verbose_name_plural = _('基础模型')

    def __unicode__(self):
        return self.name

    def add_fields(self, fields):
        """增加字段"""
        table_fields = list(self.fields.values_list('id', flat=True))
        for field in fields:
            if field not in table_fields:
                table_fields.append(field)
        self.fields = table_fields
        self.save()

    def remove_fields(self, fields):
        """删除字段"""
        table_fields = list(self.fields.values_list('id', flat=True))
        for field in fields:
            try:
                table_fields.remove(field)
            except ValueError:
                pass
        self.fields = table_fields
        self.save()

    def tag_data(self, exclude=None):
        """获取table快照数据"""

        _exclude = list(self.FIELDS) + ['is_builtin', 'fields', 'fields_order']

        if isinstance(exclude, (list, tuple)):
            _exclude.extend(exclude)

        table_fields = TemplateField.objects.filter(id__in=self.fields_order)

        # build field hash
        fields, id_to_key = [], {}
        for tf in table_fields:
            id_to_key[tf.id] = tf.key
            fields.append(tf.tag_data())

        field_key_order = [id_to_key[field_id] for field_id in self.fields_order if
                           field_id in id_to_key]
        data = model_to_dict(self, exclude=_exclude)
        data.update(fields=fields, fields_order=self.fields_order, field_key_order=field_key_order)

        return data

    def clone(self):
        """返回克隆对象"""

        fields = self.fields.values_list('id', flat=True)
        self.id = None
        self.save()

        version_name = create_version_number()
        self.name = '{}_{}'.format(self.name, version_name)
        self.fields = fields
        self.version = version_name
        self.save()

        return self
