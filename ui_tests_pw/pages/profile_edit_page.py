"""
Page object for the Profile edit page.
"""

from __future__ import annotations
import re

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
        self.profile_avatar_file = self.page.locator("#profileAvatarImage")
        self.profile_avatar_image = self.page.locator("#profileAvatar")
        self.save = self.page.locator("#save")
        self.cancel = self.page.locator("#cancel")

    def open(self) -> None:
        """
        Open the profile edit page.
        """
        self.goto("/profile-edit")
        self.verify_profile_edit_page_uri_is_open()

    def fill_basic_fields(self, first_name: str, last_name: str, bio: str, avatar: str = None) -> None:
        """
        Fill first name, last name, and bio fields.
        """
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.bio.fill(bio)
        if avatar:
            self.profile_avatar_file.set_input_files(avatar)

    def click_save_and_wait_profile_view(self) -> None:
        """
        Click the Save button and wait for the Profile View page to load
        """
        self.save.click()
        self.verify_profile_view_page_uri_is_open()

    def click_cancel_and_wait_profile_view(self) -> None:
        """
        Click the Cancel button and wait for the Profile View page to load
        """
        self.cancel.click()
        self.verify_profile_view_page_uri_is_open()

    def assert_loaded(self) -> None:
        """
        Assert that the profile edit form is loaded.
        """
        expect(self.first_name).to_be_visible()
        expect(self.last_name).to_be_visible()
        expect(self.bio).to_be_visible()
        expect(self.profile_avatar_file).to_be_visible()

    def remove_maxlength_attribute_from_input_fields(self) -> None:
        """
        Remove the maxlength attribute from the input fields for further error validation
        """
        self.first_name.evaluate("node => node.removeAttribute('maxlength')")
        self.last_name.evaluate("node => node.removeAttribute('maxlength')")
        self.bio.evaluate("node => node.removeAttribute('maxlength')")

    def assert_avatar_in_profile_edit(self, src_attr: str) -> None:
        """
        Assert that the passed avatar is in the Profile Edit page.
        Note: avatar being set while editing will be applied
        after saving and entering the Profile Edit page again.

        Examples for src_attr:
            - default avatar = r".*placehold.co/\d+x\d+\?text=.*"
            - some uploaded picture = rf".*/media/avatars/user_\d+/.*{Path(avatar_path).suffix}"
        """
        expect(self.profile_avatar_image).to_have_attribute("src", re.compile(src_attr))

    def assert_avatar_not_in_profile_edit(self, src_attr: str) -> None:
        """
        Assert that the passed avatar is not in the Profile Edit page.

        Examples for src_attr:
            - default avatar = r".*placehold.co/\d+x\d+\?text=.*"
            - some uploaded picture = rf".*/media/avatars/user_\d+/.*{Path(avatar_path).suffix}"
        """
        expect(self.profile_avatar_image).not_to_have_attribute("src", re.compile(src_attr))
