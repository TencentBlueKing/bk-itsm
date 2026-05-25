# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
"""

import json

import mock
from django.test import TestCase, override_settings


class WorkflowVersionBatchDeleteAuthzTest(TestCase):
    """spec round2 H-C：WorkflowVersionViewSet.batch_delete 仅 creator/超管可删。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_batch_delete_rejects_non_creator(self, _is_super):
        with mock.patch(
            "itsm.workflow.views.WorkflowVersionViewSet.queryset"
        ) as mock_qs:
            qs = mock.MagicMock()
            qs.exclude.return_value.values_list.return_value = [42]
            mock_qs.filter.return_value = qs

            resp = self.client.post(
                "/api/workflow/versions/batch_delete/",
                data=json.dumps({"id": "42"}),
                content_type="application/json",
            )

            self.assertEqual(resp.status_code, 403)
            qs.delete.assert_not_called()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_batch_delete_allows_creator(self, _is_super):
        with mock.patch(
            "itsm.workflow.views.WorkflowVersionViewSet.queryset"
        ) as mock_qs:
            qs = mock.MagicMock()
            qs.exclude.return_value.values_list.return_value = []
            qs.values_list.return_value = [42]
            mock_qs.filter.return_value = qs

            resp = self.client.post(
                "/api/workflow/versions/batch_delete/",
                data=json.dumps({"id": "42"}),
                content_type="application/json",
            )

            self.assertEqual(resp.status_code, 200)
            qs.delete.assert_called_once()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=True)
    def test_batch_delete_allows_itsm_superuser(self, _is_super):
        with mock.patch(
            "itsm.workflow.views.WorkflowVersionViewSet.queryset"
        ) as mock_qs:
            qs = mock.MagicMock()
            qs.values_list.return_value = [42]
            mock_qs.filter.return_value = qs

            resp = self.client.post(
                "/api/workflow/versions/batch_delete/",
                data=json.dumps({"id": "42"}),
                content_type="application/json",
            )

            self.assertEqual(resp.status_code, 200)
            qs.delete.assert_called_once()
            qs.exclude.assert_not_called()
