"""
Tests for the Reset Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_reset_password_page_renders(page: Page,
                                     reset_password_page: Page,
                                     ui_theme_param: Theme,
                                     ui_locale_param: str) -> None:
    """
    Reset password page should render correctly under multiple themes and locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    expect(reset_password_page.email).to_be_visible()


@pytest.mark.parametrize("email", ["user@example.com"])
def test_reset_password_request_shows_feedback(reset_password_page: Page,
                                               email: str) -> None:
    """
    Submitting a reset-password request should show user feedback.
    """
    reset_password_page.request_reset(email)
    reset_password_page.assert_info_message()
