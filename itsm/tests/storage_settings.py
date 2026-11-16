"""Isolated settings for attachment security tests; no database or network."""

import os

SECRET_KEY = "storage-unit-tests-only"
USE_TZ = True
INSTALLED_APPS = ["itsm.attachment"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("ITSM_ATTACHMENT_TEST_DB", ":memory:"),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
