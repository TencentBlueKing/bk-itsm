import logging
import time
from typing import Any, Dict, Optional, List, Union

import requests
from pydantic import BaseModel, Field
from requests.exceptions import HTTPError, ReadTimeout
from django.conf import settings

from itsm.component.exceptions import RemoteCallError

logger = logging.getLogger(__name__)


class Monitor:
    """
    Monitor API 基类
    """
    
    TIMEOUT = 60
    
    # 代理配置
    proxy_ip = settings.MONITOR_PROXY_IP
    proxy_port = settings.MONITOR_PROXY_PORT
    
    # 子类需要重写的属性
    action = ""  # API路径后缀
    method = "POST"  # 请求方法，默认POST

    monitor_data_id = settings.MONITOR_EVENT_DATA_ID
    monitor_event_token = settings.MONITOR_EVENT_TOKEN
    
    def __init__(self):
        self.method = self.method.upper()
        self.session = requests.session()
    
    @property
    def base_url(self):
        """基础URL"""
        return f"http://{self.proxy_ip}:{self.proxy_port}"
    
    @property
    def module_name(self):
        return "monitor"
    
    @property
    def label(self):
        return self.__doc__ or ""
    
    def get_request_url(self, request_data=None):
        """
        获取完整的请求URL
        子类可以重写此方法以自定义URL生成规则
        """
        url = self.base_url.rstrip("/") + "/" + self.action.lstrip("/")
        if request_data:
            url = url.format(**request_data)
        return url
    
    def __call__(self, request_data=None, **kwargs):
        """
        调用入口，支持字典或关键字参数
        """
        if request_data is None:
            request_data = {}
        request_data.update(kwargs)
        return self.perform_request(request_data)
    
    def perform_request(self, request_data):
        """
        发起HTTP请求
        """
        if (not self.monitor_data_id or not self.monitor_event_token or 
            not self.proxy_ip or not self.proxy_port):
            logger.warning(f"【{self.module_name}】请求错误："
                           f"缺少monitor_data_id/monitor_event_token/proxy_ip/proxy_port")
            return False
        request_url = self.get_request_url(request_data)
        
        try:
            if self.method == "GET":
                result = self.session.get(
                    url=request_url, 
                    params=request_data, 
                    verify=False, 
                    timeout=self.TIMEOUT
                )
            else:
                result = self.session.post(
                    url=request_url,
                    verify=False,
                    timeout=self.TIMEOUT,
                    json=request_data,
                )
        except ReadTimeout:
            raise RemoteCallError(f"{request_url}接口返回结果超时")
        except Exception as e:
            logger.exception(f"【模块：{self.module_name}】请求错误：{e}，请求url: {request_url}")
            raise RemoteCallError(f"{request_url} 调用失败: {str(e)}")
        
        try:
            result.raise_for_status()
        except HTTPError as e:
            logger.exception(f"【模块：{self.module_name}】请求错误：{e}，请求url: {request_url}")
            raise RemoteCallError(f"{request_url} 调用失败: {str(e.response.content)}")
        
        result_json = result.json()
        
        if not self.is_result_success(result_json):
            raise RemoteCallError(f"{request_url} 返回结果错误: {result_json}")
        
        return self.handle_response(result_json)
    
    @staticmethod
    def is_result_success(response_data):
        """
        判断请求是否成功，子类可以重写
        """
        return True
    
    @staticmethod
    def handle_response(response_data):
        """
        处理响应数据，子类可以重写
        """
        return response_data.get("data", response_data)
    
    def _build_request_data(self, data: list) -> dict:
        request_data = {
            "data_id": int(self.monitor_data_id),  # 确保是整数类型
            "access_token": self.monitor_event_token,
            "data": data
        }
        return request_data
        

class MonitorEventData(BaseModel):
    """
    监控事件数据模型
    """
    event_name: str = Field(..., description="事件名称，需要在监控平台配置")
    event: Dict[str, Any] = Field(..., description="事件内容，包含具体的事件信息")
    target: str = Field(..., description="目标，通常为IP地址或主机标识")
    dimension: Optional[Dict[str, str]] = Field(default=None, description="维度信息，用于分类和过滤")
    timestamp: Optional[int] = Field(default=None,
                                     description="事件时间戳（毫秒），不传则使用当前时间")

    @classmethod
    def set_default_timestamp(cls, v):
        """如果未提供时间戳，使用当前时间（毫秒）"""
        if v is None:
            return int(time.time() * 1000)
        return v

    def to_dict(self) -> dict:
        """转换为字典，排除None值"""
        return self.model_dump(exclude_none=True)


class PushData(Monitor):
    """
    推送数据到监控平台
    """
    action = "v2/push/"
    method = "POST"

    def __call__(self, data=None, **kwargs):
        if data is None:
            data = []

        if kwargs and not data:
            data = [kwargs]
        elif isinstance(data, dict):
            data = [data]

        request_data = self._build_request_data(data)
        return self.perform_request(request_data)

    @staticmethod
    def _validate_data(data: List[Union[MonitorEventData, dict]]) -> List[dict]:
        """验证数据格式"""
        validated = []
        for item in data:
            if isinstance(item, MonitorEventData):
                validated.append(item.to_dict())
            elif isinstance(item, dict):
                # 使用 Pydantic 模型验证数据格式
                event_data = MonitorEventData(**item)
                validated.append(event_data.to_dict())
            else:
                raise ValueError(f"不支持的数据类型: {type(item)}")
        return validated
