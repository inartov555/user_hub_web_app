"""
Tests for the Profile view page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from core.constants import LocaleConsts, ThemeConsts
from pages.profile_view_page import ProfileViewPage
from utils.theme import Theme


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_profile_view_renders_for_regular_user(profile_view_page_regular: ProfileViewPage,
                                               ui_theme_param: Theme,
                                               ui_locale_param: str) -> None:
    """
    Regular user should be able to see their own profile under different themes/locales.
    """
    profile_view_page_regular.ensure_theme(ui_theme_param)
    profile_view_page_regular.ensure_locale(ui_locale_param)
    profile_view_page_regular.assert_profile_basics_visible()
    # Verifying localization
    actual = profile_view_page_regular.page_title.text_content()
    expected = "Profile"
    profile_view_page_regular.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.admin
def test_profile_view_renders_for_admin(profile_view_page_admin: ProfileViewPage) -> None:
    """
    Admin user should also have a profile view.
    """
    profile_view_page_admin.assert_profile_basics_visible()


@pytest.mark.regular_user
def test_profile_view_has_edit_link(page: Page,
                                    profile_view_page_regular: ProfileViewPage) -> None:
    """
    Profile view page should link to the edit profile form.
    """
    profile_view_page_regular.edit_profile.click()
    page.wait_for_url(re.compile(r".*/profile-edit$"))
    expect(page).to_have_url(re.compile(r".*/profile-edit$"))
