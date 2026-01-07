"""
Tests for the Profile edit page.
"""

from __future__ import annotations
import random
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from core.constants import LocaleConsts, ThemeConsts
from pages.profile_edit_page import ProfileEditPage
from pages.profile_view_page import ProfileViewPage
from pages.login_page import LoginPage
from utils.theme import Theme


@pytest.mark.regular_user
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.admin
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_profile_edit_renders_and_can_save(profile_edit_page_regular: ProfileEditPage,
                                           page: Page,
                                           ui_theme_param: Theme,
                                           ui_locale_param: str) -> None:
    """
    Regular user should be able to edit and save their profile.
    """
    rand_num = random.randint(0, 1000)
    avatars = list(Path("test_data/avatars/").glob("*.*"))
    avatar_path = str(random.choice(avatars))
    edit_data = {"firstName": f"UI_{rand_num}",
                 "lastName": f"Tester_{rand_num}",
                 "bio": f"Bio from automated test._{rand_num}"}

    profile_edit_page_regular.ensure_theme(ui_theme_param)
    profile_edit_page_regular.ensure_locale(ui_locale_param)
    profile_edit_page_regular.assert_loaded()
    # Verifying localization
    actual = profile_edit_page_regular.page_title.text_content()
    expected = "Edit profile"
    profile_edit_page_regular.assert_text_localization(ui_locale_param, actual, expected)
    # Now let's check if data are saved
    profile_edit_page_regular.fill_basic_fields(edit_data.get("firstName"),
                                                edit_data.get("lastName"),
                                                edit_data.get("bio"),
                                                avatar_path)
    profile_edit_page_regular.click_save_and_wait_profile_view()
    profile_view_page = ProfileViewPage(page)

    default_avatar = ".*placehold.co/\d+x\d+\?text=.*"
    src_to_check = f".*/media/avatars/user_\d+/.*{Path(avatar_path).suffix}"
    profile_view_page.assert_avatar_in_profile_view(src_to_check)
    profile_view_page.assert_avatar_not_in_profile_view(default_avatar)

    # Verifying if changed values have been applied and are displayed in the Preview Profile page
    full_name = "{} {}".format(edit_data.get("firstName"), edit_data.get("lastName"))  # pylint: disable=consider-using-f-string
    expect(profile_view_page.full_name).to_have_text(full_name)
    expect(profile_view_page.bio).to_have_text(edit_data.get("bio"))


@pytest.mark.regular_user
@pytest.mark.admin
def test_profile_edit_cancel_returns_to_profile_view(profile_edit_page_regular: ProfileEditPage) -> None:
    """
    Cancel button should navigate back to profile view.
    """
    profile_edit_page_regular.click_cancel_and_wait_profile_view()


@pytest.mark.regular_user
@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["flower"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_new_avatar_picture_shown_after_uploading_a_picture(login_page: LoginPage,
                                                            page: Page,
                                                            suffix: str) -> None:
    """
    Verify that:
        1. Default avatar when user never changed it
        2. Check new avatar picture in the Profile View page
        3. Check new avatar picture in the Profile Edit page

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    # Full default avatar name looks like this:
    #   https://placehold.co/160x160?text=TU
    # Full picture name looks like this:
    #   http://localhost:5173/media/avatars/user_1138/ef63caca-12ac-4fe0-b6b1-fbe27c75c13b.jpg
    username = f"ui-test-{suffix}"
    password = "Ch@ngeme123"
    # Deafult avatar before setting any picture
    default_avatar = ".*placehold.co/\d+x\d+\?text=.*"
    rand_num = random.randint(0, 999)
    avatars = list(Path("test_data/avatars/").glob("*.*"))
    avatar_path = str(random.choice(avatars))
    # The file extenion is preserved when saved, but the name itself changes
    src_to_check = f".*/media/avatars/user_\d+/.*{Path(avatar_path).suffix}"
    edit_data = {"firstName": f"Tester {rand_num}",
                 "lastName": f"UI_{rand_num}",
                 "bio": f"The bio from the automated test._{rand_num}"}

    # Let's check that default avatar is shown before change
    login_page.submit_credentials_success(username, password)
    login_page.click_profile_tab()

    profile_view_page = ProfileViewPage(page)
    profile_view_page.assert_avatar_in_profile_view(default_avatar)
    profile_view_page.click_edit_button()

    profile_edit_page = ProfileEditPage(page)
    profile_edit_page.assert_avatar_in_profile_edit(default_avatar)
    # Now, let's set a new avatar
    profile_edit_page.fill_basic_fields(edit_data.get("firstName"),
                                        edit_data.get("lastName"),
                                        edit_data.get("bio"),
                                        avatar_path)
    profile_edit_page.click_save_and_wait_profile_view()
    profile_view_page.assert_avatar_in_profile_view(src_to_check)
    profile_view_page.assert_avatar_not_in_profile_view(default_avatar)
    profile_view_page.click_edit_button()
    profile_edit_page.assert_avatar_in_profile_edit(src_to_check)
    profile_edit_page.assert_avatar_not_in_profile_edit(default_avatar)
