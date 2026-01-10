"""
Tests for the Excel import page (admin-only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD
)
from core.constants import LocaleConsts, ThemeConsts
from pages.excel_import_page import ExcelImportPage
from pages.users_table_page import UsersTablePage
from pages.profile_view_page import ProfileViewPage
from pages.profile_edit_page import ProfileEditPage
from pages.change_password_page import ChangePasswordPage
from pages.login_page import LoginPage
from utils.theme import Theme
from utils.auth import get_api_utils


def _helper_update_profile_via_regular_user(authorized_admin_page: Page,
                                            page: Page,
                                            ui_locale_param: str,
                                            username: str,
                                            password: str,
                                            email: str,
                                            first_name: str,
                                            last_name: str,
                                            bio: str) -> None:
    """
    These steps are shared between at least 2 tests.

    The steps:
        1. Go to the Users Table page and find the user by passed email
        2. Change password for the found user
        3. Log in with passed credentials
        4. Go to Profile and update it with passed values
        5. Log out before futher steps
    """
    # Now let's go to the Users Table page
    authorized_admin_page.click_users_tab()
    users_table_page = UsersTablePage(page)
    users_table_page.search_and_wait_for_results(email)
    # Verifying number of users (expected = 1)
    actual = users_table_page.page_title.text_content()
    expected = "People"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " (1)", "strict")
    users_table_page.change_password_btn.nth(0).click()
    # Set password for previously created user
    change_password_page = ChangePasswordPage(page)
    change_password_page.assert_change_password_is_loaded()
    change_password_page.change_password_success(password)
    # Now, let's login as just created user
    change_password_page.click_logout_and_wait_for_login_page()
    login_page = LoginPage(page)
    login_page.submit_credentials_success(username, password)
    # Let's enter the Profile View page
    profile_view_page = ProfileViewPage(page)
    profile_view_page.click_profile_tab()
    # Enter the Profile Edit page
    profile_view_page.click_edit_button()
    profile_edit_page = ProfileEditPage(page)
    profile_edit_page.assert_loaded()
    # Now, let's set values, first, last names, and bio
    profile_edit_page.click_save_and_wait_profile_view_success(first_name, last_name, bio)
    # Let's log back in as admin to import an excel spreadsheet
    profile_edit_page.click_logout_and_wait_for_login_page()


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.excel_import
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_excel_import_page_renders_for_admin(ui_theme_param: Theme,
                                             ui_locale_param: str,
                                             admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin user can open the Excel import page.
    """
    admin_excel_import_page.ensure_theme(ui_theme_param)
    admin_excel_import_page.ensure_locale(ui_locale_param)
    # Verifying if Import & Download buttons are visible
    admin_excel_import_page.assert_loaded()
    # Verifying localization
    actual = admin_excel_import_page.page_title.text_content()
    expected = "Excel Import"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, None, "strict")


@pytest.mark.regular_user
@pytest.mark.excel_import
def test_excel_import_page_not_visible_in_nav_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not see the Additional/Import from Excel nav items.
    Excel Import tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)


@pytest.mark.admin
@pytest.mark.excel_import
def test_excel_download_template_does_not_require_file(admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin should be able to download the Excel template.
    """
    download_info = admin_excel_import_page.download_template()
    download_path = download_info.value.path()
    assert download_path is not None


@pytest.mark.admin
@pytest.mark.excel_import
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.SPANISH])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_upload_a_correct_spreadsheet(page: Page,
                                      admin_excel_import_page: ExcelImportPage,
                                      suffix: str,
                                      ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet and check that users are saved to the database.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}-{num}"
        email = f"{username}@test.com"
    """
    admin_excel_import_page.ensure_locale(ui_locale_param)
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_test_50_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_msg.text_content()
    expected = "Import completed successfully"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, None, "contains")
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 50 on the success message
    users_table_page = UsersTablePage(page)
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 50", "contains")
    expected = "Created:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 50", "contains")
    expected = "Updated:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 0", "contains")
    # Now let's go to the Users Table page and check if just imported users can be present in the table
    admin_excel_import_page.click_users_tab()
    users_table_page.search_and_wait_for_results(suffix)
    users_table_page.change_number_of_users_per_page_control_top(50)
    # Verifying number of users (expected = 50)
    actual = users_table_page.page_title.text_content()
    expected = "People"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " (50)", "strict")


