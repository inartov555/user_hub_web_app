"""
Cross-check UI locale dropdown with Django backend configuration.
"""

from __future__ import annotations

from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from pages.login_page import LoginPage
from utils.django_localization import get_backend_languages
from utils.localization import assert_locale_visible


def test_locale_dropdown_matches_backend_languages(login_page: LoginPage,
                                                   page: Page) -> None:
    """
    Verify that the UI locale dropdown exposes all backend languages (by code).

    This uses Django's settings.LANGUAGES via django_localization.
    """
    login_page.ensure_theme(ThemeConsts.LIGHT)
    login_page.ensure_locale(LocaleConsts.ENGLISH_US)
    backend_langs = get_backend_languages()
    backend_codes = [code for code, _name in backend_langs]
    assert_locale_visible(page, backend_codes)
