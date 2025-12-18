"""
Tests for the Change Password page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from config import DEFAULT_REGULAR_USERNAME


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_admin_can_open_change_password_for_user(logged_in_admin: Page,  # pylint: disable=unused-argument
                                                 ui_theme_param: Theme,  # pylint: disable=unused-argument
                                                 ui_locale_param: str,  # pylint: disable=unused-argument
                                                 page: Page,
                                                 admin_users_page: UsersTablePage
                                                ) -> None:
    """
    Admin should be able to navigate to the change-password page for a user.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    # Type username and wait the table is refreshed
    admin_users_page.search_and_wait_for_results(DEFAULT_REGULAR_USERNAME)
    # Click first change-password button
    admin_users_page.change_password_btn.first.click()
    # Verify that the change-password URI is opened
    expect(page).to_have_url(re.compile(r".*/users/\d+/change-password$"))


@pytest.mark.regular_user
def test_regular_user_cannot_change_other_users_password(logged_in_regular: Page,  # pylint: disable=unused-argument
                                                         regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not be able to access another user's change-password page.
    """
    # Verifying that the Change Password column is not shown for a regular user
    regular_users_page.assert_admin_controls_hidden_for_regular_user()
