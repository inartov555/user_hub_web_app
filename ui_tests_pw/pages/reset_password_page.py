"""
Page object for the Reset Password page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ResetPasswordPage(BasePage):
    """
    Encapsulates the reset-password page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h1")
        self.email = self.page.locator("#email")
        self.submit = self.page.locator("form button[type='submit']")
        self.reset_pswd_info_msg = self.page.locator("p[data-tag='resetPassInfoMsg']")

    def open(self) -> None:
        """
        Open the reset password page.
        """
        self.goto("/reset-password")

    def request_reset(self, email: str) -> None:
        """
        Submit the reset-password form with the given email.
        """
        self.email.fill(email)
        self.submit.click()

    def assert_info_message(self) -> None:
        """
        Assert that reset password info message is visible.
        """
        expect(self.reset_pswd_info_msg).to_be_visible()
