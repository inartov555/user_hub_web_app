"""
Tests for the Change Password page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect
from django.utils import translation

from pages.users_table_page import UsersTablePage
from pages.change_password_page import ChangePasswordPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from config import DEFAULT_REGULAR_USERNAME


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_admin_can_open_change_password_for_user(ui_theme_param: Theme,
                                                 ui_locale_param: str,
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
    change_password_page = ChangePasswordPage(page)
    # Verify that the change-password URI is opened
    expect(page).to_have_url(re.compile(r".*/users/\d+/change-password$"))
    page.wait_for_url(re.compile(r".*/users/\d+/change-password$"))
    # Verifying localization
    actual = change_password_page.page_title.text_content()
    with translation.override(ui_locale_param.lower()):
        expected = translation.gettext("Change password")
    assert actual == expected, f"Wrong page title localization; actual '{actual}'; expected '{expected}'"


@pytest.mark.regular_user
def test_regular_user_cannot_change_other_users_password(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not be able to access another user's change-password page.
    """
    # Verifying that the Change Password column is not shown for a regular user
    regular_users_page.assert_admin_controls_hidden_for_regular_user()
