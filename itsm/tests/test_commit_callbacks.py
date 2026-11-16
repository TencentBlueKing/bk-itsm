"""Request fixtures must execute committed callbacks but discard rolled-back ones."""

from unittest.mock import Mock

from django.db import transaction
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from itsm.tests.middlewares import CommitCallbacksMiddleware


class CommitCallbacksMiddlewareTest(TestCase):
    def test_executes_callback_after_response_creation(self):
        callback = Mock()

        def response(request):
            with transaction.atomic():
                transaction.on_commit(callback)
            callback.assert_not_called()
            return HttpResponse()

        result = CommitCallbacksMiddleware(response)(RequestFactory().post("/"))
        self.assertEqual(result.status_code, 200)
        callback.assert_called_once_with()

    def test_does_not_execute_rolled_back_callback(self):
        callback = Mock()

        def response(request):
            with transaction.atomic():
                transaction.on_commit(callback)
                transaction.set_rollback(True)
            return HttpResponse()

        CommitCallbacksMiddleware(response)(RequestFactory().post("/"))
        callback.assert_not_called()
