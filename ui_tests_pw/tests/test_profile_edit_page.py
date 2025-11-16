"""Tests for the Profile edit page."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from ..pages.profile_edit_page import ProfileEditPage
from ..utils.theme import Theme, set_theme
from ..utils.localization import set_locale


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_profile_edit_renders_and_can_save(logged_in_regular: Page, theme: Theme, locale_code: str) -> None:
    """Regular user should be able to edit and save their profile."""
    page = logged_in_regular
    set_theme(page, theme)
    set_locale(page, locale_code)

    edit = ProfileEditPage(page)
    edit.open()
    edit.assert_loaded()
    edit.fill_basic_fields("UI", "Tester", "Bio from automated test.")
    edit.save()
    # No explicit assertion; absence of an error is considered success.


@pytest.mark.regular_user
def test_profile_edit_cancel_returns_to_profile_view(logged_in_regular: Page) -> None:
    """Cancel button should navigate back to profile view."""
    edit = ProfileEditPage(logged_in_regular)
    edit.open()
    edit.cancel()
    assert "profile-view" in logged_in_regular.url
