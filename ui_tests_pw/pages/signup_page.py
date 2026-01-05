"""
Page object for the Signup page.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class SignupPage(BasePage):
    """
    Encapsulates the registration / signup page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.email = self.page.locator("#email")
        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.save = self.page.locator("#create")
        self.login = self.page.locator("a[href='/login']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")

    def open(self) -> None:
        """
        Open the signup page.
        """
        self.goto("/signup")
        self.verify_sign_up_page_uri_is_open()

    def fill_form(self, email: str, username: str, password: str) -> None:
        """
        Fill the signup form fields.
        """
        self.username.fill(username)
        self.email.fill(email)
        self.password.fill(password)

    def submit_credentials_success(self, email: str, username: str, password: str) -> None:
        """
        Expected: Successful user creation.
        Submitting the input credentials and waiting for the /login page
        """
        self.fill_form(email, username, password)
        self.save.click()
        self.assert_login_page_is_displayed()

    def submit_credentials_error(self, email: str, username: str, password: str) -> None:
        """
        Expected: Failed user creation.
        Submitting the input credentials and waiting for the error message on the /signup page
        """
        self.fill_form(email, username, password)
        self.save.click()
        self.verify_sign_up_page_uri_is_open()
        self.assert_error_visible()

    def click_sign_in_link(self) -> None:
        """
        Clicking the Sign in link on the Sign up page
        """
        self.login.click()
        self.assert_login_page_is_displayed()

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed signup attempt.
        """
        expect(self.error).to_be_visible()

    def assert_sign_up_is_loaded(self) -> None:
        """
        Verifying that key controls are displayed on the Sign up page
        """
        expect(self.username).to_be_visible()
        expect(self.email).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.save).to_be_visible()
        expect(self.login).to_be_visible()
