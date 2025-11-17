"""
Page object for the User Delete Confirm page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class UserDeleteConfirmPage(BasePage):
    """
    Encapsulates the user deletion confirmation page.
    """

    def open(self) -> None:
        """
        Open the confirm-delete page directly.
        """
        self.goto("/users/confirm-delete")

    def confirm(self) -> None:
        """
        Click the confirm-delete button.
        """
        self.page.locator("#confirmDelete").click()

    def cancel(self) -> None:
        """
        Click the cancel button.
        """
        self.page.locator("#cancel").click()

    def assert_loaded(self) -> None:
        """
        Assert that the confirmation UI is visible.
        """
        expect(self.page.locator("text=Delete users")).to_be_visible()
