# -*- coding: utf-8 -*-
import traceback
from functools import wraps

from rest_framework.response import Response
from django.utils.translation import gettext as _

from common.log import logger
from itsm.component.drf.exception import ValidationError
from itsm.component.exceptions import (
    TicketNotFoundError,
    ServerError,
    ParamError,
    OperateTicketError,
    ServiceNotExist,
)
from itsm.component.utils.drf import format_validation_message
from itsm.service.models import Service
from itsm.ticket.models import Ticket


# ---------------------------------------------------------------------------
# H5 安全修复：OpenAPI 接口防"伪造 operator"横向越权
#
# 历史问题：openapi/ticket/views.py 中存在大量
#     operator = request.data.get("operator")
#     # 或
#     operator = request.data.get("username") or request.data.get("operator")
# 直接信任请求体里的"操作人"字段，并把它当作真实身份去做 approve / operate_node /
# operate_ticket / proceed_approval / withdraw / suspend / unsuspend 等关键动作。
# 一旦上层 JWT 校验被绕过（例如 BK_APIGW_REQUIRE_EXEMPT=1、RUN_VER==ieod 短路），
# 任何调用方都可冒充任意人完成审批/终止/挂起。
#
# 本辅助函数提供"可信 operator"的统一解析策略：
#   1) 如果 request.jwt 合法且 jwt.user.username 存在 ——
#      认定 jwt.user.username 才是可信操作人。若 claimed_operator 与之不一致，
#      记录告警并以 jwt.user.username 为准（防止冒充）。
#   2) 否则（开发/测试环境豁免、或仅 app 级 JWT 无用户态）——
#      回退到 claimed_operator，由调用点继续做处理人/创建人业务校验，
#      不在装饰器层做强制拒绝，避免破坏现有 dev/ieod 部署形态。
# ---------------------------------------------------------------------------
def resolve_trusted_operator(request, claimed_operator):
    """解析"可信操作人"。

    :param request: DRF Request
    :param claimed_operator: 客户端在 body 中声明的操作人（可能为 None/空串）
    :return: 真正用于业务逻辑的 operator 字符串
    """
    jwt_obj = getattr(request, "jwt", None)
    if jwt_obj is None or not getattr(jwt_obj, "is_valid", False):
        # JWT 校验未生效（开发/豁免/ieod 模式）：直接使用调用方声明值，
        # 业务侧仍需通过 can_sign_state_operate / can_operate 等做兜底校验。
        return claimed_operator

    jwt_user = getattr(jwt_obj, "user", None)
    jwt_username = getattr(jwt_user, "username", None) if jwt_user else None
    if not jwt_username:
        # 仅 app 级身份（如网关蓝图），无具体用户态，回退给业务层校验。
        return claimed_operator

    if claimed_operator and claimed_operator != jwt_username:
        # 检测到调用方尝试以"非自身身份"做操作 —— 记录审计日志，但仍以 JWT 为准，
        # 以"静默纠正 + 留痕"的方式防御冒充，避免直接 4xx 让攻击者快速试探。
        logger.warning(
            "openapi: claimed operator(%s) mismatch jwt user(%s), force jwt user",
            claimed_operator,
            jwt_username,
        )
    return jwt_username


def catch_openapi_exception(view_func):
    """单据处理接口的公共异常捕捉"""

    @wraps(view_func)
    def __wrapper(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": TicketNotFoundError.ERROR_CODE_INT,
                    "data": None,
                    "message": TicketNotFoundError.MESSAGE,
                }
            )
        except Service.DoesNotExist:
            return Response(
                {
                    "result": False,
                    "code": ServiceNotExist.ERROR_CODE_INT,
                    "data": None,
                    "message": ServiceNotExist.MESSAGE,
                }
            )
        except ServerError as e:
            # 捕捉drf序列化检验的自定义错误
            return Response(
                {
                    "result": False,
                    "code": e.code_int,
                    "data": None,
                    "message": e.message,
                }
            )
        except ValidationError as e:
            # 捕捉drf序列化检验原始错误
            return Response(
                {
                    "result": False,
                    "code": ParamError.ERROR_CODE_INT,
                    "data": None,
                    "message": format_validation_message(e),
                }
            )
        except Exception:
            # 完整堆栈仅进入服务端日志，避免上游异常详情（含文件路径/
            # SQL 错误/KeyError 键名等）随响应身变为可被调用方获取的信息。
            logger.exception("openapi unexpected error")
            return Response(
                {
                    "result": False,
                    "code": OperateTicketError.ERROR_CODE_INT,
                    "data": None,
                    "message": _("接口异常，请检查请求参数后重试"),
                }
            )

    return __wrapper
