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
        self.search_input = self.page.locator("#search")
        self.clear_sort_btn = self.page.locator("#clearSort")
        self.delete_users_btn = self.page.locator("#deleteUsers")

        self.check_all_header = self.page.locator('input[data-tag="check-all-rows"]')
        self.username_header = self.page.locator('button[data-tag="sort-by-username"]')
        self.email_header = self.page.locator('button[data-tag="sort-by-email"]')
        self.first_name_header = self.page.locator('button[data-tag="sort-by-email"]')
        self.last_name_header = self.page.locator('button[data-tag="sort-by-email"]')
        self.change_password_header = self.page.locator('div[data-tag="changePasswordHeader"]')

        self.change_password_btn = self.page.locator('button[data-tag="change-password"]')

        self.sort_labels = self.page.locator("thead th span.text-xs")
        self.is_updating = self.page.locator('span[data-tag="isUpdating"]')

    def open(self) -> None:
        """
        Open the users table page.
        """
        self.goto("/users")

    def wait_till_users_table_update_finished(self) -> None:
        """
        There's isUpdating element's text shown while Users Table data is refreshed
        """
        self.is_updating.wait_for(state="detached", timeout=30000)

    def sort_by_username_then_email(self) -> None:
        """
        Apply a multi-column sort: first by username, then by email.
        """
        self.username_header.click()
        self.email_header.click()

    def get_sort_order_labels(self) -> List[str]:
        """
        Return the list of #1, #2 labels rendered for multi-column sort.
        """
        return [self.sort_labels.nth(i).inner_text().strip() for i in range(self.sort_labels.count())]

    def assert_admin_controls_visible(self) -> None:
        """
        Assert that admin-only controls on the users table are visible.
        """
        expect(self.delete_users_btn).to_be_visible()
        # Admins see the bulk select checkbox in the header.
        expect(self.check_all_header).to_be_visible()
        expect(self.change_password_header).to_be_visible()

    def assert_admin_controls_hidden_for_regular_user(self) -> None:
        """
        Assert that admin-only controls are hidden for a regular user.
        """
        expect(self.delete_users_btn).not_to_be_visible()
        # No header-level checkbox for regular user.
        expect(self.check_all_header).to_have_count(0)
        expect(self.change_password_header).to_have_count(0)
