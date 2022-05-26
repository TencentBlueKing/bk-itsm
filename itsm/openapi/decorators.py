# -*- coding: utf-8 -*-
import traceback
from functools import wraps

from rest_framework.response import Response
from django.utils.translation import ugettext as _

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
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {
                    "result": False,
                    "code": OperateTicketError.ERROR_CODE_INT,
                    "data": None,
                    "message": _("接口异常，请检查请求参数: {}").format(e),
                }
            )

    return __wrapper
