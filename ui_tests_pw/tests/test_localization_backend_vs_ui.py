"""
Cross-check UI locale dropdown with Django backend configuration.
"""

from __future__ import annotations
from typing import Set

from playwright.sync_api import Page

from utils.django_localization import get_backend_languages
from utils.localization import get_visible_locales
from utils.theme import set_theme
from pages.login_page import LoginPage


def test_locale_dropdown_matches_backend_languages(page: Page) -> None:
    """
    Verify that the UI locale dropdown exposes all backend languages (by code).

    This uses Django's settings.LANGUAGES via :mod:`django_localization`.
    """
    login = LoginPage(page)
    login.open()
    set_theme(page, "light")
    visible = set(get_visible_locales(page))

    backend_langs = get_backend_languages()
    backend_codes: Set[str] = {code.replace("_", "-") for code, _name in backend_langs}
    missing = backend_codes - visible
    assert not missing, f"UI is missing locale codes: {sorted(missing)}"
