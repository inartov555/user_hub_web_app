"""
Tests for the Reset Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.reset_password_page import ResetPasswordPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_reset_password_page_renders(page: Page, theme: Theme, locale_code: str) -> None:
    """
    Reset password page should render correctly under multiple themes and locales.
    """
    reset_page = ResetPasswordPage(page)
    reset_page.open()
    set_theme(page, theme)
    set_locale(page, locale_code)
    expect(page.locator("input[type='email']")).to_be_visible()


@pytest.mark.parametrize("email", ["user@example.com", "invalid-email"])
def test_reset_password_request_shows_feedback(page: Page, email: str) -> None:
    """
    Submitting a reset-password request should show user feedback.
    """
    reset_page = ResetPasswordPage(page)
    reset_page.open()
    reset_page.request_reset(email)
    reset_page.assert_success_or_error()
