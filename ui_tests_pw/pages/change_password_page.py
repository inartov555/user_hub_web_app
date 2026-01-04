"""
Page object for the Change Password page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ChangePasswordPage(BasePage):
    """
    Encapsulates the change-password form for a user.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.password = self.page.locator("#password")
        self.confirm_password = self.page.locator("#confirmPassword")
        self.submit = self.page.locator("form button[type='submit']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")

    def open_for_user(self, user_id: int) -> None:
        """
        Open the change-password page for a given user id.
        """
        self.goto(f"/users/{user_id}/change-password")
        self.wait_for_change_password_page_to_load()

    def wait_for_change_password_page_to_load(self) -> None:
        """
        Wait for the Change Password page to load
        """
        expect(page).to_have_url(re.compile(r".*/users/\d+/change-password$"))
        page.wait_for_url(re.compile(r".*/users/\d+/change-password$"))

    def fill_passwords(self, password: str, confirm: str) -> None:
        """
        Fill the new password and confirmation fields.
        """
        self.password.fill(password)
        self.confirm_password.fill(confirm)

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed Change Password page.
        """
        expect(self.error).to_be_visible()

    def assert_change_password_is_loaded(self) -> None:
        """
        Assert that Change Password page's key controls are loaded
        """
        expect(self.password.to_be_visible()
        expect(self.confirm_password.to_be_visible()
        expect(self.submit.to_be_visible()