@pytest.mark.admin
@pytest.mark.excel_import
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.POLISH])
@pytest.mark.usefixtures("cleanup_logout_currently_logged_in_user_on_ui")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_check_full_name_updates_from_excel_are_applied(page: Page,
                                                        admin_excel_import_page: ExcelImportPage,
                                                        suffix: str,
                                                        ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet and check that updates from excel (first and last name)
    for existing user are applied.
    Note: bio field is located in Profile and first and last names are located in User,
    so we need extra case to check.

    Test steps:
        1. Create a user via API
        2. Change password for just created user
        3. Change Profile values for just create user:
            - First name (it should differs from the Excel file)
            - Last name (it should differs from the Excel file)
            - !!! Bio (it should the same as in the Excel file)
        4. Import excel
        5. Check results data on the Excel Import page
        6. Go to Profile View
        7. Check the values got updated

    Username & email are created with this logic:
        username = f"excel-jack-1"
        email = f"{username}@{suffix}.com"
    """
    admin_excel_import_page.ensure_locale(ui_locale_param)
    api_utils = get_api_utils()
    username = "excel-jack-1"
    email = f"{username}@{suffix}.com"
    password = "Ch@ngeme123"
    api_utils.create_user(username, email, password)
    # Now, let's set values, first, last names different from Excel file, bio should be the same
    diff_first_name = "Different from Excel"
    diff_last_name = "Different from Excel"
    same_bio = "Some text for bio watermelon 1"
    _helper_update_profile_via_regular_user(admin_excel_import_page,
                                            page,
                                            ui_locale_param,
                                            username,
                                            password,
                                            email,
                                            diff_first_name,
                                            diff_last_name,
                                            same_bio)
    # Let's log back in as admin to import an excel spreadsheet
    login_page = LoginPage(page)
    login_page.submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now, let's go to the Excel Import page
    login_page.click_additional_excel_import_tab()
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_update_test_2_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_msg.text_content()
    expected = "Import completed successfully"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, None, "contains")
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 1, and updated ones is 1 on the success message
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 2", "contains")
    expected = "Created:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 1", "contains")
    expected = "Updated:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 1", "contains")
    # Now, let's login as the updated user
    admin_excel_import_page.click_logout_and_wait_for_login_page()
    login_page.submit_credentials_success(username, password)
    # Let's enter the Profile View page
    profile_view_page = ProfileViewPage(page)
    profile_view_page.click_profile_tab()
    profile_view_page.assert_profile_basics_visible()
    # Now, let's verify that updated values applied
    expected_first_name = "Excel Jack 1"
    expected_last_name = "Watermelon 1"
    full_name_excel = f"{expected_first_name} {expected_last_name}"
    bio_excel = "Some text for bio watermelon 1"
    profile_view_page.verify_full_name_and_bio_values(full_name_excel, bio_excel)


@pytest.mark.admin
@pytest.mark.excel_import
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.ESTONIAN])
@pytest.mark.usefixtures("cleanup_logout_currently_logged_in_user_on_ui")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_check_bio_updates_from_excel_are_applied(page: Page,
                                                  admin_excel_import_page: ExcelImportPage,
                                                  suffix: str,
                                                  ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet and check that updates from excel (bio)
    for existing user are applied.
    Note: bio field is located in Profile and first and last names are located in User,
    so we need extra case to check.

    Test steps:
        1. Create a user via API
        2. Change password for just created user
        3. Change Profile values for just create use:
            - !!! First name (it should the same as in the Excel file)
            - !!! Last name (it should the same as in the Excel file)
            - Bio (it should differs from the Excel file)
        4. Import excel
        5. Check results data on the Excel Import page
        6. Go to Profile View
        7. Check the values got updated

    Username & email are created with this logic:
        username = f"excel-jack-1"
        email = f"{username}@{suffix}.com"
    """
    admin_excel_import_page.ensure_locale(ui_locale_param)
    api_utils = get_api_utils()
    username = "excel-jack-1"
    email = f"{username}@{suffix}.com"
    password = "Ch@ngeme123"
    api_utils.create_user(username, email, password)
    # Now, let's set values, first, last names different from Excel file, bio should be the same
    same_first_name = "Excel Jack 1"
    same_last_name = "Watermelon 1"
    diff_bio = "Different from Excel fille"
    _helper_update_profile_via_regular_user(admin_excel_import_page,
                                            page,
                                            ui_locale_param,
                                            username,
                                            password,
                                            email,
                                            same_first_name,
                                            same_last_name,
                                            diff_bio)
    # Let's log back in as admin to import an excel spreadsheet
    login_page = LoginPage(page)
    login_page.submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Now, let's go to the Excel Import page
    login_page.click_additional_excel_import_tab()
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_update_test_2_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_msg.text_content()
    expected = "Import completed successfully"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, None, "contains")
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 1, and updated ones is 1 on the success message
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 2", "contains")
    expected = "Created:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 1", "contains")
    expected = "Updated:"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, " 1", "contains")
    # Now, let's login as a updated user
    admin_excel_import_page.click_logout_and_wait_for_login_page()
    login_page.submit_credentials_success(username, password)
    # Let's enter the Profile View page
    profile_view_page = ProfileViewPage(page)
    profile_view_page.click_profile_tab()
    profile_view_page.assert_profile_basics_visible()
    # Now, let's verify that updated values applied
    expected_first_name = "Excel Jack 1"
    expected_last_name = "Watermelon 1"
    full_name_excel = f"{expected_first_name} {expected_last_name}"
    bio_excel = "Some text for bio watermelon 1"
    profile_view_page.verify_full_name_and_bio_values(full_name_excel, bio_excel)


@pytest.mark.admin
@pytest.mark.excel_import
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.FINNISH])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_check_if_results_show_0_when_no_users_to_update_and_create(page: Page,
                                                                    admin_excel_import_page: ExcelImportPage,
                                                                    suffix: str,  # pylint: disable=unused-argument
                                                                    ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet and check that results show 0 when no users to update or create

    Username & email are created with this logic:
        username = {some_user_name_from_excel}
        email = f"{username}@{suffix}.com"
    """
    admin_excel_import_page.ensure_locale(ui_locale_param)
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_update_test_2_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_msg.text_content()
    expected = "Import completed successfully"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, None, "contains")
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 2 on the success message
    users_table_page = UsersTablePage(page)
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 2", "contains")
    expected = "Created:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 2", "contains")
    expected = "Updated:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 0", "contains")

    # Now let's import the same Excel spreadsheet again
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_update_test_2_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 0 on the success message
    users_table_page = UsersTablePage(page)
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 0", "contains")
    expected = "Created:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 0", "contains")
    expected = "Updated:"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, " 0", "contains")
