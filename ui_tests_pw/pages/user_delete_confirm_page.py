"""
Page object for the User Delete Confirm page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page

from .base_page import BasePage


class UserDeleteConfirmPage(BasePage):
    """
    Encapsulates the user deletion confirmation page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.confirm_delete_top = self.page.locator("#confirmDeleteTop")
        self.confirm_delete_bottom = self.page.locator("#confirmDeleteBottom")
        self.cancel_top = self.page.locator("#cancelTop")
        self.cancel_bottom = self.page.locator("#cancelBottom")

    def open(self) -> None:
        """
        Open the confirm-delete page directly.
        """
        self.goto("/users/confirm-delete")

    def assert_confirm_delete_loaded(self) -> None:
        """
        Assert that the confirmation UI is visible.
        """
        expect(self.page).to_have_url(re.compile(r".*/users/confirm-delete$"))
        expect(self.confirm_delete_top).to_be_visible()
        expect(self.confirm_delete_bottom).to_be_visible()
        expect(self.cancel_top).to_be_visible()
        expect(self.cancel_bottom).to_be_visible()
