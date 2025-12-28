"""
Tests for the admin Settings page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect
from django.utils import translation

from pages.settings_page import SettingsPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_settings_page_renders_for_admin(settings_page: SettingsPage,
                                         page: Page,
                                         ui_theme_param: Theme,
                                         ui_locale_param: str) -> None:
    """
    Admin user can open the settings page under multiple themes/locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    settings_page.assert_loaded()
    # Verifying localization
    actual = settings_page.page_title.text_content()
    with translation.override(ui_locale_param.lower()):
        expected = translation.gettext("App Settings")
    assert actual == expected, f"Wrong page title localization; actual '{actual}'; expected '{expected}'"


@pytest.mark.regular_user
def test_settings_page_not_accessible_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not be able to access the settings page.
    Settings tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)
