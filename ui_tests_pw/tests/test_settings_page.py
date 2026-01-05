"""
Tests for the admin Settings page (admin only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
)
from core.constants import LocaleConsts, ThemeConsts
from pages.settings_page import SettingsPage
from pages.users_table_page import UsersTablePage
from pages.login_page import LoginPage
from utils.theme import Theme


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_settings_page_renders_for_admin(settings_page: SettingsPage,
                                         ui_theme_param: Theme,
                                         ui_locale_param: str) -> None:
    """
    Admin user can open the settings page under multiple themes/locales.
    """
    settings_page.ensure_theme(ui_theme_param)
    settings_page.ensure_locale(ui_locale_param)
    settings_page.assert_loaded()
    # Verifying localization
    actual = settings_page.page_title.text_content()
    expected = "App Settings"
    settings_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.regular_user
def test_settings_page_not_accessible_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not be able to access the settings page.
    Settings tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(False, 64, 60, 68)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_rotate_false_inactivity_timeout(page: Page,
                                         settings_page: SettingsPage,
                                         rotate_refresh_token,
                                         renew_at_sec,  # pylint: disable=unused-argument
                                         idle_timeout_sec,
                                         access_token_lifetime) -> None:
    """
    1. ROTATE_REFRESH_TOKENS is False
    2. User logs in and just waits for idle timeout (no actions on UI or API)
    3. Once token is invalidated due to inactivity timeout, the Login page should be displayed
    """
    # Verifying if App Settings page is actually shown
    settings_page.assert_loaded()
    # Setting values to App Settings in UI
    settings_page.change_values_save_success(rotate_refresh_token,
                                             renew_at_sec,
                                             idle_timeout_sec,
                                             access_token_lifetime)
    # Now, logout and re-login is required for new settings to be applied
    settings_page.click_logout_and_wait_for_login_page()
    LoginPage(page).submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now let's just wait for (idle_timeout_sec + 1) seconds to invalidate user session
    settings_page.wait_a_bit(idle_timeout_sec + 1)
    settings_page.reload()
    # Verifying if the Login page is shown (it means user session has been invalidated)
    settings_page.assert_login_page_is_displayed()


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(False, 64, 60, 68)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_rotate_false_token_lifetime(page: Page,
                                     settings_page: SettingsPage,
                                     rotate_refresh_token,
                                     renew_at_sec,  # pylint: disable=unused-argument
                                     idle_timeout_sec,
                                     access_token_lifetime) -> None:
    """
    1. ROTATE_REFRESH_TOKENS is False
    2. User makes some actions, e.g., opens tabs, etc., for (access_token_lifetime) seconds
    3. After that time session should be invalidated
    """
    # Verifying if App Settings page is actually shown
    settings_page.assert_loaded()
    # Setting values to App Settings in UI
    settings_page.change_values_save_success(rotate_refresh_token,
                                             renew_at_sec,
                                             idle_timeout_sec,
                                             access_token_lifetime)
    # Now, logout and re-login is required for new settings to be applied
    settings_page.click_logout_and_wait_for_login_page()
    LoginPage(page).submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now let's refresh the Users Table page for (access_token_lifetime) seconds
    for _ in range(access_token_lifetime):
        settings_page.wait_a_bit(1)
        settings_page.reload()  # reloading Users Table page (it got displayed after re-logging in)
    # Verifying if the Login page is shown (it means user session has been invalidated)
    settings_page.assert_login_page_is_displayed()


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(True, 64, 60, 68)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_rotate_true_inactivity_timeout(page: Page,
                                        settings_page: SettingsPage,
                                        rotate_refresh_token,
                                        renew_at_sec,
                                        idle_timeout_sec,
                                        access_token_lifetime) -> None:
    """
    1. ROTATE_REFRESH_TOKENS is True
    2. User logs in and just waits for idle timeout (no actions on UI or API)
    3. Once token is invalidated due to inactivity timeout, the Login page should be displayed
    """
    # Verifying if App Settings page is actually shown
    settings_page.assert_loaded()
    # Setting values to App Settings in UI
    settings_page.change_values_save_success(rotate_refresh_token,
                                             renew_at_sec,
                                             idle_timeout_sec,
                                             access_token_lifetime)
    # Now, logout and re-login is required for new settings to be applied
    settings_page.click_logout_and_wait_for_login_page()
    LoginPage(page).submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now let's just wait for (idle_timeout_sec + 1) seconds to invalidate user session
    settings_page.wait_a_bit(idle_timeout_sec + 1)
    settings_page.reload()
    # Verifying if the Login page is shown (it means user session has been invalidated)
    settings_page.assert_login_page_is_displayed()


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(True, 64, 60, 68)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_rotate_true_token_refreshed(page: Page,
                                     settings_page: SettingsPage,
                                     rotate_refresh_token,
                                     renew_at_sec,
                                     idle_timeout_sec,
                                     access_token_lifetime) -> None:
    """
    1. ROTATE_REFRESH_TOKENS is True
    2. User makes some actions, e.g., opens tabs, etc., for (access_token_lifetime + 5) seconds
    3. The token should be refreshed
    """
    # Verifying if App Settings page is actually shown
    settings_page.assert_loaded()
    # Setting values to App Settings in UI
    settings_page.change_values_save_success(rotate_refresh_token,
                                             renew_at_sec,
                                             idle_timeout_sec,
                                             access_token_lifetime)
    # Now, logout and re-login is required for new settings to be applied
    settings_page.click_logout_and_wait_for_login_page()
    LoginPage(page).submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now let's refresh the Users Table page for (access_token_lifetime + 5) seconds
    for _ in range(access_token_lifetime + 5):
        settings_page.wait_a_bit(1)
        settings_page.reload()  # reloading Users Table page (it got displayed after re-logging in)
    # Verifying if the Users Table page still shown and user session kept alive
    settings_page.wait_for_the_users_table_page_to_load()


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(True, 64, 60, 68)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_rotate_true_token_refreshed_indle_timeout_after(page: Page,
                                                         settings_page: SettingsPage,
                                                         rotate_refresh_token,
                                                         renew_at_sec,
                                                         idle_timeout_sec,
                                                         access_token_lifetime) -> None:
    """
    1. ROTATE_REFRESH_TOKENS is True
    2. User makes some actions, e.g., opens tabs, etc., for (access_token_lifetime + 5) seconds
    3. The token should be refreshed
    4. Then user does not make any action on UI or API for idle_timeout_sec
    5. When idle_timeout_sec of inactivity time elapsed, user session should be invalidated
    """
    # Verifying if App Settings page is actually shown
    settings_page.assert_loaded()
    # Setting values to App Settings in UI
    settings_page.change_values_save_success(rotate_refresh_token,
                                             renew_at_sec,
                                             idle_timeout_sec,
                                             access_token_lifetime)
    # Now, logout and re-login is required for new settings to be applied
    settings_page.click_logout_and_wait_for_login_page()
    LoginPage(page).submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now let's refresh the Users Table page for (access_token_lifetime + 5) seconds
    for _ in range(access_token_lifetime + 5):
        settings_page.wait_a_bit(1)
        settings_page.reload()  # reloading Users Table page (it got displayed after re-logging in)
    # Verifying if the Users Table page still shown and user session kept alive
    settings_page.wait_for_the_users_table_page_to_load()
    # Now let's just wait for (idle_timeout_sec + 1) seconds to invalidate user session
    settings_page.wait_a_bit(idle_timeout_sec + 1)
    settings_page.reload()
    # Verifying if the Login page is shown (it means user session has been invalidated)
    settings_page.assert_login_page_is_displayed()
