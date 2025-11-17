"""
Tests for the User Delete Confirm page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.user_delete_confirm_page import UserDeleteConfirmPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_admin_can_navigate_to_delete_confirm(logged_in_admin: Page,  # pylint: disable=unused-argument
                                              theme: Theme,  # pylint: disable=unused-argument
                                              page: Page,
                                              admin_users_page: UsersTablePage,  # pylint: disable=unused-argument
                                              locale_code: str  # pylint: disable=unused-argument
                                             ) -> None:
    """
    Admin should be able to select users and reach the delete-confirm page.
    """
    # Select first row.
    page.locator("tbody tr input[type='checkbox']").first.check()
    page.locator("#deleteUsers").click()
    expect(page).to_have_url("**/users/confirm-delete")
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.assert_loaded()


@pytest.mark.admin
def test_admin_can_cancel_delete_confirm(logged_in_admin: Page) -> None:
    """
    Cancel button on delete-confirm page should navigate back to /users.
    """
    page = logged_in_admin
    users = UsersTablePage(page)
    users.open()
    page.locator("tbody tr input[type='checkbox']").first.check()
    page.locator("#deleteUsers").click()
    confirm_page = UserDeleteConfirmPage(page)
    confirm_page.cancel()
    expect(page).to_have_url("**/users")
