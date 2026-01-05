"""
Tests for the Change Password page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from pages.users_table_page import UsersTablePage
from pages.login_page import LoginPage
from pages.change_password_page import ChangePasswordPage
from pages.profile_view_page import ProfileViewPage
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
                                                 admin_users_page: UsersTablePage) -> None:
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
    # Verifying that the Change Password column in the Users Table page is not shown for a regular user
    regular_users_page.assert_admin_controls_hidden_for_regular_user()


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["one"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_admin_can_change_password_for_any_user(page: Page,
                                                admin_users_page: UsersTablePage,
                                                suffix: str) -> None:
    """
    Admin should be able to change password for any user.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    username = f"ui-test-{suffix}"
    # old_password = "Ch@ngeme123"
    new_password = "changeme123"
    # Let's search for a user in the Users Table
    admin_users_page.search_and_wait_for_results(username)
    # Let's select the 1st user for changing the password
    admin_users_page.change_password_btn.nth(0).click()
    change_password_page = ChangePasswordPage(page)
    change_password_page.fill_passwords(new_password, new_password)
    change_password_page.submit.click()
    admin_users_page.wait_for_the_users_table_page_to_load()
    # Now, let's logout from admin user and login as a user the password just got changed
    admin_users_page.click_logout_and_wait_for_login_page()
    login_page = LoginPage(page)
    login_page.submit_credentials_success(username, new_password)
    login_page.wait_for_the_users_table_page_to_load()
    # And let's check if the currently logged in username is shown in the greeting message
    users_table_page = UsersTablePage(page)
    users_table_page.assert_username_contained_in_greeting_message(username)


@pytest.mark.regular_user
@pytest.mark.parametrize("suffix", ["one"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_regular_user_can_change_password_for_themselves(page: Page,
                                                         login_page: LoginPage,
                                                         suffix: str) -> None:
    """
    Regular user should be able to change password for themselves

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    username = f"ui-test-{suffix}"
    old_password = "Ch@ngeme123"
    new_password = "changeme123"
    # Login as a regular user with old password
    login_page.submit_credentials_success(username, old_password)
    # Go to the Profile View page
    profile_view_page = ProfileViewPage(page)
    profile_view_page.click_profile_tab()
    # Click the Change Password button in the Profile View page
    profile_view_page.click_change_password_button()
    change_password_page = ChangePasswordPage(page)
    # Let's change the password
    change_password_page.fill_passwords(new_password, new_password)
    change_password_page.submit.click()
    users_table_page = UsersTablePage(page)
    users_table_page.wait_for_the_users_table_page_to_load()
    # Now, let's logout and login with the new password
    users_table_page.click_logout_and_wait_for_login_page()
    login_page.submit_credentials_success(username, new_password)
    login_page.wait_for_the_users_table_page_to_load()
    # And let's check if the currently logged in username is shown in the greeting message
    users_table_page.assert_username_contained_in_greeting_message(username)
