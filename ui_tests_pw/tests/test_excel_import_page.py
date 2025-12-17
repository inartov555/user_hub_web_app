"""
Tests for the Excel import page (admin-only).
"""

from __future__ import annotations
import os

import pytest
from playwright.sync_api import Page, expect

from pages.excel_import_page import ExcelImportPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme", ["light", "dark"])
@pytest.mark.parametrize("ui_locale", ["en-US", "uk-UA"])
def test_excel_import_page_renders_for_admin(logged_in_admin: Page,
                                             ui_theme: Theme,
                                             ui_locale: str,
                                             admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin user can open the Excel import page.
    """
    page = logged_in_admin
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    # Verifying if Import & Download buttons are visible
    expect(admin_excel_import_page.import_template_btn).to_be_visible()
    expect(admin_excel_import_page.download_template_btn).to_be_visible()


@pytest.mark.regular_user
def test_excel_import_page_not_visible_in_nav_for_regular_user(logged_in_regular: Page,  # pylint: disable=unused-argument
                                                               regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not see the Additional/Import from Excel nav items.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)


@pytest.mark.admin
def test_excel_download_template_does_not_require_file(logged_in_admin: Page,  # pylint: disable=unused-argument
                                                       tmp_path: os.PathLike[str],  # pylint: disable=unused-argument
                                                       admin_excel_import_page: ExcelImportPage) -> None:
    """
    Admin should be able to download the Excel template.
    """
    download_info = admin_excel_import_page.download_template()
    download_path = download_info.value.path()
    assert download_path is not None
