"""
Page object for the Signup page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class SignupPage(BasePage):
    """
    Encapsulates the registration / signup page.
    """

    def open(self) -> None:
        """
        Open the signup page.
        """
        self.goto("/signup")

    def fill_form(self, username: str, email: str, password: str) -> None:
        """
        Fill the signup form fields.
        """
        self.page.fill("#username", username)
        self.page.fill("#email", email)
        self.page.fill("#password", password)

    def submit(self) -> None:
        """
        Submit the signup form.
        """
        self.page.locator("#create").click()

    def assert_error_or_success(self) -> None:
        """
        Assert that either a success alert or an error is visible.
        """
        # Implementation is intentionally loose; exact markup may change.
        expect(self.page.locator("div[role='alert']")).to_be_visible()
