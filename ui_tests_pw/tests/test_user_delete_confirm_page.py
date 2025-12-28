"""
Tests for the User Delete Confirm page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect
from django.utils import translation

from pages.user_delete_confirm_page import UserDeleteConfirmPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.parametrize("suffix", ["one"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_admin_can_navigate_to_delete_confirm(page: Page,
                                              admin_users_page: UsersTablePage,
                                              ui_locale_param: str,
                                              ui_theme_param: Theme,
                                              suffix,
                                             ) -> None:
    """
    Admin should be able to select users and reach the delete-confirm page.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
    """
    username = f"ui-test-{suffix}"
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    admin_users_page.search_and_wait_for_results(username)
    # Let's be on the safe side and check if there's the only 1 user in the search results
    expect(admin_users_page.check_rows).to_have_count(1)
    # Now, let's check the users for further deletion
    admin_users_page.check_all_header.click()
    # Verifying that the Confirm deletion page is shown after pressing the Delete Selected button
    admin_users_page.delete_users_btn.click()
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.assert_confirm_delete_loaded()
    # Verifying localization
    actual = confirm_page.page_title.text_content()
    with translation.override(ui_locale_param.lower()):
        expected = translation.gettext("Confirm deletion")
    assert actual == expected, f"Wrong page title localization; actual '{actual}'; expected '{expected}'"
    # Now let's check deleting the user from UI
    confirm_page.confirm_delete.click()
    # Verifying that user is deleted
    # User is redirected to the /users page after successful deletion
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    # Verifying that the user is actually deleted
    admin_users_page.search_and_wait_for_results(username)
    expect(admin_users_page.check_rows).to_have_count(0)


@pytest.mark.admin
@pytest.mark.parametrize("suffix", ["one"])
@pytest.mark.usefixtures("setup_create_users_by_suffix")
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_admin_can_cancel_delete_confirm(page: Page,
                                         admin_users_page: UsersTablePage,
                                         suffix,
                                        ) -> None:
    """
    Cancel button on delete-confirm page should navigate back to /users.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
    """
    username = f"ui-test-{suffix}"
    admin_users_page.search_and_wait_for_results(username)
    admin_users_page.check_all_header.click()
    admin_users_page.delete_users_btn.click()
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.cancel.click()
    # Verifying that user is redirected to the /users page
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    # Verifying that the user actually exists
    admin_users_page.search_and_wait_for_results(username)
    expect(admin_users_page.check_rows).to_have_count(1)
