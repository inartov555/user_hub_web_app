"""
Page object for the Change Password page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ChangePasswordPage(BasePage):
    """
    Page object for the Change Password page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.password = self.page.locator("#password")
        self.confirm_password = self.page.locator("#confirmPassword")
        self.submit = self.page.locator("form button[type='submit']")

    def open_for_user(self, user_id: int) -> None:
        """
        Open the change-password page for a given user ID.
        """
        self.goto(f"/users/{user_id}/change-password")
        self.wait_for_change_password_page_to_load()

    def wait_for_change_password_page_to_load(self) -> None:
        """
        Wait for the Change Password page to load
        """
        self.verify_change_password_page_uri_is_open()

    def fill_passwords(self, password: str, confirm: str) -> None:
        """
        Fill in the new password and confirmation fields.
        """
        self.password.fill(password)
        self.confirm_password.fill(confirm)

    def assert_change_password_is_loaded(self) -> None:
        """
        Assert that the Change Password page's key controls are loaded
        """
        expect(self.password).to_be_visible()
        expect(self.confirm_password).to_be_visible()
        expect(self.submit).to_be_visible()
