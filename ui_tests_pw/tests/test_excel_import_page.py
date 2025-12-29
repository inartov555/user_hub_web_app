"""
Tests for the Excel import page (admin-only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.excel_import_page import ExcelImportPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_excel_import_page_renders_for_admin(page: Page,
                                             ui_theme_param: Theme,
                                             ui_locale_param: str,
                                             admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin user can open the Excel import page.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    # Verifying if Import & Download buttons are visible
    expect(admin_excel_import_page.import_template_btn).to_be_visible()
    expect(admin_excel_import_page.download_template_btn).to_be_visible()
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
