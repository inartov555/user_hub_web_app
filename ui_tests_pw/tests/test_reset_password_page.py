"""
Tests for the Reset Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from core.constants import LocaleConsts, ThemeConsts
from pages.reset_password_page import ResetPasswordPage


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_reset_password_page_renders(reset_password_page: ResetPasswordPage,
                                     ui_theme_param: Theme,
                                     ui_locale_param: str) -> None:
    """
    Reset password page should render correctly under multiple themes and locales.
    """
    reset_password_page.ensure_theme(ui_theme_param)
    reset_password_page.ensure_locale(ui_locale_param)
    expect(reset_password_page.email).to_be_visible()
    # Verifying localization
    actual = reset_password_page.page_title.text_content()
    expected = "Reset password"
    reset_password_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.parametrize("email", ["user@example.com"])
def test_reset_password_request_shows_feedback(reset_password_page: ResetPasswordPage,
                                               email: str) -> None:
    """
    Submitting a reset-password request should show user feedback.
    """
    reset_password_page.request_reset(email)
    reset_password_page.assert_info_message()
