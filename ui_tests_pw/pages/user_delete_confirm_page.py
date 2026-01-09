"""
Page object for the User Delete Confirm page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class UserDeleteConfirmPage(BasePage):
    """
    Page object for the User Delete Confirm page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.confirm_delete_top = self.page.locator("#confirmDeleteTop")
        self.confirm_delete_bottom = self.page.locator("#confirmDeleteBottom")
        self.cancel_top = self.page.locator("#cancelTop")
        self.cancel_bottom = self.page.locator("#cancelBottom")

    def open(self) -> None:
        """
        Open the confirm-delete page directly.
        """
        self.goto("/users/confirm-delete")
        self.verify_confirm_user_delete_page_uri_is_open()

    def assert_confirm_delete_loaded(self) -> None:
        """
        Assert that the confirmation UI is visible.
        """
        self.verify_confirm_user_delete_page_uri_is_open()
        expect(self.confirm_delete_top).to_be_visible()
        expect(self.confirm_delete_bottom).to_be_visible()
        expect(self.cancel_top).to_be_visible()
        expect(self.cancel_bottom).to_be_visible()

    def click_top_cancel(self) -> None:
        """
        Clicking the top cancel button and waiting for the /users page to load
        """
        self.cancel_top.click()
        self.verify_users_table_page_uri_is_open()

    def click_top_confirm_delete_success(self) -> None:
        """
        Clicking the top confirm delete button and waiting for the /users page to load
        """
        self.confirm_delete_top.click()
        self.verify_users_table_page_uri_is_open()

    def click_top_confirm_delete_error(self) -> None:
        """
        Clicking the top confirm delete button and ending up on the Confirm Delete page with an error
        """
        self.confirm_delete_top.click()
        self.assert_confirm_delete_loaded()
        self.assert_error_visible()
