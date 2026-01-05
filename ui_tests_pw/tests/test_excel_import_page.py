"""
Tests for the Excel import page (admin-only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from core.constants import LocaleConsts, ThemeConsts
from pages.excel_import_page import ExcelImportPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme


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
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)


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
    Importing a correct Excel spreadsheet.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}-{num}"
        email = f"{username}-{num}@test.com"
        password = "Ch@ngeme123"
    """
    admin_excel_import_page.assert_loaded()
    admin_excel_import_page.import_excel_file_success("test_data/import_template_test_50_users.xlsx")
    # Let's check the success message title
    actual = admin_excel_import_page.success_title.text_content()
    expected = "Result"
    admin_excel_import_page.assert_text_localization(ui_locale_param, actual, expected)
    # Now let's go to the Users Table page and check if just imported users can be present in the table
    admin_excel_import_page.click_users_tab()
    users_table_page = UsersTablePage(page)
    users_table_page.search_and_wait_for_results(suffix)
    users_table_page.change_number_of_users_per_page_control_top(50)
    # Verifying number of users (expected = 50)
    actual = users_table_page.page_title.text_content()
    expected = "People (50)"
    users_table_page.assert_text_localization(ui_locale_param, actual, expected)
