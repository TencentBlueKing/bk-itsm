# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

from common.log import logger
from common.template.mako_utils import mako_safety
from common.template.mako_utils.checker import check_mako_template_safety
from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException
from common.template.template import Template as CommonTemplate
from django.utils.translation import gettext as _
from itsm.component.drf.exception import ValidationError
from itsm.component.exceptions import ComponentNotExist, FieldRequiredError
from itsm.trigger.models import Trigger, ActionSchema
from itsm.component.dlls.component import ComponentLibrary


class TriggerValidator:
    def __init__(self, instance=None):
        self.instance = instance
        if self.instance:
            self.source_type = instance.source_type
            self.source_id = instance.source_id

    def __call__(self, value):
        if not self.instance:
            self.source_id = value["source_id"]
            self.source_type = value["source_type"]
        self.name_validate(value)

    def name_validate(self, value):
        """
        名称的唯一性校验
        统一类型统一来源对象的name必须唯一
        """
        trigger_query_set = Trigger.objects.filter(
            name=value["name"], source_type=self.source_type, source_id=self.source_id
        )
        if self.instance and trigger_query_set.exclude(id=self.instance.id).exists():
            raise ValidationError(_("存在其他相同名称的触发器，请修改后再提交"))

        if not self.instance and trigger_query_set.exists():
            raise ValidationError(_("存在其他相同名称的触发器，请修改后再提交"))


class BulkTriggerRuleValidator:
    def __call__(self, rules):
        self.name_validate(rules)
        self.action_schemas_exist_validate(rules)

    @staticmethod
    def name_validate(rules):
        """
        名称的唯一性校验
        同一个触发器下面如果名称不为空，则不允许相同
        """
        all_name = [rule["name"] for rule in rules if rule.get("name")]
        if len(set(all_name)) < len(all_name):
            raise ValidationError(_("同一个触发器下的规则名称不能重复"))

    @staticmethod
    def action_schemas_exist_validate(rules):
        for index, rule in enumerate(rules):
            action_schemas = rule["action_schemas"]
            if ActionSchema.objects.filter(id__in=action_schemas).count() < len(
                action_schemas
            ):
                raise ValidationError(
                    _("第{}个规则下的响应事件部分不存在").format(index + 1)
                )


class ActionSchemaValidator:
    """
    响应事件配置的
    """

    def __init__(self, instance=None):
        self.instance = instance

    def __call__(self, value):
        self.component_validate(value)
        self.template_validate(value.get("params", []))

    @staticmethod
    def _iter_all_string_values(params):
        """递归收集 params 中**所有字符串值**。

        历史实现仅扫描 ref_type=='import' 字段；攻击者可把 payload 放进 custom 等普通字段，
        运行时 _render_string 仍会无差别渲染。这里改为对所有字符串字段统一抽取模板片段后再检查。
        """
        if isinstance(params, str):
            yield params
            return
        if isinstance(params, list):
            for item in params:
                for value in ActionSchemaValidator._iter_all_string_values(item):
                    yield value
            return
        if isinstance(params, dict):
            for item in params.values():
                for value in ActionSchemaValidator._iter_all_string_values(item):
                    yield value

    def component_validate(self, value):
        try:
            component_class = ComponentLibrary.get_component_class(
                "trigger", component_code=value["component_type"]
            )
            form_class = getattr(component_class, "form_class", None)
            if form_class is None:
                return
            form_class(value.get("params", []), {}).validate_params()
        except ComponentNotExist:
            raise ValidationError("非法的组件类型,请确认组件是否选择正确")
        except FieldRequiredError as error:
            raise ValidationError(str(error))
        except BaseException as error:
            logger.exception(
                "校验错误，instance id {}".format(
                    self.instance.id if self.instance else "None"
                )
            )
            raise ValidationError("组件异常错误：{}".format(str(error)))

    def template_validate(self, params):
        for template_value in self._iter_all_string_values(params):
            for template in CommonTemplate(template_value).get_templates():
                try:
                    check_mako_template_safety(
                        template,
                        mako_safety.SingleLineNodeVisitor(),
                        mako_safety.SingleLinCodeExtractor(),
                    )
                except ForbiddenMakoTemplateException as error:
                    raise ValidationError(
                        _("参数模板存在非法表达式: {} ").format(str(error))
                    )
                except BaseException as error:
                    logger.exception(
                        "模板校验错误，instance id {}".format(
                            self.instance.id if self.instance else "None"
                        )
                    )
                    raise ValidationError(
                        _("参数模板校验失败: {} ").format(str(error))
                    )
