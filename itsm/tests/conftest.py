"""Initialize Django for the isolated attachment test settings."""

import django
from django.apps import apps


def pytest_configure():
    if not apps.ready:
        django.setup()
