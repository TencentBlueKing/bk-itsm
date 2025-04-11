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

import os
import json
import logging

logger = logging.getLogger(__name__)

from pipeline.conf import settings
from requests.exceptions import HTTPError, ReadTimeout
from itsm.component.apigw.base import APIResource
from itsm.component.exceptions import RemoteCallError, NotAllowedError

CLIENT_URL = settings.DEVOPS_CLIENT_URL


class DevOps(APIResource):
    base_url = settings.DEVOPS_BASE_URL

    # 模块名
    module_name = 'devops'

    @property
    def label(self):
        return self.__doc__

    @property
    def action(self):
        """
        url的后缀，通常是指定特定资源
        """
        raise NotImplementedError

    @property
    def method(self):
        """
        请求方法，仅支持GET或POST
        """
        raise NotImplementedError

    def perform_request(self, request_data):
        """
        发起http请求
        """
        if not request_data.get(settings.BK_CI_COOKIE_NAME, ""):
            return super().perform_request(request_data)

        request_url = self.get_request_url(request_data)
        params = {
            'projectId': request_data.get('project_id', ''),
            'pipelineId': request_data.get('pipeline_id', ''),
            'buildId': request_data.get('build_id', ''),
        }

        try:
            if self.method == "GET":
                headers = {
                    "Content-Type": "application/json",
                    "X-Bkapi-Authorization": json.dumps({
                        "bk_app_code": os.environ.get("BKPAAS_APP_ID", ""),
                        "bk_app_secret": os.environ.get("BKPAAS_APP_SECRET", ""),
                        settings.BK_CI_COOKIE_NAME: request_data.pop(settings.BK_CI_COOKIE_NAME),
                    }),
                    "X-DEVOPS-UID": self.user
                }

                result = self.session.get(url=request_url, params=params, headers=headers,
                                          verify=False,
                                          timeout=self.TIMEOUT)
            else:
                raise NotAllowedError("请求方法不允许")

        except ReadTimeout:
            raise RemoteCallError("{}接口返回结果超时".format(request_url))

        try:
            result.raise_for_status()
        except HTTPError as e:
            logger.exception(
                "【模块：%s】请求APIGW错误：%s，请求url: %s " % (self.module_name, e, request_url))
            raise RemoteCallError("{} 调用失败:{}".format(request_url, str(e.response.content)))

        result_json = result.json()

        if not self.is_result_success(result_json):
            raise RemoteCallError("{} 返回结果错误:{}".format(request_url, result_json))

        response_data = self.handle_response(result_json)

        return response_data

    def is_result_success(self, response_data):
        return response_data["status"] == 0


class ProjectPipelineList(DevOps):
    """
    获取项目流水线列表
    """

    # action = '/v3/apigw-user/projects/{project_id}/pipelines'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/pipelines/pipeline_list'

    method = 'GET'

    def handle_response(self, response_data):
        return response_data["data"]


class ProjectsList(DevOps):
    """
    获取用户项目列表
    """

    # action = '/v3/apigw-user/projects'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/project_list'
    method = 'GET'

    def is_result_success(self, response_data):
        return response_data["code"] == 0


class PipelineBuildStartInfo(DevOps):
    """
    获取流水线启动信息
    """

    # action = '/v3/apigw-user/projects/{project_id}/pipelines/{pipeline_id}/builds/manualStartupInfo'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/build_manual_startup_info'
    method = 'GET'


class ProjectPipelineDetail(DevOps):
    """
    获取流水线详情
    """
    # 获取流水线编排（正确）

    # action = '/v3/apigw-user/projects/{project_id}/pipelines/{pipeline_id}'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/pipelines/pipeline'
    method = 'GET'


class PipelineBuildList(DevOps):
    """
    获取流水线构建历史
    """

    # action = '/apigw-user/builds/{project_id}/{pipeline_id}/history'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/build_histories'
    method = 'GET'


class PipelineBuildStart(DevOps):
    """
    启动流水线
    """

    # action = '/v3/apigw-user/projects/{project_id}/pipelines/{pipeline_id}/builds/start'
    # action='/api/devops/bk-dev/v4/apigw-user/projects/{projectId}/build_start'
    action = '/api/devops/bk-dev/v4/apigw-app/projects/{project_id}/build_start'
    method = 'POST'


class PipelineBuildStatus(DevOps):
    """
    获取流水线构建状态
    """

    # action = '/v3/apigw-user/projects/{project_id}/pipelines/{pipeline_id}/builds/{build_id}/status'
    # action='/api/devops/bk-dev/v4/apigw-user/projects/{projectId}/build_status'
    action = '/api/devops/bk-dev/v4/apigw-app/projects/{project_id}/build_status'
    method = 'GET'

    def handle_response(self, response_data):
        data = response_data.get("data")
        if data:
            variables = {}
            for key, value in data["variables"].items():
                is_builtin = key.startswith(
                    (
                        "BK_CI_",
                        "DEVOPS_GIT",
                        "bk_repo_",
                        "devops_container",
                        "git.",
                        "pipeline.",
                        "project.",
                        "X-DEVOPS-",
                        "codecc_report",
                        "reportCallBack",
                    )
                )
                if not is_builtin:
                    variables[key] = value
            data["variables"] = variables
        return data


class PipelineBuildDetail(DevOps):
    """
    获取流水线构建详情
    """

    # action = '/v3/apigw-user/projects/{project_id}/pipelines/{pipeline_id}/builds/{build_id}/detail'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/build_detail'
    method = 'GET'


class PipelineBuildArtifactoryList(DevOps):
    """
    获取流水线构建产物
    """

    # action = '/v2/apigw-user/artifactories/projects/{project_id}/pipelines/{pipeline_id}/builds/{build_id}/search'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/artifactories/file_info'
    method = 'GET'


class PipelineBuildArtifactoryThirdPartyDownloadUrl(DevOps):
    """
    获取流水线构建产物第三方下载链接
    """

    # action = '/v2/apigw-user/artifactories/projects/{project_id}/thirdPartyDownloadUrl'
    action = '/api/devops/bk-dev/v4/apigw-user/projects/{project_id}/artifactories/user_download_url'
    method = 'GET'


projects_list = ProjectsList()
project_pipeline_list = ProjectPipelineList()
pipeline_build_start_info = PipelineBuildStartInfo()
project_pipeline_detail = ProjectPipelineDetail()
pipeline_build_list = PipelineBuildList()
pipeline_build_start = PipelineBuildStart()
pipeline_build_status = PipelineBuildStatus()
pipeline_build_detail = PipelineBuildDetail()
pipeline_build_artifactory_list = PipelineBuildArtifactoryList()
pipeline_build_artifactory_third_party_download_url = PipelineBuildArtifactoryThirdPartyDownloadUrl()
