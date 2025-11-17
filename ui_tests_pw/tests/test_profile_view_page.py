"""
Tests for the Profile view page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.profile_view_page import ProfileViewPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_profile_view_renders_for_regular_user(logged_in_regular: Page, theme: Theme, locale_code: str) -> None:
    """
    Regular user should be able to see their own profile under different themes/locales.
    """
    page = logged_in_regular
    set_theme(page, theme)
    set_locale(page, locale_code)
    profile = ProfileViewPage(page)
    profile.open()
    profile.assert_profile_basics_visible()


@pytest.mark.admin
def test_profile_view_renders_for_admin(logged_in_admin: Page) -> None:
    """
    Admin user should also have a profile view.
    """
    profile = ProfileViewPage(logged_in_admin)
    profile.open()
    profile.assert_profile_basics_visible()


@pytest.mark.regular_user
def test_profile_view_has_edit_link(logged_in_regular: Page) -> None:
    """
    Profile view page should link to the edit profile form.
    """
    profile = ProfileViewPage(logged_in_regular)
    profile.open()
    profile.click_edit_profile()
    expect(logged_in_regular).to_have_url("**/profile-edit")
