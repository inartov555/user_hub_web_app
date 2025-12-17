"""
Tests for the Change Password page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from pages.change_password_page import ChangePasswordPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme
from config import DEFAULT_REGULAR_USERNAME


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
# @pytest.mark.parametrize("theme", ["light", "dark"])
# @pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
@pytest.mark.parametrize("theme", ["light"])
@pytest.mark.parametrize("locale_code", ["en-US"])
def test_admin_can_open_change_password_for_user(logged_in_admin: Page,  # pylint: disable=unused-argument
                                                 theme: Theme,  # pylint: disable=unused-argument
                                                 page: Page,
                                                 admin_users_page: UsersTablePage,
                                                 locale_code: str  # pylint: disable=unused-argument
                                                ) -> None:
    """
    Admin should be able to navigate to the change-password page for a user.
    """
    admin_users_page.search_input.fill(DEFAULT_REGULAR_USERNAME)
    admin_users_page.wait_till_users_table_update_finished()
    # Click first change-password button
    admin_users_page.change_password_btn.first.click()
    expect(page).to_have_url(re.compile(r".*/users/\d+/change-password$"))


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
