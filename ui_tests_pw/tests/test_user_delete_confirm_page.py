"""
Tests for the User Delete Confirm page (admin only).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from core.constants import LocaleConsts, ThemeConsts
from pages.user_delete_confirm_page import UserDeleteConfirmPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.parametrize("suffix", ["tomato"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_admin_can_navigate_to_delete_confirm(page: Page,
                                              admin_users_page: UsersTablePage,
                                              ui_locale_param: str,
                                              ui_theme_param: Theme,
                                              suffix: str) -> None:
    """
    Admin should be able to select users and reach the delete-confirm page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    username = f"ui-test-{suffix}"
    admin_users_page.ensure_theme(ui_theme_param)
    admin_users_page.ensure_locale(ui_locale_param)
    admin_users_page.search_and_wait_for_results(username)
    # Let's be on the safe side and check if there's the only 1 user in the search results
    expect(admin_users_page.check_rows).to_have_count(1)
    # Now, let's check the users for further deletion
    admin_users_page.check_all_header.click()
    # Verifying that the Confirm deletion page is shown after pressing the Delete Selected button
    admin_users_page.click_delete_users_and_wait_confirm_delete_page()
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.assert_confirm_delete_loaded()
    # Verifying localization
    actual = confirm_page.page_title.text_content()
    expected = "Confirm deletion"
    confirm_page.assert_text_localization(ui_locale_param, actual, expected)
    # Now let's check deleting the user from UI
    confirm_page.click_top_confirm_delete_success()
    # Verifying that the user is actually deleted
    admin_users_page.search_and_wait_for_results(username)
    expect(admin_users_page.check_rows).to_have_count(0)


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["potato"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_admin_can_cancel_delete_confirm(page: Page,
                                         admin_users_page: UsersTablePage,
                                         suffix: str) -> None:
    """
    Cancel button on delete-confirm page should navigate back to the Users Table page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    username = f"ui-test-{suffix}"
    admin_users_page.search_and_wait_for_results(username)
    admin_users_page.check_all_header.click()
    admin_users_page.click_delete_users_and_wait_confirm_delete_page()
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.click_top_cancel()
    # Verifying that the user actually exists
    admin_users_page.search_and_wait_for_results(username)
    expect(admin_users_page.check_rows).to_have_count(1)
