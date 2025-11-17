"""
Helpers for introspecting Django localization from tests.

The UI tests primarily validate the frontend behaviour, but this helper
module demonstrates how Django can also be imported and used to verify
that backend-localized languages are in sync with the UI language picker.
"""

from __future__ import annotations
import os
import sys
from functools import lru_cache
from typing import List, Tuple

import django
from django.conf import settings


# Ensure the Django project (backend) is importable.
BACKEND_PATH = os.environ.get("BACKEND_PATH", "/app/backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings"))


@lru_cache(maxsize=1)
def init_django() -> None:
    """
    Initialize Django if it has not been set up yet.

    This is safe to call from multiple tests; initialization happens only once.
    """
    if not settings.configured:
        django.setup()  # pragma: no cover


def get_backend_languages() -> List[Tuple[str, str]]:
    """
    Return the list of configured Django languages.

    Returns:
        A list of (code, human-readable name) tuples matching settings.LANGUAGES.
    """
    init_django()
    return list(getattr(settings, "LANGUAGES", []))


def get_backend_locale_paths() -> List[str]:
    """
    Return configured Django LOCALE_PATHS as string paths.
    """
    init_django()
    return [str(p) for p in getattr(settings, "LOCALE_PATHS", [])]


def get_backend_default_language_code() -> str:
    """
    Return Django's default language code.
    """
    init_django()
    return getattr(settings, "LANGUAGE_CODE", "en-us")
