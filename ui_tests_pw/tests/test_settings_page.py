"""
Tests for the admin Settings page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_settings_page_renders_for_admin(settings_page: Page,
                                         page: Page,
                                         ui_theme_param: Theme,
                                         ui_locale_param: str) -> None:
    """
    Admin user can open the settings page under multiple themes/locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    settings_page.assert_loaded()


@pytest.mark.regular_user
def test_settings_page_not_accessible_for_regular_user(regular_users_page: Page) -> None:
    """
    Regular user should not be able to access the settings page.
    Settings tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)
