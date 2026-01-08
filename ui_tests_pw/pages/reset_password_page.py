"""
Page object for the Reset Password page.
"""

from __future__ import annotations

from playwright.sync_api import Page

from .base_page import BasePage


class ResetPasswordPage(BasePage):
    """
    Page object for the Reset Password page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.email = self.page.locator("#email")
        self.submit = self.page.locator("form button[type='submit']")
        self.reset_pswd_info_msg = self.page.locator("div[data-tag='simpleInfoMessage']")
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

    def click_sign_in_link(self) -> None:
        """
        Clicking the Log in link on the Reset Password page
        """
        self.login.click()
        self.verify_login_page_uri_is_open()
