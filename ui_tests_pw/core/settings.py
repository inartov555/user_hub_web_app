from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "ui-tests-secret-key"
DEBUG = False
ALLOWED_HOSTS = ["*"]

USE_TZ = True
TIME_ZONE = "UTC"

USE_I18N = True

LANGUAGE_CODE = "en-US"
LANGUAGES = [
    ("en-US", "English"),
    ("uk-UA", "Ukrainian"),
]

LOCALE_PATHS = [str(BASE_DIR / "locale")]

INSTALLED_APPS: list[str] = []
MIDDLEWARE: list[str] = []

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
