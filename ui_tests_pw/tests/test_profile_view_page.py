"""
Tests for the Profile view page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_profile_view_renders_for_regular_user(page: Page,  # pylint: disable=unused-argument
                                               profile_view_page_regular: Page,
                                               ui_theme_param: Theme,
                                               ui_locale_param: str) -> None:
    """
    Regular user should be able to see their own profile under different themes/locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    profile_view_page_regular.assert_profile_basics_visible()


@pytest.mark.admin
def test_profile_view_renders_for_admin(profile_view_page_admin: Page) -> None:
    """
    Admin user should also have a profile view.
    """
    profile_view_page_admin.assert_profile_basics_visible()


@pytest.mark.regular_user
def test_profile_view_has_edit_link(page: Page,
                                    profile_view_page_regular: Page) -> None:
    """
    Profile view page should link to the edit profile form.
    """
    profile_view_page_regular.edit_profile.click()
    page.wait_for_url(re.compile(r".*/profile-edit$"))
    expect(page).to_have_url(re.compile(r".*/profile-edit$"))
