"""
Page object for the Reset Password page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class ResetPasswordPage(BasePage):
    """
    Encapsulates the reset-password page.
    """

    def open(self) -> None:
        """
        Open the reset password page.
        """
        self.goto("/reset-password")

    def request_reset(self, email: str) -> None:
        """
        Submit the reset-password form with the given email.
        """
        self.page.fill("input[type='email']", email)
        self.page.locator("form button[type='submit']").click()

    def assert_success_or_error(self) -> None:
        """
        Assert that either a success message or error is visible.
        """
        expect(self.page.locator("div[role='alert']")).to_be_visible()
