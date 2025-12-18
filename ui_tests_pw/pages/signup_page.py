"""
Page object for the Signup page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class SignupPage(BasePage):
    """
    Encapsulates the registration / signup page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.email = self.page.locator("#email")
        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.save = self.page.locator("#create")

    def open(self) -> None:
        """
        Open the signup page.
        """
        self.goto("/signup")

    def fill_form(self, username: str, email: str, password: str) -> None:
        """
        Fill the signup form fields.
        """
        self.username.fill(username)
        self.email.fill(email)
        self.password.fill(password)

    def submit(self) -> None:
        """
        Submit the signup form.
        """
        self.save.click()

    def assert_error_or_success(self) -> None:
        """
        Assert that either a success alert or an error is visible.
        """
        expect(self.page.locator("div[role='alert']")).to_be_visible()
