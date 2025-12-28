"""
Cross-check UI locale dropdown with Django backend configuration.
"""

from __future__ import annotations

from playwright.sync_api import Page

from utils.django_localization import get_backend_languages
from utils.localization import get_visible_locales, assert_locale_visible
from utils.theme import set_theme
from pages.login_page import LoginPage


def test_locale_dropdown_matches_backend_languages(login_page: LoginPage,  # pylint: disable=unused-argument
                                                   page: Page) -> None:
    """
    Verify that the UI locale dropdown exposes all backend languages (by code).

    This uses Django's settings.LANGUAGES via django_localization.
    """
    set_theme(page, "light")
    backend_langs = get_backend_languages()
    backend_codes: Set[str] = {code.lower() for code, _name in backend_langs}
    assert_locale_visible(backend_codes)
