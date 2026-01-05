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

        self.page_title = self.page.locator("h2")
        self.email = self.page.locator("#email")
        self.submit = self.page.locator("form button[type='submit']")
        self.reset_pswd_info_msg = self.page.locator("p[data-tag='resetPassInfoMsg']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")
        self.login = self.page.locator("a[href='/login']")

    def open(self) -> None:
        """
        Open the reset password page.
        """
        self.goto("/reset-password")
        self.verify_reset_password_page_uri_is_open()

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

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed /reset-password page.
        """
        expect(self.error).to_be_visible()

    def click_sign_in_link(self) -> None:
        """
        Clicking the Sign in link on the Reset Password page
        """
        self.login.click()
        self.verify_login_page_uri_is_open()
