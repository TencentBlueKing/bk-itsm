# -*- coding: utf-8 -*-
from django.test import TestCase
from blueapps.core.celery.celery import app


class TestHelper(TestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
