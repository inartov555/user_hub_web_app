"""
Page object for the Profile view page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ProfileViewPage(BasePage):
    """
    Encapsulates the profile view UI.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.full_name = self.page.locator("#fullName")
        self.username = self.page.locator("#username")
        self.user_id = self.page.locator("#userid")
        self.email = self.page.locator("#email")
        self.bio = self.page.locator("#bio")
        self.edit_profile = self.page.locator("#editProfile")
        self.change_password = self.page.locator("#changePassword")

    def open(self) -> None:
        """
        Open the profile view page.
        """
        self.goto("/profile-view")
        self.page.wait_for_url(re.compile(r".*/profile-view$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-view$"))

    def assert_profile_basics_visible(self) -> None:
        """
        Assert that basic profile fields are visible.
        """
        expect(self.username).to_be_visible()
        expect(self.email).to_be_visible()
        expect(self.full_name).to_be_visible()

    def click_edit_button(self) -> None:
        """
        Click Edit button to enter the Profile Edit page
        """
        self.edit_profile.click()
        self.page.wait_for_url(re.compile(r".*/profile-edit$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-edit$"))

    def click_change_password_button(self) -> None:
        """
        Click Change Password button to enter the Change Password page
        """
        self.change_password.click()
        self.page.wait_for_url(re.compile(r".*/users/\d+/change-password$"))
        expect(self.page).to_have_url(re.compile(r".*/users/\d+/change-password$"))
