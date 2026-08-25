"""bk-itsm APIGW client base classes."""

from typing import Optional

from django.conf import settings as django_settings

from bkapi_client_core.client import BaseClient
from bkapi_client_core.config import SettingKeys, settings as bkapi_settings
from bkapi_client_core.session import Session
from bkapi_client_core.utils import urljoin


class APIGatewayClient(BaseClient):
    """bk-itsm 对 bkapi_client_core APIGatewayClient 的项目适配"""

    _default_stage = "prod"
    _api_name = ""
    name = "bkapi"
    _stage_by_run_mode = {
        "DEVELOP": "stag",
        "STAGING": "stag",
        "PRODUCT": "prod",
    }

    def get_env(self):
        """根据运行环境和网关返回 APIGW stage。"""
        run_mode = getattr(django_settings, "RUN_MODE", "")
        if self._api_name == "bk-sops" and run_mode in {"DEVELOP", "STAGING"}:
            return "stage"
        return self._stage_by_run_mode.get(run_mode, self._default_stage)

    def __init__(
        self,
        stage: str | None = None,
        endpoint: str = "",
        session: Session | None = None,
    ):
        if stage is None:
            stage = self.get_env()
        self._stage = stage

        endpoint = endpoint or bkapi_settings.get(SettingKeys.BK_API_URL_TMPL, "")
        endpoint = urljoin(endpoint, "/{stage_name}")
        super().__init__(
            endpoint=endpoint,
            session=session,
            name=self._api_name,
        )

    def _get_endpoint(self):
        return self._endpoint.format(api_name=self._api_name, stage_name=self._stage)

    def get_extra_headers(self):
        """子类可重写，返回需要追加到每个请求的额外请求头
        """
        if not getattr(django_settings, "BKPAAS_MULTI_TENANT_MODE", False):
            return {}
        tenant_id = getattr(django_settings, "BKPAAS_APP_TENANT_ID", "")
        if tenant_id:
            return {"X-Bk-Tenant-Id": tenant_id}
        return {}

    def handle_request(self, operation, context):
        """统一请求处理：注入额外请求头后调用基类逻辑。"""
        extra = self.get_extra_headers()
        if extra:
            context = context or {}
            headers = context.setdefault("headers", {})
            headers.update(extra)
        return super().handle_request(operation, context)
