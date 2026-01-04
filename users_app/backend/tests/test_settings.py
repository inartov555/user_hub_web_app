"""
Unit tests
"""

# This test intentionally uses a wildcard import to load all Django settings.
# pylint: disable=wildcard-import,unused-wildcard-import,unused-import

from core.settings import *

# Testing if the Settings object can be initialized
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3","NAME": ":memory:"}}
PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]

if LANGUAGE_CODE != "en-us":
    raise AssertionError(f"Default language is not en-us; current value: {LANGUAGE_CODE}")
