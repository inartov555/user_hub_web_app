"""
Tests for the Change Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from pages.users_table_page import UsersTablePage
from pages.change_password_page import ChangePasswordPage
from config import DEFAULT_REGULAR_USERNAME
from utils.theme import Theme


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_admin_can_open_change_password_for_user(ui_theme_param: Theme,
                                                 ui_locale_param: str,
                                                 page: Page,
                                                 admin_users_page: UsersTablePage
                                                ) -> None:
    """
    Admin should be able to navigate to the change-password page for a user.
    """
    admin_users_page.ensure_theme(ui_theme_param)
    admin_users_page.ensure_locale(ui_locale_param)
    # Type username and wait the table is refreshed
    admin_users_page.search_and_wait_for_results(DEFAULT_REGULAR_USERNAME)
    # Click first change-password button
    admin_users_page.change_password_btn.first.click()
    change_password_page = ChangePasswordPage(page)
    change_password_page.wait_for_change_password_page_to_load()
    change_password_page.assert_change_password_is_loaded()
    # Verifying localization
    actual = change_password_page.page_title.text_content()
    expected = "Change password"
    change_password_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.regular_user
def test_regular_user_cannot_change_other_users_password(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not be able to access another user's change-password page.
    """
    # Verifying that the Change Password column is not shown for a regular user
    regular_users_page.assert_admin_controls_hidden_for_regular_user()
