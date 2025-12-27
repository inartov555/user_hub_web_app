"""
Page object for the Profile edit page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ProfileEditPage(BasePage):
    """
    Encapsulates the profile edit form.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.first_name = self.page.locator("#firstName")
        self.last_name = self.page.locator("#lastName")
        self.bio = self.page.locator("#bio")
        self.save = self.page.locator("#save")
        self.cancel = self.page.locator("#cancel")

    def open(self) -> None:
        """
        Open the profile edit page.
        """
        self.goto("/profile-edit")

    def fill_basic_fields(self, first_name: str, last_name: str, bio: str) -> None:
        """
        Fill first name, last name, and bio fields.
        """
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.bio.fill(bio)

    def assert_loaded(self) -> None:
        """
        Assert that the profile edit form is loaded.
        """
        expect(self.first_name).to_be_visible()
        expect(self.last_name).to_be_visible()
        expect(self.bio).to_be_visible()
