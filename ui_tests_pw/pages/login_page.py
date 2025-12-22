"""
Page object for the Login page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page, PlaywrightTimeoutError

from .base_page import BasePage


class LoginPage(BasePage):
    """
    Encapsulates interactions with the login page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # /users page after logging in
        self.users_tab = self.page.locator('#users')

        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.submit = self.page.locator("form button[type='submit']")
        self.error = self.page.locator("p.text-red-600")

        self.cookie_consent_title = self.page.locator("div[data-tag='cookieConsentTitle']")
        self.cookie_consent_body = self.page.locator("p[data-tag='cookieConsentBody']")
        self.cookie_consent_accept = self.page.locator("#cookieAccept")

        self.signup = self.page.locator("a[href='/signup']")
        self.forgot_password = self.page.locator("a[href='/reset-password']")

    def open(self) -> None:
        """
        Navigate to the login page.
        """
        self.goto("/login")

    def fill_credentials(self, username: str, password: str) -> None:
        """
        Fill the username and password fields.

        Args:
            username: Username to type into the form.
            password: Password to type into the form.
        """
        self.username.fill(username)
        self.password.fill(password)

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed login attempt.
        """
        expect(self.error).to_be_visible()

    def assert_on_login_page(self) -> None:
        """
        Assert that the current page is still the login page.
        """
        expect(self.username).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/login$"))

    def accept_cookie_consent_if_present(self) -> None:
        """
        Handling cookie consent overlay, if present
        """
        try:
            self.cookie_consent_accept.wait_for(state="visible")
        except PlaywrightTimeoutError:
            return  # No cookie consent overlay
        self.cookie_consent_accept.click()
        expect(self.cookie_consent_accept).to_be_hidden()
