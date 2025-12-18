"""
Page object for the User Delete Confirm page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class UserDeleteConfirmPage(BasePage):
    """
    Encapsulates the user deletion confirmation page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.confirm_delete = self.page.locator("#confirmDelete")
        self.cancel = self.page.locator("#cancel")

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

    def assert_confirm_delete_loaded(self) -> None:
        """
        Assert that the confirmation UI is visible.
        """
        expect(page).to_have_url(re.compile(r".*/users/confirm-delete$"))
        expect(self.confirm_delete).to_be_visible()
