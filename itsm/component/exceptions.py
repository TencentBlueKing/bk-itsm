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


from django.utils.translation import ugettext as _
from rest_framework.exceptions import PermissionDenied


class ServerError(Exception):
    """
    后台错误类
    """

    MESSAGE = _("系统异常")
    ERROR_CODE = "FATAL_ERROR"
    ERROR_CODE_INT = 3900000

    def __init__(self, *args):
        self.code = self.ERROR_CODE
        self.code_int = self.ERROR_CODE_INT
        self.message = (
            "%s: %s" % (_(self.MESSAGE), args[0]) if args else _(self.MESSAGE)
        )
        super(ServerError, self).__init__(*args)

    def __str__(self):
        return self.message


class MigrateDataError(ServerError):
    MESSAGE = _("升级失败")
    ERROR_CODE = "Migrate_Data_Error"
    ERROR_CODE_INT = 3900001


class NotAllowedError(ServerError):
    MESSAGE = _("方法不允许")
    ERROR_CODE = "NOT_ALLOWED_ERROR"
    ERROR_CODE_INT = 3900002


class CreateTicketError(ServerError):
    MESSAGE = _("提单失败")
    ERROR_CODE = "CREATE_TICKET_ERROR"
    ERROR_CODE_INT = 3900003


class OperateTicketError(ServerError):
    MESSAGE = _("单据操作失败")
    ERROR_CODE = "OPERATE_TICKET_ERROR"
    ERROR_CODE_INT = 3900004


class ParamError(ServerError):
    MESSAGE = _("参数验证失败")
    ERROR_CODE = "FORM_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900005


class AnnexStoreValidateError(ServerError):
    MESSAGE = _("附件存储")
    ERROR_CODE = "ANNEX_STORE_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900006


class OrganizationStructureFunctionSwitchValidateError(ServerError):
    MESSAGE = _("组织架构功能开关")
    ERROR_CODE = "ORGANIZATION_STRUCTURE_FUNCTION_SWITCH_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900007


class ServiceCatalogValidateError(ServerError):
    MESSAGE = _("服务目录")
    ERROR_CODE = "SERVICE_CATALOG_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900008


class DeleteError(ServerError):
    MESSAGE = _("删除失败")
    ERROR_CODE = "DELETE_ERROR"
    ERROR_CODE_INT = 3900009


class WorkFlowError(ServerError):
    MESSAGE = _("创建流程失败")
    ERROR_CODE = "WORKFLOW_ERROR"
    ERROR_CODE_INT = 3900010


class WorkFlowInvalidError(ServerError):
    MESSAGE = _("流程保存失败")
    ERROR_CODE = "WORKFLOW_INVALID_ERROR"
    ERROR_CODE_INT = 3900011

    def __init__(self, invalid_state_ids, *args):
        self.invalid_state_ids = invalid_state_ids
        super(WorkFlowInvalidError, self).__init__(*args)


class RemoteCallError(ServerError):
    MESSAGE = _("远程服务请求结果异常")
    ERROR_CODE = "REMOTE_CALL_ERROR"
    ERROR_CODE_INT = 3900012


class ComponentCallError(ServerError):
    MESSAGE = _("组件调用异常")
    ERROR_CODE = "COMPONENT_CALL_ERROR"
    ERROR_CODE_INT = 3900014

    def __init__(self, *args):
        """组件错误信息格式化"""
        if args:
            res = args[0]
            self.MESSAGE = "%s:%s(code=%s)" % (
                self.MESSAGE,
                res.get("message"),
                res.get("code"),
            )
            self.esb_message = res.get("message")
            super(ComponentCallError, self).__init__()
        else:
            super(ComponentCallError, self).__init__()


class PermissionError(ServerError):
    MESSAGE = _("权限不足")
    ERROR_CODE = "PERMISSION_ERROR"
    ERROR_CODE_INT = 3900015


class ObjectDoesNotMatchError(ServerError):
    MESSAGE = _("当前对象不匹配查询条件")
    ERROR_CODE = "OBJECT__NOT_MATCH_ERROR"
    ERROR_CODE_INT = 3900016


class StateNotFoundError(ServerError):
    MESSAGE = _("没有找到对应的节点")
    ERROR_CODE = "STATE_NOT_FOUND_ERROR"
    ERROR_CODE_INT = 3900017


class RevokePipelineError(ServerError):
    MESSAGE = _("流程终止失败")
    ERROR_CODE = "REVOKE_PIPELINE_ERROR"
    ERROR_CODE_INT = 3900018


class CallPipelineError(ServerError):
    MESSAGE = _("流程服务调用失败")
    ERROR_CODE = "CALL_PIPELINE_ERROR"
    ERROR_CODE_INT = 3900019


class TransitionError(ServerError):
    MESSAGE = _("添加连接线失败")
    ERROR_CODE = "TRANSITION_ERROR"
    ERROR_CODE_INT = 3900020


class ValidateError(ServerError):
    MESSAGE = _("参数错误")
    ERROR_CODE = "VALIDATE_ERROR"
    ERROR_CODE_INT = 3900021


class TicketNotFoundError(ServerError):
    MESSAGE = _("没有找到对应的单据")
    ERROR_CODE = "TICKET_NOT_FOUND_ERROR"
    ERROR_CODE_INT = 3900022


class SlaTaskError(ServerError):
    MESSAGE = _("SLA任务异常")
    ERROR_CODE = "SLA_TASK_ERROR"
    ERROR_CODE_INT = 3900023


class RpcAPIError(ServerError):
    """
    Shortcut for returning an error response
    """

    MESSAGE = _("RPC的API返回错误")
    ERROR_CODE = "RPC_API_ERROR"
    ERROR_CODE_INT = 3900024


