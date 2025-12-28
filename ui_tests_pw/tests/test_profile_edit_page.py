"""
Tests for the Profile edit page.
"""

from __future__ import annotations
import random
import re

import pytest
from playwright.sync_api import Page, expect
from django.utils import translation

from pages.profile_view_page import ProfileViewPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_profile_edit_renders_and_can_save(profile_edit_page_regular: Page,
                                           page: Page,
                                           ui_theme_param: Theme,
                                           ui_locale_param: str) -> None:
    """
    Regular user should be able to edit and save their profile.
    """
    rand_num = random.randint(0, 1000)
    edit_data = {"firstName": "UI_{}".format(rand_num),  # pylint: disable=consider-using-f-string
                 "lastName": "Tester_{}".format(rand_num),  # pylint: disable=consider-using-f-string
                 "bio": "Bio from automated test._{}".format(rand_num)}  # pylint: disable=consider-using-f-string
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    profile_edit_page_regular.assert_loaded()
    # Verifying localization
    actual = profile_edit_page_regular.page_title.text_content()
    with translation.override(ui_locale_param.lower()):
        expected = translation.gettext("Edit profile")
    assert actual == expected, f"Wrong page title localization; actual '{actual}'; expected '{expected}'"
    # Now let's check if data are saved
    profile_edit_page_regular.fill_basic_fields(edit_data.get("firstName"), edit_data.get("lastName"), edit_data.get("bio"))
    profile_edit_page_regular.save.click()
    page.wait_for_url(re.compile(r".*/profile-view$"))
    profile_view_page = ProfileViewPage(page)
    # Verifying if changed values have been applied and are displayed in the Preview Profile page
    full_name = "{} {}".format(edit_data.get("firstName"), edit_data.get("lastName"))  # pylint: disable=consider-using-f-string
    expect(profile_view_page.full_name).to_have_text(full_name)
    expect(profile_view_page.bio).to_have_text(edit_data.get("bio"))


@pytest.mark.regular_user
def test_profile_edit_cancel_returns_to_profile_view(page: Page,
                                                     profile_edit_page_regular: Page) -> None:
    """
    Cancel button should navigate back to profile view.
    """
    profile_edit_page_regular.cancel.click()
    page.wait_for_url(re.compile(r".*/profile-view$"))
    expect(page).to_have_url(re.compile(r".*/profile-view$"))
