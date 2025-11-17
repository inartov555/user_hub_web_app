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
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_stats_page_renders_for_admin(logged_in_admin: Page, theme: Theme, locale_code: str) -> None:
    """
    Admin user can open the online-users stats page.
    """
    page = logged_in_admin
    set_theme(page, theme)
    set_locale(page, locale_code)
    stats = StatsPage(page)
    stats.open()
    stats.assert_loaded()


@pytest.mark.regular_user
def test_stats_page_renders_for_regular_user(logged_in_regular: Page) -> None:
    """
    Regular user can also access the stats page (endpoint is authenticated-only).
    """
    stats = StatsPage(logged_in_regular)
    stats.open()
    stats.assert_loaded()
