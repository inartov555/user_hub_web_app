"""
Page object for the Profile edit page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class ProfileEditPage(BasePage):
    """
    Encapsulates the profile edit form.
    """

    def open(self) -> None:
        """
        Open the profile edit page.
        """
        self.goto("/profile-edit")

    def fill_basic_fields(self, first_name: str, last_name: str, bio: str) -> None:
        """
        Fill first name, last name and bio fields.
        """
        self.page.fill("#firstName", first_name)
        self.page.fill("#lastName", last_name)
        self.page.fill("#bio", bio)

    def save(self) -> None:
        """
        Click the Save button.
        """
        self.page.locator("#save").click()

    def cancel(self) -> None:
        """
        Click the Cancel button.
        """
        self.page.locator("#cancel").click()

    def assert_loaded(self) -> None:
        """
        Assert that the profile edit form is loaded.
        """
        expect(self.page.locator("#firstName")).to_be_visible()
