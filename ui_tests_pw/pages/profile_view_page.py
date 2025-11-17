"""
Page object for the Profile view page.
"""

from __future__ import annotations

from playwright.sync_api import expect

from .base_page import BasePage


class ProfileViewPage(BasePage):
    """
    Encapsulates the profile view UI.
    """

    def open(self) -> None:
        """
        Open the profile view page.
        """
        self.goto("/profile-view")

    def assert_profile_basics_visible(self) -> None:
        """
        Assert that basic profile fields are visible.
        """
        expect(self.page.locator("#username")).to_be_visible()
        expect(self.page.locator("#email")).to_be_visible()
        expect(self.page.locator("#fullName")).to_be_visible()

    def click_edit_profile(self) -> None:
        """
        Click the 'Edit profile' button.
        """
        self.page.locator("#editProfile").click()
