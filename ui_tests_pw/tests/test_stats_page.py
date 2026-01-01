"""
Tests for the Stats page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from core.constants import LocaleConsts, ThemeConsts
from pages.users_table_page import UsersTablePage


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_stats_page_renders_for_admin(user_stats_page: UsersTablePage,
                                      ui_theme_param: Theme,
                                      ui_locale_param: str) -> None:
    """
    Admin user can open the online-users stats page.
    """
    user_stats_page.ensure_theme(ui_theme_param)
    user_stats_page.ensure_locale(ui_locale_param)
    user_stats_page.assert_loaded()
    # Verifying localization
    actual = user_stats_page.page_title.text_content()
    expected = "Users online in the last 5 minutes"
    user_stats_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.regular_user
def test_stats_page_renders_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user can NOT access the stats page.
    User Stats tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)
