"""
Tests for the Excel import page (admin-only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from core.constants import LocaleConsts, ThemeConsts
from pages.excel_import_page import ExcelImportPage
from pages.users_table_page import UsersTablePage
from pages.profile_view_page import ProfileViewPage
from pages.change_password_page import ChangePasswordPage
from pages.login_page import LoginPage
from utils.theme import Theme
from utils.auth import get_api_utils


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
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
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, "strict")
    # Verify title of results block
    actual = admin_excel_import_page.success_msg.text_content()
    expected = "Import completed successfully"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected, "contains")


@pytest.mark.regular_user
def test_excel_import_page_not_visible_in_nav_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not see the Additional/Import from Excel nav items.
    Excel Import tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)


@pytest.mark.admin
def test_excel_download_template_does_not_require_file(admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin should be able to download the Excel template.
    """
    download_info = admin_excel_import_page.download_template()
    download_path = download_info.value.path()
    assert download_path is not None


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.ENGLISH_US])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_upload_a_correct_spreadsheet(page: Page,
                                      admin_excel_import_page: ExcelImportPage,
                                      suffix: str,
                                      ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet and check that users are saved to the database.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}-{num}"
        email = f"{username}-{num}@test.com"
    """
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_test_50_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 50 on the success message
    users_table_page = UsersTablePage(page)
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed: 50"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    expected = "Created: 50"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    expected = "Updated: 0"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    # Now let's go to the Users Table page and check if just imported users can be present in the table
    admin_excel_import_page.click_users_tab()
    users_table_page.search_and_wait_for_results(suffix)
    users_table_page.change_number_of_users_per_page_control_top(50)
    # Verifying number of users (expected = 50)
    actual = users_table_page.page_title.text_content()
    expected = "People (50)"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.parametrize("ui_locale_param", [LocaleConsts.ENGLISH_US])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_check_that_updates_from_excel_are_applied(page: Page,
                                                   admin_excel_import_page: ExcelImportPage,
                                                   suffix: str,
                                                   ui_locale_param: str) -> None:
    """
    Importing a correct Excel spreadsheet.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}-{num}"
        email = f"{username}-{num}@test.com"
    """
    api_utils = get_api_utils()
    username = "excel-jack-1"
    email = f"{username}@watermelon.com"
    password = "Ch@ngeme123"
    api_utils.create_user(username, email, password)
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/excel_import/import_template_update_test_2_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Verifying number of created users is 1, and updated ones is 1 on the success message
    users_table_page = UsersTablePage(page)
    actual = admin_excel_import_page.success_body.text_content()
    expected = "Processed: 2"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    expected = "Created: 1"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    expected = "Updated: 1"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected, "contains")
    # Now let's go to the Users Table page and check if just imported users can be present in the table
    admin_excel_import_page.click_users_tab()
    users_table_page.search_and_wait_for_results(email)
    # Verifying number of users (expected = 1)
    actual = users_table_page.page_title.text_content()
    expected = "People (1)"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected)
    users_table_page.change_password_btn.nth(0).click()
    # Set password for previously created user
    change_password_page = ChangePasswordPage(page)
    change_password_page.assert_change_password_is_loaded()
    change_password_page.change_password_success(password)
    # Now, let's login as a updated user
    users_table_page.click_logout_and_wait_for_login_page()
    login_page = LoginPage(page)
    login_page.submit_credentials_success(username, password)
    # Let's enter the Profile View page
    profile_view_page = ProfileViewPage(page)
    profile_view_page.click_profile_tab()
    profile_view_page.assert_profile_basics_visible()
    # Now, let's verify that updated values applied
    full_name_excel = "{} {}".format("Excel Jack 1", "Watermelon 1")
    bio_excel = "Some text for bio watermelon 1"
    profile_view_page.verify_full_name_and_bio_values(full_name_excel, bio_excel)
