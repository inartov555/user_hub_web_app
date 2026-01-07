"""
DEMO tests.
Non-test methods that start from _* are state dependent.

   1. test_base_demo
      Base DEMO test to run multiple pages and take screenshots

   2. test_locale_demo
      Locale DEMO test to run multiple pages and take screenshots
"""

from __future__ import annotations
import random
import string

import pytest
from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from conftest import take_a_screenshot, delete_users_by_suffix_via_api
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.reset_password_page import ResetPasswordPage
from pages.users_table_page import UsersTablePage
from pages.user_delete_confirm_page import UserDeleteConfirmPage
from pages.change_password_page import ChangePasswordPage
from pages.profile_view_page import ProfileViewPage
from pages.profile_edit_page import ProfileEditPage
from pages.stats_page import StatsPage
from pages.settings_page import SettingsPage
from pages.excel_import_page import ExcelImportPage
from utils.theme import Theme
from utils.auth import get_api_utils
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)


# Some elements do not have enough time to update styles before taking a screenshot
FIXED_TIME_TO_WAIT = 0.2


def _helper_login_page(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Log in page (Success/Error cases)
    """
    login_page = LoginPage(page)
    login_page.open()
    # To see the Cookie Consent overlay in different themes and then the theme changed,
    # let's set display: none for block. The page should be reloaded after that
    # to see the cookie consent pop-up again.
    login_page.hide_cookie_consent_popup_in_dom()
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    login_page.reload()
    # Screenshot -> Cookie consent pop-up
    take_a_screenshot(page)
    # Accepting the cookie consent pop-up
    login_page.accept_cookie_consent_if_present()
    # Screenshot -> Login page
    take_a_screenshot(page)
    login_page.submit_credentials_error("invalid", "short")
    # Screenshot -> Login page -> Error
    take_a_screenshot(page)


def _helper_signup_page(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Sign up page (Success/Error cases)
    """
    login_page = LoginPage(page)
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    login_page.click_create_account_link()
    # Screenshot -> Signup page
    take_a_screenshot(page)
    signup_page = SignupPage(page)
    signup_page.submit_credentials_error("mail", "", "mail")
    # Screenshot -> Signup page -> Error
    take_a_screenshot(page)
    # Getting back to the /login page
    signup_page.click_sign_in_link()


def _helper_reset_password_page(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Reset Password page (Success/Error cases)
    """
    login_page = LoginPage(page)
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    # Now, let's open Forgot Password page
    login_page.click_forgot_password_link()
    # Screenshot -> Forgot Password page -> Email input
    take_a_screenshot(page)
    reset_password_page = ResetPasswordPage(page)
    reset_password_page.request_reset("invalid")
    reset_password_page.assert_error_visible()
    # Screenshot -> Reset Password page -> Error
    take_a_screenshot(page)
    # Clearing email field before entering a correct one
    reset_password_page.email.press("Control+A")
    reset_password_page.email.press("Backspace")
    reset_password_page.request_reset("test1@test.com")
    reset_password_page.assert_info_message()
    # Screenshot -> Forgot Password page -> Info page
    take_a_screenshot(page)
    # Let's get back to the Login page
    reset_password_page.click_sign_in_link()


def _helper_users_table_page_admin_user(page: Page,
                                        ui_theme_param: Theme,
                                        ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Users Table page (table, controls)
    """
    login_page = LoginPage(page)
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    # Now, let's login as Admin user to get to the Users Table page
    login_page.submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Let's set multi-column sorting (First Name - ascending, Last Name - descending)
    users_table_page = UsersTablePage(page)
    users_table_page.change_column_sorting("firstname", "asc")
    users_table_page.change_column_sorting("lastname", "desc")
    users_table_page.assert_column_sorting("firstname", "asc")
    users_table_page.assert_column_sorting("lastname", "desc")
    # Let's change the number of users per page to 10
    users_table_page.change_number_of_users_per_page_control_top(10)
    # The table does not have time to change the styles before take a screenshot
    users_table_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Admin user -> Users Table page -> Multi column sort on
    take_a_screenshot(page)
    # Let's create a user which will be deleted right before confirming deletion
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    api_utils.import_excel_spreadsheet(access_token, "test_data/excel_import/import_template_test_20_users.xlsx")
    # Now, let's search for just imported users on UI
    users_table_page.search_and_wait_for_results("admin")
    # There are supposed to be 2 users: admin and just created one
    users_table_page.check_all_header.click()
    # The item checking does not have time to change the styles before take a screenshot
    users_table_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Admin user -> Users Table page -> Checked users
    take_a_screenshot(page)


def _helper_user_delete_page(page: Page,
                             ui_theme_param: Theme,
                             ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the User Delete page (Success/Error cases)
    """
    # Now, let's set locale and theme for the User Delete Confirm page
    users_table_page = UsersTablePage(page)
    users_table_page.ensure_theme(ui_theme_param)
    users_table_page.ensure_locale(ui_locale_param)
    # Now, let's see the user deletion page
    users_table_page.click_delete_users_and_wait_confirm_delete_page()
    user_delete_page = UserDeleteConfirmPage(page)
    user_delete_page.assert_confirm_delete_loaded()
    # Screenshot -> Admin user -> User Delete Confirm page -> List of users to delete
    take_a_screenshot(page)
    # Let's delete previously created via API user, so the delete operation on UI will show these
    # as failed during deletion since they are not pesent at the momen of UI deletion
    delete_users_by_suffix_via_api("admin-excel-watermelon-11@test.com", "strict", "email")
    delete_users_by_suffix_via_api("admin-excel-watermelon-13@test.com", "strict", "email")
    delete_users_by_suffix_via_api("admin-excel-watermelon-14@test.com", "strict", "email")
    # Let's see if User Delete Confirm page shows error messages (it's supposed to show an error)
    user_delete_page.click_top_confirm_delete_error()
    # Screenshot -> Admin user -> User Delete Confirm page -> List of users to delete
    take_a_screenshot(page)
    # Let's get back to the /users page
    user_delete_page.click_top_cancel()


def _helper_change_password_page(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Change Password page (Success/Error cases)
    """
    users_table_page = UsersTablePage(page)
    users_table_page.ensure_theme(ui_theme_param)
    users_table_page.ensure_locale(ui_locale_param)
    # Let's click the Change Password button
    users_table_page.search_and_wait_for_results("mi")
    # Let's select the 1st user for changing the password
    users_table_page.change_password_btn.nth(0).click()
    # Screenshot -> Admin user -> Change Password page
    take_a_screenshot(page)
    # Error case
    change_password_page = ChangePasswordPage(page)
    change_password_page.fill_passwords("short", "short")
    change_password_page.submit.click()
    change_password_page.assert_error_visible()
    # Screenshot -> Admin user -> Change Password page -> Error case
    take_a_screenshot(page)


def _helper_users_table_page_regular_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Users Table page (table, controls)
    """
    login_page = LoginPage(page)
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    users_table_page = UsersTablePage(page)
    # Let's log in to the website as a regular user
    users_table_page.click_logout_and_wait_for_login_page()
    login_page.submit_credentials_success(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    # Let's set some multi-column sorting
    users_table_page.change_column_sorting("username", "asc")
    users_table_page.change_column_sorting("email", "desc")
    users_table_page.change_column_sorting("firstname", "asc")
    users_table_page.change_column_sorting("lastname", "desc")
    users_table_page.assert_column_sorting("username", "asc")
    users_table_page.assert_column_sorting("email", "desc")
    users_table_page.assert_column_sorting("firstname", "asc")
    users_table_page.assert_column_sorting("lastname", "desc")
    # Let's change the number of users per page to 10
    users_table_page.change_number_of_users_per_page_control_top(10)
    # Screenshot -> Regular User -> Users Table page -> Multi-colunn sort
    take_a_screenshot(page)


def _helper_profile_view_page_regular_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Profile View page (Success/Error cases)
    """
    # Let's go to the Profile tab
    profile_view_page = ProfileViewPage(page)
    profile_view_page.ensure_theme(ui_theme_param)
    profile_view_page.ensure_locale(ui_locale_param)
    profile_view_page.click_profile_tab()
    profile_view_page.assert_profile_basics_visible()
    # The tab does not have time to change the styles before take a screenshot
    profile_view_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Regular User -> Profile View Page
    take_a_screenshot(page)


def _helper_profile_edit_page_regular_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Profile Edit page (Success/Error cases)
    """
    profile_view_page = ProfileViewPage(page)
    profile_view_page.ensure_theme(ui_theme_param)
    profile_view_page.ensure_locale(ui_locale_param)
    # Now, let's see the Profile Edit page
    profile_view_page.click_edit_button()
    profile_edit_page = ProfileEditPage(page)
    profile_edit_page.assert_loaded()
    # Screenshot -> Regular User -> Profile Edit Page
    take_a_screenshot(page)
    # Let's check error validation
    profile_edit_page.remove_maxlength_attribute_from_input_fields()
    field_value_501_symb = "".join(random.choices(string.ascii_letters + string.digits, k=501))
    profile_edit_page.fill_basic_fields(field_value_501_symb,
                                        field_value_501_symb,
                                        field_value_501_symb)
    profile_edit_page.save.click()
    profile_edit_page.assert_error_visible()
    # Screenshot -> Regular User -> Profile Edit Page -> Error alert
    take_a_screenshot(page)


def _helper_user_stats_page_admin_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the User Stats page
    """
    login_page = LoginPage(page)
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    profile_edit_page = ProfileEditPage(page)
    # Let's log in to the website as Admin user
    profile_edit_page.click_logout_and_wait_for_login_page()
    login_page.submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Let's open the User Stats tab
    stats_page = StatsPage(page)
    stats_page.click_additional_user_stats_tab()
    stats_page.assert_loaded()
    # The tab does not have time to change styles before taking a screenshot
    stats_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Admin User -> User Stats Page
    take_a_screenshot(page)


def _helper_app_settings_page_admin_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the App Settings page (Success/Error cases)
    """
    # Now, let's go to the Additional -> App Settings tab
    app_settings_page = SettingsPage(page)
    app_settings_page.ensure_theme(ui_theme_param)
    app_settings_page.ensure_locale(ui_locale_param)
    app_settings_page.click_additional_app_settings_tab()
    app_settings_page.assert_loaded()
    # The tab does not have time to change styles before taking a screenshot
    app_settings_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Admin User -> App Settings Page
    take_a_screenshot(page)
    # Let's check successful settings save
    app_settings_page.change_values_save_success(False, 222, 222, 222)
    # Screenshot -> Admin User -> App Settings Page -> Success
    take_a_screenshot(page)
    app_settings_page.reload()  # Firefox glitches without it and does not find visible and clickable Save button
    # Let's check the error validation
    app_settings_page.change_values_save_error(True, 13, 13, 13)
    # Screenshot -> Admin User -> App Settings Page -> Error case
    take_a_screenshot(page)


def _helper_excel_import_page_admin_user(page: Page, ui_theme_param: Theme, ui_locale_param: str) -> None:
    """
    This is a helper function that takes screenshots on the Excel Import page (Success/Error cases)
    """
    # Now, let's go to the Additional -> Excel Import tab
    excel_import_page = ExcelImportPage(page)
    excel_import_page.ensure_theme(ui_theme_param)
    excel_import_page.ensure_locale(ui_locale_param)
    excel_import_page.click_additional_excel_import_tab()
    excel_import_page.assert_loaded()
    # The tab does not have time to change styles before taking a screenshot
    excel_import_page.wait_a_bit(FIXED_TIME_TO_WAIT)
    # Screenshot -> Admin User -> Excel Import Page
    take_a_screenshot(page)
    # Let's check the success case
    excel_import_page.import_excel_file_success("test_data/excel_import/import_template_test_50_users.xlsx")
    # Let's check the success message title
    actual = excel_import_page.success_title.text_content()
    expected = "Result"
    excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Screenshot -> Admin User -> Excel Import Page -> Success
    take_a_screenshot(page)
    # Let's check the error validation
    excel_import_page.import_excel_file_error("")
    # Screenshot -> Admin User -> Excel Import Page -> Error case
    take_a_screenshot(page)


@pytest.mark.demo
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.ENGLISH_US])
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(True, 900, 900, 900)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_base_demo(page: Page,
                   ui_theme_param: Theme,
                   ui_locale_param: str,
                   suffix: str,  # pylint: disable=unused-argument
                   rotate_refresh_token: bool,  # pylint: disable=unused-argument
                   renew_at_sec: int,  # pylint: disable=unused-argument
                   idle_timeout_sec: int,  # pylint: disable=unused-argument
                   access_token_lifetime: int,  # pylint: disable=unused-argument
                  ) -> None:
    """
    Base DEMO test to run multiple pages and take screenshots
    """
    _helper_login_page(page,
                       ui_theme_param,
                       ui_locale_param)
    _helper_signup_page(page,
                        ui_theme_param,
                        ui_locale_param)
    _helper_reset_password_page(page,
                                ui_theme_param,
                                ui_locale_param)
    _helper_users_table_page_admin_user(page,
                                        ui_theme_param,
                                        ui_locale_param)
    _helper_user_delete_page(page,
                             ui_theme_param,
                             ui_locale_param)
    _helper_change_password_page(page,
                                 ui_theme_param,
                                 ui_locale_param)
    _helper_users_table_page_regular_user(page,
                                          ui_theme_param,
                                          ui_locale_param)
    _helper_profile_view_page_regular_user(page,
                                           ui_theme_param,
                                           ui_locale_param)
    _helper_profile_edit_page_regular_user(page,
                                           ui_theme_param,
                                           ui_locale_param)
    _helper_user_stats_page_admin_user(page,
                                       ui_theme_param,
                                       ui_locale_param)
    _helper_app_settings_page_admin_user(page,
                                         ui_theme_param,
                                         ui_locale_param)
    _helper_excel_import_page_admin_user(page,
                                         ui_theme_param,
                                         ui_locale_param)


@pytest.mark.demo
@pytest.mark.parametrize("ui_theme_param", [ThemeConsts.LIGHT])
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize(
    "rotate_refresh_token, renew_at_sec, idle_timeout_sec, access_token_lifetime",
    [(True, 900, 900, 900)])
@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_locale_demo(page: Page,
                     ui_theme_param: Theme,
                     suffix: str,  # pylint: disable=unused-argument
                     rotate_refresh_token: bool,  # pylint: disable=unused-argument
                     renew_at_sec: int,  # pylint: disable=unused-argument
                     idle_timeout_sec: int,  # pylint: disable=unused-argument
                     access_token_lifetime: int,  # pylint: disable=unused-argument
                    ) -> None:
    """
    Locale DEMO test to run multiple pages and take screenshots
    """
    _helper_login_page(page,
                       ui_theme_param,
                       LocaleConsts.ESTONIAN)
    _helper_signup_page(page,
                        ui_theme_param,
                        LocaleConsts.FINNISH)
    _helper_reset_password_page(page,
                                ui_theme_param,
                                LocaleConsts.ENGLISH_US)
    _helper_users_table_page_admin_user(page,
                                        ui_theme_param,
                                        LocaleConsts.UKRAINIAN)
    _helper_user_delete_page(page,
                             ui_theme_param,
                             LocaleConsts.CZECH)
    _helper_change_password_page(page,
                                 ui_theme_param,
                                 LocaleConsts.POLISH)
    _helper_users_table_page_regular_user(page,
                                          ui_theme_param,
                                          LocaleConsts.ESTONIAN)
    _helper_profile_view_page_regular_user(page,
                                           ui_theme_param,
                                           LocaleConsts.UKRAINIAN)
    _helper_profile_edit_page_regular_user(page,
                                           ui_theme_param,
                                           LocaleConsts.CZECH)
    _helper_user_stats_page_admin_user(page,
                                       ui_theme_param,
                                       LocaleConsts.SPANISH)
    _helper_app_settings_page_admin_user(page,
                                         ui_theme_param,
                                         LocaleConsts.POLISH)
    _helper_excel_import_page_admin_user(page,
                                         ui_theme_param,
                                         LocaleConsts.SPANISH)
