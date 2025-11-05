"""
Login page
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class LoginPage(BasePage):
    """
    Login page
    """
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.username = page.get_by_label("Username")
        self.password = page.get_by_label("Password")
        self.submit = page.get_by_role("button", name="Sign in")

    def open(self):
        """
        Open Login page
        """
        self.goto("/login")

    def login(self, username: str, password: str):
        """
        Fill in the user credentials and submit the login form
        """
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    def expect_error(self):
        """
        Check if login error is shown
        """
        expect(self.page.get_by_role("alert")).to_be_visible()
