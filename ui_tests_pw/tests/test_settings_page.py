"""Tests for the admin Settings page."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from ..pages.settings_page import SettingsPage
from ..utils.theme import Theme, set_theme
from ..utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_settings_page_renders_for_admin(logged_in_admin: Page, theme: Theme, locale_code: str) -> None:
    """Admin user can open the settings page under multiple themes/locales."""
    page = logged_in_admin
    set_theme(page, theme)
    set_locale(page, locale_code)
    settings = SettingsPage(page)
    settings.open()
    settings.assert_loaded()


@pytest.mark.regular_user
def test_settings_page_not_accessible_for_regular_user(logged_in_regular: Page) -> None:
    """Regular user should not be able to access the settings page."""
    page = logged_in_regular
    settings = SettingsPage(page)
    settings.open()
    # Either redirected away or an error status is shown; we assert that the idle timeout field is not visible.
    expect(page.locator("#idleTimeoutSeconds")).not_to_be_visible()
