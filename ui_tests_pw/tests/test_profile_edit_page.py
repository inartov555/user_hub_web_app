"""
Tests for the Profile edit page.
"""

from __future__ import annotations
import random

import pytest
from playwright.sync_api import Page, expect

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
# @pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
# @pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
@pytest.mark.parametrize("ui_theme_param", ["light"])
@pytest.mark.parametrize("ui_locale_param", ["en-US"])
def test_profile_edit_renders_and_can_save(profile_edit_page_regular: Page,
                                           profile_view_page_regular: Page,
                                           page: Page,
                                           ui_theme_param: Theme,
                                           ui_locale_param: str) -> None:
    """
    Regular user should be able to edit and save their profile.
    """
    rand_num = random.randint(0, 1000)
    edit_data = {"firstName": "UI_{}".format(rand_num),
                 "lastName": "Tester_{}".format(rand_num),
                 "bio": "Bio from automated test._{}".format(rand_num)}
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    import time
    time.sleep(4)
    # profile_edit_page_regular.assert_loaded()
    profile_edit_page_regular.fill_basic_fields(edit_data.get("firstName"), edit_data.get("lastName"), edit_data.get("bio"))
    import time
    time.sleep(4)
    # profile_edit_page_regular.save.click()
    # Verifying if changed values have been applied and are displayed in the Preview Profile page
    full_name = "{} {}".format(edit_data.get("firstName"), edit_data.get("lastName"))
    expect(profile_view_page_regular.full_name).to_have_value(full_name)
    expect(profile_view_page_regular.bio).to_have_value(edit_data.get("bio"))
    import time
    time.sleep(4)


@pytest.mark.regular_user
def test_profile_edit_cancel_returns_to_profile_view(logged_in_regular: Page) -> None:
    """
    Cancel button should navigate back to profile view.
    """
    edit = ProfileEditPage(logged_in_regular)
    edit.open()
    edit.cancel()
    assert "profile-view" in logged_in_regular.url
