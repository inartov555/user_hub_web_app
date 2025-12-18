"""
Tests for the Stats page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.stats_page import StatsPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_stats_page_renders_for_admin(page: Page,
                                      user_stats_page: Page,
                                      ui_theme_param: Theme,
                                      ui_locale_param: str) -> None:
    """
    Admin user can open the online-users stats page.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    user_stats_page.assert_loaded()


@pytest.mark.regular_user
def test_stats_page_renders_for_regular_user(page: Page,
                                             regular_users_page: Page) -> None:
    """
    Regular user can NOT access the stats page.
    User Stats tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)
