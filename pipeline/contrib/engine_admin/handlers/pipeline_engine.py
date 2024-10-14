# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from pipeline.service import task_service
from .base import ActionRequestHandler, HandlerType


class PipelineEngineRequestHandler(ActionRequestHandler):
    handler_type = HandlerType.PIPELINE_ENGINE

    def task_pause(self):
        return task_service.pause_pipeline(pipeline_id=self.instance_id)

    def task_resume(self, **kwargs):
        return task_service.resume_pipeline(pipeline_id=self.instance_id)

    def task_revoke(self, **kwargs):
        return task_service.revoke_pipeline(pipeline_id=self.instance_id)

    def node_retry(self, **kwargs):
        return task_service.retry_activity(act_id=self.instance_id, inputs=kwargs.get("inputs"))

    def node_skip(self, **kwargs):
        return task_service.skip_activity(act_id=self.instance_id)

    def node_callback(self, **kwargs):
        return task_service.callback(act_id=self.instance_id, data=kwargs.get("data"))

    def node_skip_exg(self, **kwargs):
        return task_service.skip_exclusive_gateway(gateway_id=self.instance_id, flow_id=kwargs["flow_id"])

    def node_skip_cpg(self, **kwargs):
        return task_service.skip_conditional_parallel_gateway(
            gateway_id=self.instance_id, flow_ids=kwargs["flow_ids"], converge_gateway_id=kwargs["converge_gateway_id"]
        )

    def node_forced_fail(self, **kwargs):
        return task_service.forced_fail(
            act_id=self.instance_id, ex_data=f"force fail by {kwargs.get('operator', 'engine_admin')}"
        )
