# -*- coding: utf-8 -*-
"""
spec round3 H-α / H-β 鉴权回归。

- ``TicketFieldPermissionValidate``：``api_field_choices`` / ``download_file`` 需沿
  ``obj.ticket`` 反查 ``TicketPermissionValidate``。
- ``TicketPermissionValidate``：``master_or_slave`` / ``get_ticket_output`` /
  ``get_step_process_info`` 不再无脑放行，回落到"可见性"分支。
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase

from itsm.ticket.models import Ticket, TicketField
from itsm.ticket.permissions import (
    TicketFieldPermissionValidate,
    TicketPermissionValidate,
)


def _request(username, method="GET", **query):
    request = MagicMock()
    request.user.username = username
    request.method = method
    request.query_params = query
    request.data = {}
    return request


class TicketFieldPermissionValidateTest(TestCase):
    """spec round3 H-α。"""

    def setUp(self):
        Ticket.objects.all().delete()
        TicketField.objects.all().delete()
        self.alice_ticket = Ticket.objects.create(
            sn="SN-A", title="t1", service_id=1, service_type="request",
            creator="alice", current_status="RUNNING", project_key="public",
        )
        self.alice_field = TicketField.objects.create(
            ticket=self.alice_ticket, key="k1", name="n1", type="STRING",
        )

    @patch(
        "itsm.ticket.permissions.UserRole.is_itsm_superuser",
        return_value=False,
    )
    @patch.object(TicketPermissionValidate, "has_object_permission", return_value=True)
    def test_object_permission_delegates_to_ticket_permission(self, _tpv, _su):
        view = MagicMock()
        view.action = "api_field_choices"
        request = _request("alice")
        self.assertTrue(
            TicketFieldPermissionValidate().has_object_permission(
                request, view, self.alice_field
            )
        )

    @patch(
        "itsm.ticket.permissions.UserRole.is_itsm_superuser",
        return_value=False,
    )
    @patch.object(TicketPermissionValidate, "has_object_permission", return_value=False)
    def test_object_permission_denies_when_ticket_unauthorized(self, _tpv, _su):
        view = MagicMock()
        view.action = "download_file"
        request = _request("eve")
        self.assertFalse(
            TicketFieldPermissionValidate().has_object_permission(
                request, view, self.alice_field
            )
        )

    @patch(
        "itsm.ticket.permissions.UserRole.is_itsm_superuser",
        return_value=False,
    )
    def test_other_actions_remain_forbidden(self, _su):
        view = MagicMock()
        view.action = "list"
        request = _request("alice")
        self.assertFalse(
            TicketFieldPermissionValidate().has_object_permission(
                request, view, self.alice_field
            )
        )

    @patch(
        "itsm.ticket.permissions.UserRole.is_itsm_superuser",
        return_value=True,
    )
    def test_superuser_short_circuits(self, _su):
        view = MagicMock()
        view.action = "list"
        request = _request("admin")
        self.assertTrue(
            TicketFieldPermissionValidate().has_object_permission(
                request, view, self.alice_field
            )
        )


class TicketPermissionValidateWhitelistTest(TestCase):
    """spec round3 H-β：白名单缩小。"""

    def setUp(self):
        Ticket.objects.all().delete()
        self.alice_ticket = Ticket.objects.create(
            sn="SN-A", title="t1", service_id=1, service_type="request",
            creator="alice", current_status="RUNNING", project_key="public",
        )

    @patch(
        "itsm.ticket.permissions.TicketPermissionValidate.iam_ticket_view_auth",
        return_value=False,
    )
    @patch("itsm.ticket.models.Ticket.can_view", return_value=False)
    def test_master_or_slave_falls_back_to_visibility(self, _can_view, _iam):
        view = MagicMock()
        view.action = "master_or_slave"
        request = _request("eve", method="GET")
        self.assertFalse(
            TicketPermissionValidate().has_object_permission(
                request, view, self.alice_ticket
            )
        )

    @patch("itsm.ticket.models.Ticket.can_view", return_value=True)
    def test_master_or_slave_passes_when_visible(self, _can_view):
        view = MagicMock()
        view.action = "master_or_slave"
        request = _request("alice", method="GET")
        self.assertTrue(
            TicketPermissionValidate().has_object_permission(
                request, view, self.alice_ticket
            )
        )

    @patch(
        "itsm.ticket.permissions.TicketPermissionValidate.iam_ticket_view_auth",
        return_value=False,
    )
    @patch("itsm.ticket.models.Ticket.can_view", return_value=False)
    def test_get_ticket_output_falls_back_to_visibility(self, _can_view, _iam):
        view = MagicMock()
        view.action = "get_ticket_output"
        request = _request("eve", method="GET")
        self.assertFalse(
            TicketPermissionValidate().has_object_permission(
                request, view, self.alice_ticket
            )
        )

    @patch(
        "itsm.ticket.permissions.TicketPermissionValidate.iam_ticket_view_auth",
        return_value=False,
    )
    @patch("itsm.ticket.models.Ticket.can_view", return_value=False)
    def test_get_step_process_info_falls_back_to_visibility(self, _can_view, _iam):
        view = MagicMock()
        view.action = "get_step_process_info"
        request = _request("eve", method="GET")
        self.assertFalse(
            TicketPermissionValidate().has_object_permission(
                request, view, self.alice_ticket
            )
        )

    def test_can_exception_distribute_still_whitelisted(self):
        # 视图函数体内自校验管理员身份，权限层维持放行
        view = MagicMock()
        view.action = "can_exception_distribute"
        request = _request("eve", method="GET")
        self.assertTrue(
            TicketPermissionValidate().has_object_permission(
                request, view, self.alice_ticket
            )
        )
