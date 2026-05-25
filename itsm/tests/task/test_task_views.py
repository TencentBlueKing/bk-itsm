# -*- coding: utf-8 -*-
"""
任务相关接口越权回归测试。

覆盖 spec round2 的修复点：
- C-1 TaskPermissionValidate.has_object_permission：写动作/读动作/proceed 分类；
- C-2 TaskViewSet.set_order：detail=False 写动作必须校验 ticket.can_operate；
- C-3 TaskViewSet.sync_task_status：detail=False 必须校验 ticket.can_view；
- H-3 TaskFieldViewSet.batch_update：批量改字段必须命中所属单据的处理人/创建人/超管；
- H-4 TaskLibViewSet：列表/读取按 creator 过滤（个人范畴）。
"""

import json
from unittest import mock

from django.test import TestCase, override_settings

from itsm.component.constants.task import NORMAL_TASK
from itsm.task.models import Task, TaskField, TaskLib
from itsm.task.permissions import TaskPermissionValidate
from itsm.ticket.models import Ticket


def _make_ticket(creator="creator_a", current_status="RUNNING"):
    return Ticket.objects.create(
        sn="SN-{}-{}".format(creator, current_status),
        title="t",
        service_id=1,
        service_type="request",
        creator=creator,
        current_status=current_status,
    )


def _make_task(ticket, name="t"):
    return Task.objects.create(
        ticket_id=ticket.id,
        state_id=0,
        name=name,
        task_schema_id=0,
        component_type=NORMAL_TASK,
        creator=ticket.creator,
    )


class FakeView(object):
    def __init__(self, action):
        self.action = action


class FakeRequest(object):
    def __init__(self, username):
        class _U(object):
            pass

        self.user = _U()
        self.user.username = username


class TaskPermissionValidateTest(TestCase):
    """C-1：单元层验证 has_object_permission 的分类语义。"""

    def setUp(self):
        Ticket.objects.all().delete()
        Task.objects.all().delete()
        self.ticket = _make_ticket(creator="alice")
        self.task = _make_task(self.ticket)
        self.perm = TaskPermissionValidate()

    def tearDown(self):
        Task.objects.all().delete()
        Ticket.objects.all().delete()

    def _check(self, username, action):
        return self.perm.has_object_permission(
            FakeRequest(username), FakeView(action), self.task
        )

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.task.models.Task.can_process", return_value=True)
    def test_proceed_falls_back_to_can_process(self, _can_process, _superuser):
        self.assertTrue(self._check("anyone", "proceed"))

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=True)
    def test_superuser_bypasses_all_actions(self, _superuser):
        for act in ["update", "partial_update", "destroy", "retry", "skip",
                    "retrieve", "fields", "get_task_status"]:
            self.assertTrue(self._check("super", act), act)

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.real_current_processors",
                new_callable=mock.PropertyMock, return_value=[])
    @mock.patch("itsm.ticket.models.Ticket.can_operate", return_value=False)
    def test_write_action_rejects_unrelated_user(
        self, _can_operate, _processors, _superuser
    ):
        for act in ["update", "partial_update", "destroy", "retry", "skip"]:
            self.assertFalse(self._check("bob", act), act)

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_write_action_allows_ticket_creator(self, _superuser):
        # alice 是 ticket.creator，应放行所有写动作
        for act in ["update", "partial_update", "destroy", "retry", "skip"]:
            self.assertTrue(self._check("alice", act), act)

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.can_view", return_value=False)
    def test_read_action_rejects_unrelated_user(self, _can_view, _superuser):
        for act in ["retrieve", "fields", "get_task_status"]:
            self.assertFalse(self._check("bob", act), act)

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.can_view", return_value=True)
    def test_read_action_allows_ticket_viewer(self, _can_view, _superuser):
        for act in ["retrieve", "fields", "get_task_status"]:
            self.assertTrue(self._check("viewer", act), act)

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_unknown_action_returns_true(self, _superuser):
        # 非读非写非 proceed 的 action，保持原有放行语义（list 等由 queryset 兜底）
        self.assertTrue(self._check("bob", "list"))

    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_missing_ticket_rejects(self, _superuser):
        # ticket_id 已被改为不存在
        self.task.ticket_id = 999999
        self.task.save(update_fields=["ticket_id"])
        for act in ["update", "retrieve"]:
            self.assertFalse(self._check("bob", act), act)


