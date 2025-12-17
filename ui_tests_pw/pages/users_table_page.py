"""
Page object for the Users table page.
"""

from __future__ import annotations
from typing import List

from playwright.sync_api import Locator, expect, Page

from .base_page import BasePage


class UsersTablePage(BasePage):
    """
    Encapsulates the Users table view and its sorting / filtering actions.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.SEARCH_INPUT = self.page.locator("#search")
        self.CLEAR_SORT_BTN = self.page.locator("#clearSort")
        self.DELETE_USERS_BTN = self.page.locator("#deleteUsers")

        self.CHECK_ALL_HEADER = self.page.locator('input[data-tag="check-all-rows"]')
        self.USERNAME_HEADER = self.page.locator('button[data-tag="sort-by-username"]')
        self.EMAIL_HEADER = self.page.locator('button[data-tag="sort-by-email"]')
        self.FIRST_NAME_HEADER = self.page.locator('button[data-tag="sort-by-email"]')
        self.LAST_NAME_HEADER = self.page.locator('button[data-tag="sort-by-email"]')
        self.CHANGE_PASSWROD_HEADER = self.page.locator('div[data-tag="changePasswordHeader"]')

        self.CHANGE_PASSWROD_BTN = self.page.locator('button[data-tag="change-password"]')

        self.SORT_LABELS = self.page.locator("thead th span.text-xs")
        self.IS_UPDATING = self.page.locator('span[data-tag="isUpdating"]')

    def open(self) -> None:
        """
        Open the users table page.
        """
        self.goto("/users")

    def wait_isupdating_disappeared(self) -> None:
        """
        There's isUpdating element's text shown while Users Table data is refreshed
        """
        self.IS_UPDATING.wait_for(state="detached", timeout=30000)

    def wait_till_users_table_update_finished(self) -> None:
        """
        Apply a multi-column sort: first by username, then by email.
        """
        self.USERNAME_HEADER.click()
        self.EMAIL_HEADER.click()

    def sort_by_username_then_email(self) -> None:
        """
        Apply a multi-column sort: first by username, then by email.
        """
        self.USERNAME_HEADER.click()
        self.EMAIL_HEADER.click()

    def get_sort_order_labels(self) -> List[str]:
        """
        Return the list of #1, #2 labels rendered for multi-column sort.
        """
        return [self.SORT_LABELS.nth(i).inner_text().strip() for i in range(self.SORT_LABELS.count())]

    def assert_admin_controls_visible(self) -> None:
        """
        Assert that admin-only controls on the users table are visible.
        """
        expect(self.delete_users_button).to_be_visible()
        # Admins see the bulk select checkbox in the header.
        expect(self.CHECK_ALL_HEADER).to_be_visible()
        expect(self.CHANGE_PASSWROD_HEADER).to_be_visible()

    def assert_admin_controls_hidden_for_regular_user(self) -> None:
        """
        Assert that admin-only controls are hidden for a regular user.
        """
        expect(self.delete_users_button).not_to_be_visible()
        # No header-level checkbox for regular user.
        expect(self.CHECK_ALL_HEADER).to_have_count(0)
        expect(self.CHANGE_PASSWROD_HEADER).to_have_count(0)