class ComponentNotExist(ServerError):
    MESSAGE = _("组件未找到")
    ERROR_CODE = "COMPONENT_NOT_EXIST"
    ERROR_CODE_INT = 3900025


class ComponentValidateError(ServerError):
    MESSAGE = _("组件参数校验错误")
    ERROR_CODE = "COMPONENT_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900025


class TriggerValidateError(ServerError):
    MESSAGE = _("触发器参数校验错误")
    ERROR_CODE = "TRIGGER_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900026


class ComponentInvokeError(ServerError):
    MESSAGE = _("组件调用错误")
    ERROR_CODE = "COMPONENT_INVOKE_ERROR"
    ERROR_CODE_INT = 3900027


class TaskFlowInitError(ServerError):
    MESSAGE = _("任务流程初始化失败")
    ERROR_CODE = "TASK_FLOW_INIT_ERROR"
    ERROR_CODE_INT = 3900028


class CallTaskPipelineError(ServerError):
    MESSAGE = _("任务服务调用失败")
    ERROR_CODE = "CALL_TASK_PIPELINE_ERROR"
    ERROR_CODE_INT = 3900029


class FieldRequiredError(ServerError):
    MESSAGE = _("必填字段不存在")
    ERROR_CODE = "FIELD_IS_REQUIRED"
    ERROR_CODE_INT = 3900030


class ObjectNotExist(ServerError):
    MESSAGE = _("查找对象不存在")
    ERROR_CODE = "OBJECT_NOT_EXIST"
    ERROR_CODE_INT = 3900404


class Server500Error(ServerError):
    MESSAGE = _("系统异常")
    ERROR_CODE = "SERVER_500_ERROR"
    ERROR_CODE_INT = 3900500


class IamPermissionDenied(PermissionDenied):
    def __init__(self, **kwargs):
        self.data = kwargs.pop("data", [])
        super(IamPermissionDenied, self).__init__(**kwargs)

    MESSAGE = _("用户没有对应模块的权限")
    ERROR_CODE = "IAM_PERMISSION_DENIED"
    ERROR_CODE_INT = 3900499


class ChildTicketSwitchValidateError(ServerError):
    MESSAGE = _("母子单功能开关")
    ERROR_CODE = "CHILD_TICKET_FUNCTION_SWITCH_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900031


class TaskSwitchValidateError(ServerError):
    MESSAGE = _("任务功能开关")
    ERROR_CODE = "TASK_FUNCTION_SWITCH_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900032


class TriggerSwitchValidateError(ServerError):
    MESSAGE = _("触发器功能开关")
    ERROR_CODE = "TRIGGER_FUNCTION_SWITCH_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900033


class IamGrantCreatorActionError(ServerError):
    MESSAGE = _("关联创建权限失败")
    ERROR_CODE = "IAM_GRANT_CREATOR_ACTION"
    ERROR_CODE_INT = 3900034


class ServiceInsertError(ServerError):
    MESSAGE = _("创建服务失败")
    ERROR_CODE = "SERVICE_INSERT_ERROR"
    ERROR_CODE_INT = 3900035


class ServicePartialError(ServerError):
    MESSAGE = _("创建服务部分失败")
    ERROR_CODE = "SERVICE_PARTIAL_ERROR"
    ERROR_CODE_INT = 3900036


class CatalogDeleteError(ServerError):
    MESSAGE = _("目录占用中，请先解绑当前目录及子目录下的服务")
    ERROR_CODE = "CATALOG_DELETE_ERROR"
    ERROR_CODE_INT = 3900037


class ResourceTypeNotFound(ServerError):
    MESSAGE = _("相关类型未找到")
    ERROR_CODE = "RESOURCE_TYPE_ERROR"
    ERROR_CODE_INT = 3900038


class ProjectNotFound(ServerError):
    MESSAGE = _("项目未找到")
    ERROR_CODE = "PROJECT_NOT_ERROR"
    ERROR_CODE_INT = 3900039


class NoMigratePermission(ServerError):
    MESSAGE = _("当前没有权限迁移此资源")
    ERROR_CODE = "NO_MIGRATE_PERMISSION"
    ERROR_CODE_INT = 3900040


class ProjectSettingsNotFound(ServerError):
    MESSAGE = _("没有找到对应的配置")
    ERROR_CODE = "PROJECT_SETTINGS_NOT_FOUND"
    ERROR_CODE_INT = 3900041


class ServiceNotExist(ServerError):
    MESSAGE = _("服务未找到")
    ERROR_CODE = "SERVICE_NOT_EXIST"
    ERROR_CODE_INT = 3900042


class TableNotExist(ServerError):
    MESSAGE = _("服务模板未找到")
    ERROR_CODE = "TABLE_NOT_EXIST"
    ERROR_CODE_INT = 3900043


class AuthMigrateError(ServerError):
    MESSAGE = _("权限迁移失败")
    ERROR_CODE = "AUTH_MIGRATE_ERROR"
    ERROR_CODE_INT = 3900044


class SlaParamError(ServerError):
    MESSAGE = _("Sla节点参数验证失败")
    ERROR_CODE = "SLA_VALIDATE_ERROR"
    ERROR_CODE_INT = 3900045


class DeliverOperateError(ServerError):
    MESSAGE = _("转派单异常")
    ERROR_CODE = "DELIVER_OPERATE_ERROR"
    ERROR_CODE_INT = 3900046


class GetCustomApiDataError(ServerError):
    MESSAGE = _("获取自定义数据异常")
    ERROR_CODE = "GET_CUSTOM_API_DATA_ERROR"
    ERROR_CODE_INT = 3900047