class TaskFieldBatchUpdatePermissionTest(TestCase):
    """H-3：TaskFieldViewSet.batch_update 必须命中所属单据归属。"""

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        Ticket.objects.all().delete()
        Task.objects.all().delete()
        TaskField.objects.all().delete()
        self.ticket = _make_ticket(creator="alice")
        self.task = _make_task(self.ticket)
        self.field = TaskField.objects.create(
            task=self.task,
            type="STRING",
            key="memo",
            name="memo",
            stage="CREATE",
            sequence=1,
            _value=json.dumps("old"),
        )

    def tearDown(self):
        TaskField.objects.all().delete()
        Task.objects.all().delete()
        Ticket.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.real_current_processors",
                new_callable=mock.PropertyMock, return_value=[])
    @mock.patch("itsm.ticket.models.Ticket.can_operate", return_value=False)
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit"
                ".has_permission", return_value=True)
    def test_batch_update_rejects_unrelated_user(self, *_):
        url = "/api/task/task_fields/batch_update/"
        data = {"fields": [{"id": self.field.id, "value": "new", "choice": []}]}
        resp = self.client.put(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        # ValidationError → result False，且字段未被改写
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.field.refresh_from_db()
        self.assertEqual(self.field._value, json.dumps("old"))

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=True)
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit"
                ".has_permission", return_value=True)
    def test_batch_update_allows_superuser(self, *_):
        url = "/api/task/task_fields/batch_update/"
        data = {"fields": [{"id": self.field.id, "value": "new", "choice": []}]}
        resp = self.client.put(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], True)
        self.field.refresh_from_db()
        self.assertEqual(self.field._value, "new")


class TaskSetOrderPermissionTest(TestCase):
    """C-2：set_order 必须先校验 ticket.can_operate / 超管。"""

    def setUp(self):
        Ticket.objects.all().delete()
        Task.objects.all().delete()
        self.ticket = _make_ticket(creator="alice")
        self.task = _make_task(self.ticket)

    def tearDown(self):
        Task.objects.all().delete()
        Ticket.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.can_operate", return_value=False)
    @mock.patch("itsm.task.serializers.TaskOrderSerializer.is_valid",
                return_value=True)
    def test_set_order_rejects_unrelated_user(self, *_):
        url = "/api/task/tasks/order/"
        data = {
            "ticket_id": self.ticket.id,
            "task_orders": [{"task_id": self.task.id, "order": 1}],
        }
        resp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    def test_set_order_rejects_missing_ticket(self, *_):
        url = "/api/task/tasks/order/"
        data = {
            "ticket_id": 99999999,
            "task_orders": [{"task_id": self.task.id, "order": 1}],
        }
        resp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        # serializer 阶段 TicketValidValidator 报"请输入合法单据ID"
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)


class TaskSyncStatusPermissionTest(TestCase):
    """C-3：sync_task_status 必须校验 ticket.can_view / 超管。"""

    def setUp(self):
        Ticket.objects.all().delete()
        Task.objects.all().delete()
        self.ticket = _make_ticket(creator="alice")

    def tearDown(self):
        Ticket.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.can_view", return_value=False)
    def test_sync_rejects_unrelated_user(self, *_):
        url = "/api/task/tasks/sync_task_status/?ticket_id={}".format(self.ticket.id)
        resp = self.client.get(path=url, content_type="application/json")
        self.assertEqual(resp.status_code, 403)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.task.models.Task.sync_tasks_status", return_value=None)
    @mock.patch("itsm.role.models.UserRole.is_itsm_superuser", return_value=False)
    @mock.patch("itsm.ticket.models.Ticket.can_view", return_value=True)
    def test_sync_allows_viewer(self, *_):
        url = "/api/task/tasks/sync_task_status/?ticket_id={}".format(self.ticket.id)
        resp = self.client.get(path=url, content_type="application/json")
        self.assertEqual(resp.status_code, 200)


class TaskLibPersonalScopeTest(TestCase):
    """H-4：TaskLibViewSet 个人范畴语义。"""

    def setUp(self):
        TaskLib.objects.all().delete()
        TaskLib.objects.create(name="mine", service_id=1, creator="admin")
        TaskLib.objects.create(name="other", service_id=1, creator="bob")

    def tearDown(self):
        TaskLib.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.component.drf.permissions.IamAuthWithoutResourcePermit"
                ".has_permission", return_value=True)
    def test_list_only_returns_personal_libs(self, *_):
        url = "/api/task/libs/"
        resp = self.client.get(path=url, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        names = [item["name"] for item in resp.data["data"]]
        self.assertIn("mine", names)
        self.assertNotIn("other", names)
