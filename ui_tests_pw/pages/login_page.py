"""
Page object for the Login page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class LoginPage(BasePage):
    """
    Encapsulates interactions with the login page.
    """

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
        self.page.fill("#username", username)
        self.page.fill("#password", password)

    def submit(self) -> None:
        """
        Submit the login form.
        """
        self.page.locator("form button[type='submit']").click()

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed login attempt.
        """
        expect(self.page.locator("p.text-red-600")).to_be_visible()

    def assert_on_login_page(self) -> None:
        """
        Assert that the current page is still the login page.
        """
        expect(self.page.locator("#username")).to_be_visible()
        expect(self.page).to_have_url("**/login")
