"""
Page object for the Profile view page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ProfileViewPage(BasePage):
    """
    Page object for the Profile view page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.full_name = self.page.locator("#fullName")
        self.username = self.page.locator("#username")
        self.user_id = self.page.locator("#userid")
        self.email = self.page.locator("#email")
        self.bio = self.page.locator("#bio")
        self.profile_avatar_image = self.page.locator("#profileAvatar")
        self.edit_profile = self.page.locator("#editProfile")
        self.change_password = self.page.locator("#changePassword")

    def open(self) -> None:
        """
        Open the Profile View page.
        """
        self.goto("/profile-view")
        self.verify_profile_view_page_uri_is_open()

    def assert_profile_basics_visible(self) -> None:
        """
        Assert that basic profile fields are visible.
        """
        expect(self.username).to_be_visible()
        expect(self.email).to_be_visible()
        expect(self.full_name).to_be_visible()
        expect(self.profile_avatar_image).to_be_visible()

    def click_edit_button(self) -> None:
        """
        Click the Edit button to enter the Profile Edit page
        """
        self.edit_profile.click()
        self.verify_profile_edit_page_uri_is_open()

    def click_change_password_button(self) -> None:
        """
        Click the Change Password button to enter the Change Password page
        """
        self.change_password.click()
        self.verify_change_password_page_uri_is_open()

    def assert_avatar_in_profile_view(self, src_attr: str) -> None:
        """
        Assert that the passed avatar is in the Profile View page.
        """
        expect(self.profile_avatar_image).to_have_attribute("src", re.compile(src_attr))

    def assert_avatar_not_in_profile_view(self, src_attr: str) -> None:
        """
        Assert that the passed avatar is not in the Profile View page.
        """
        expect(self.profile_avatar_image).not_to_have_attribute("src", re.compile(src_attr))
