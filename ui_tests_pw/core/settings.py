"""
Django settings
"""

from __future__ import annotations
from pathlib import Path

from django.utils import translation


BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "ui-tests-secret-key"
DEBUG = False
ALLOWED_HOSTS = ["*"]

USE_TZ = True
TIME_ZONE = "UTC"

USE_I18N = True
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en-us", translation.gettext_lazy("English (US)")),
    ("uk-ua", translation.gettext_lazy("Ukrainian")),
    ("et-ee", translation.gettext_lazy("Estonian")),
    ("fi-fi", translation.gettext_lazy("Finnish")),
    ("cs-cz", translation.gettext_lazy("Czech")),
    ("pl-pl", translation.gettext_lazy("Polish")),
    ("es-es", translation.gettext_lazy("Spanish")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

INSTALLED_APPS: list[str] = []
MIDDLEWARE: list[str] = [
    "django.middleware.locale.LocaleMiddleware",]
