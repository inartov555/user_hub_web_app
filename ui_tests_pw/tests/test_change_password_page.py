"""
Tests for the Change Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.change_password_page import ChangePasswordPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from config import DEFAULT_REGULAR_USERNAME


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_admin_can_open_change_password_for_user(logged_in_admin: Page, theme: Theme, locale_code: str) -> None:
    """
    Admin should be able to navigate to the change-password page for a user.
    """
    page = logged_in_admin
    set_theme(page, theme)
    set_locale(page, locale_code)

    users = UsersTablePage(page)
    users.open()
    users.search_input.fill(DEFAULT_REGULAR_USERNAME)
    page.wait_for_timeout(500)
    # Click first change-password button if visible.
    page.locator("text=Change password").first.click()
    expect(page).to_have_url("**/change-password")


@pytest.mark.regular_user
def test_regular_user_cannot_change_other_users_password(logged_in_regular: Page) -> None:
    """
    Regular user should not be able to access another user's change-password page.
    """
    page = logged_in_regular
    cp = ChangePasswordPage(page)
    # Attempt to access a low, probably non-self id.
    cp.open_for_user(1)
    cp.fill_passwords("NewPass123!", "NewPass123!")
    cp.submit()
    cp.assert_error_visible()
