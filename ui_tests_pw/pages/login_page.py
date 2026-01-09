"""
Page object for the Login page.
"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page object for the Login page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.submit = self.page.locator("form button[type='submit']")

        self.signup = self.page.locator("a[href='/signup']")
        self.forgot_password = self.page.locator("a[href='/reset-password']")

    def open(self) -> None:
        """
        Navigate to the login page.
        """
        self.goto("/login")
        self.assert_login_page_is_displayed()

    def fill_credentials(self, username: str, password: str) -> None:
        """
        Fill in the username and password fields.

        Args:
            username: Username to type into the form.
            password: Password to type into the form.
        """
        self.username.fill(username)
        self.password.fill(password)

    def submit_credentials_success(self, username: str, password: str) -> None:
        """
        Expected: Successful login.
        Submit the input credentials and wait for the Users Table page
        """
        self.fill_credentials(username, password)
        self.submit.click()
        self.wait_for_the_users_table_page_to_load()

    def submit_credentials_error(self, username: str, password: str) -> None:
        """
        Expected: Failed login.
        Submit the input credentials and wait for the error message on the Login page
        """
        self.fill_credentials(username, password)
        self.submit.click()
        self.assert_login_page_is_displayed()
        self.assert_error_visible()

    def click_create_account_link(self) -> None:
        """
        Clicking the Create account link on the Login page
        """
        self.signup.click()
        self.verify_sign_up_page_uri_is_open()

    def click_forgot_password_link(self) -> None:
        """
        Clicking the Forgot password? link on the Login page
        """
        self.forgot_password.click()
        self.verify_reset_password_page_uri_is_open()
