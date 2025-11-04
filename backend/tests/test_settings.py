"""
Unit tests
"""

from core.settings import *

# Testing if Settings object can be initialized
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3","NAME": ":memory:"}}
PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
