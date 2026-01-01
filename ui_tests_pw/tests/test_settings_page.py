"""
Tests for the admin Settings page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from core.constants import LocaleConsts, ThemeConsts
from pages.settings_page import SettingsPage
from pages.users_table_page import UsersTablePage
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
