"""
Tests for the Stats page (admin only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from conftest import delete_users_by_suffix_via_api
from core.constants import LocaleConsts, ThemeConsts
from pages.users_table_page import UsersTablePage
from pages.stats_page import StatsPage
from utils.theme import Theme
from utils.auth import get_api_utils


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_stats_page_renders_for_admin(user_stats_page: UsersTablePage,
                                      ui_theme_param: Theme,
                                      ui_locale_param: str) -> None:
    """
    Admin user can open the online-users stats page.
    """
    user_stats_page.ensure_theme(ui_theme_param)
    user_stats_page.ensure_locale(ui_locale_param)
    user_stats_page.assert_loaded()
    # Verifying localization
    actual = user_stats_page.page_title.text_content()
    expected = "Users online in the last 5 minutes"
    user_stats_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.regular_user
def test_stats_page_not_rendered_for_regular_user(regular_users_page: UsersTablePage) -> None:
    """
    Regular user can NOT access the stats page.
    User Stats tab is located under Additional tab.
    """
    # Navbar Additional tab is staff-only.
    expect(regular_users_page.addtional_tab).to_have_count(0)


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["cloud"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_deleted_user_is_no_longer_shown(user_stats_page: StatsPage,
                                         suffix: str) -> None:
    """
    Verify that deleted user disappears from the User Stats page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    api_utils = get_api_utils()
    username = f"cloud-{suffix}"
    email = f"{username}@mango.com"
    password = "Ch@ngeme123"
    login_info = api_utils.create_user_and_login(username, email, password)
    # Let's get profile details to simulate UI behavior, so the user becomes shown on the User Stats page
    api_utils.get_profile_details(login_info.get("access"))
    # Now let's check if user is shown on the User Stats page
    user_stats_page.reload()
    user_stats_page.assert_user_was_online_during_last_5_mins(username)
    # Let's delete the user and check if they are no longer displayed on the User Stats page
    delete_users_by_suffix_via_api(email, "email", "strict")
    # Let's reload the page and check the results
    user_stats_page.reload()
    user_stats_page.assert_user_is_not_listed_on_the_page(username)


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize("suffix", ["mango"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_user_disappears_from_user_stats_if_not_active_more_than_5_mins(user_stats_page: StatsPage,
                                                                        suffix: str) -> None:
    """
    Verify that not active for more than 5 minutes user disappears from the User Stats page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    api_utils = get_api_utils()
    username = f"login-via-api-{suffix}"
    email = f"{username}@mango.com"
    password = "Ch@ngeme123"
    login_info = api_utils.create_user_and_login(username, email, password)
    # Let's get profile details to simulate UI behavior, so the user becomes shown on the User Stats page
    api_utils.get_profile_details(login_info.get("access"))
    # Now let's check if user is shown on the User Stats page
    user_stats_page.reload()
    user_stats_page.assert_user_was_online_during_last_5_mins(username)
    # Let's wait 5 minus + a bit more
    user_stats_page.wait_a_bit(300 + 30)
    # Let's reload the page and check the results
    user_stats_page.reload()
    user_stats_page.assert_user_is_not_listed_on_the_page(username)


@pytest.mark.admin
@pytest.mark.longrun
@pytest.mark.parametrize("suffix", ["strawberry"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_user_is_present_in_user_stats_if_active_more_than_5_mins(user_stats_page: StatsPage,
                                                                        suffix: str) -> None:
    """
    Verify that active for more than 5 minutes user is still shown on the User Stats page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    api_utils = get_api_utils()
    username = f"api-login-{suffix}"
    email = f"{username}@strawberry.com"
    password = "Ch@ngeme123"
    login_info = api_utils.create_user_and_login(username, email, password)
    # Let's get profile details to simulate UI behavior, so the user becomes shown on the User Stats page
    api_utils.get_profile_details(login_info.get("access"))
    # Now let's check if user is shown on the User Stats page
    user_stats_page.reload()
    user_stats_page.assert_user_was_online_during_last_5_mins(username)
    # Let's wait 5 minus + a bit more + call get_profile_details() to simulate user activity
    for _ in range(11):
        user_stats_page.wait_a_bit(30)
        api_utils.get_profile_details(login_info.get("access"))
    # Let's reload the page and check the results
    user_stats_page.reload()
    user_stats_page.assert_user_was_online_during_last_5_mins(username)
