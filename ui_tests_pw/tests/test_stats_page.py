"""
Tests for the Stats page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect
from django.utils import translation

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
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
    # Verifying localization
    actual = user_stats_page.page_title.text_content()
    with translation.override(ui_locale_param.lower()):
        expected = translation.gettext("Users online in the last 5 minutes")
    assert actual == expected, f"Wrong page title localization; actual '{actual}'; expected '{expected}'"


@pytest.mark.regular_user
def test_stats_page_renders_for_regular_user(regular_users_page: Page) -> None:
    """
    Regular user can NOT access the stats page.
    User Stats tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)
