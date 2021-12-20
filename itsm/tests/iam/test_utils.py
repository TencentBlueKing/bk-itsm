# -*- coding: utf-8 -*-
import mock
from django.conf import settings
from django.test import TestCase, override_settings

from itsm.auth_iam.utils import (
    IamRequest,
    grant_resource_creator_related_actions,
    grant_instance_creator_related_actions,
)
from itsm.project.models import Project


class TestIamUtils(TestCase):
    request = IamRequest(username="admin")

    def test_generate_apply_url(self):
        self.request._iam._client.get_apply_url = mock.Mock(
            return_value=(True, "", "http")
        )
        data = {
            "system_id": "bk_itsm",
            "system_name": "流程服务",
            "actions": [
                {
                    "id": "project_view",
                    "name": "项目查看",
                    "related_resource_types": [
                        {
                            "system_id": "bk_itsm",
                            "system_name": "流程服务",
                            "type": "project",
                            "type_name": "项目",
                            "instances": [
                                [
                                    {
                                        "type": "project",
                                        "type_name": "项目",
                                        "id": "0",
                                        "name": "默认项目",
                                    }
                                ]
                            ],
                        }
                    ],
                }
            ],
        }
        url = self.request.generate_apply_url(data)
        self.assertEqual(url, "http")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_resource_multi_actions_allowed(self):
        resources = [
            {
                "resource_id": "0",
                "resource_name": "默认项目",
                "resource_type": "project",
                "creator": "admin",
            }
        ]
        actions = ["project_view"]
        settings.ENVIRONMENT = "dev"
        data = self.request.batch_resource_multi_actions_allowed(
            actions=actions, resources=resources
        )
        self.assertIsInstance(data, dict)
        self.assertDictEqual(data["0"], {"project_view": True})

        settings.ENVIRONMENT = "stag"
        self.request._iam.batch_resource_multi_actions_allowed = mock.Mock(
            return_value={"0": {"project_view": False}}
        )
        data = self.request.batch_resource_multi_actions_allowed(
            actions=actions, resources=resources
        )

        self.assertIsInstance(data, dict)
        self.assertDictEqual(data["0"], {"project_view": False})

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_resource_multi_actions_allowed(self):
        resources = [
            {
                "resource_id": "0",
                "resource_name": "默认项目",
                "resource_type": "project",
                "creator": "admin",
            }
        ]
        actions = ["project_view"]
        self.request._iam.resource_multi_actions_allowed = mock.Mock(
            return_value={"0": {"project_view": False}}
        )

        data = self.request.resource_multi_actions_allowed(
            actions=actions, resources=resources
        )
        self.assertIsInstance(data, dict)
        self.assertDictEqual(data["0"], {"project_view": False})

    @mock.patch("iam.api.client.Client.grant_resource_creator_actions")
    def test_grant_resource_creator_related_actions(
        self, patch_grant_resource_creator_actions
    ):
        patch_grant_resource_creator_actions.return_value = (True, "ok")
        grant_resource_creator_related_actions(
            resource_type="project",
            resource_id="0",
            resource_name="默认项目",
            creator="amin",
        )

    @mock.patch("iam.api.client.Client.grant_resource_creator_actions")
    def test_grant_instance_creator_related_actions(
        self, patch_grant_resource_creator_actions
    ):
        patch_grant_resource_creator_actions.return_value = (True, "ok")
        project = Project.objects.get(key="0")
        grant_instance_creator_related_actions(instance=project)
