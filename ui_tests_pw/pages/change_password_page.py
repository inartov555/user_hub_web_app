"""
Page object for the Change Password page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ChangePasswordPage(BasePage):
    """
    Encapsulates the change-password form for a user.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.password = self.page.locator("#password")
        self.confirm_password = self.page.locator("#confirmPassword")
        self.submit = self.page.locator("form button[type='submit']")
        self.error = self.page.locator("p.text-red-600")

    def open_for_user(self, user_id: int) -> None:
        """
        Open the change-password page for a given user id.
        """
        self.goto(f"/users/{user_id}/change-password")

    def fill_passwords(self, password: str, confirm: str) -> None:
        """
        Fill the new password and confirmation fields.
        """
        self.password.fill(password)
        self.confirm_password.fill(confirm)

    def submit(self) -> None:
        """
        Submit the change-password form.
        """
        self.submit.click()

    def assert_error_visible(self) -> None:
        """
        Assert that an error is shown (e.g. when not allowed).
        """
        expect(self.error).to_be_visible()
