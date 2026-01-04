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
        self.save = self.page.locator("#save")
        self.cancel = self.page.locator("#cancel")
        self.error = self.page.locator("div[data-tag='errorAlert']")

    def open(self) -> None:
        """
        Open the profile edit page.
        """
        self.goto("/profile-edit")
        self.page.wait_for_url(re.compile(r".*/profile-edit$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-edit$"))

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

    def remove_maxlength_attribute_from_input_fields(self) -> None:
        """
        Remove maxlength attribute from the input fields for further error validation
        """
        self.first_name.evaluate("node => node.removeAttribute('maxlength')")
        self.last_name.evaluate("node => node.removeAttribute('maxlength')")
        self.bio.evaluate("node => node.removeAttribute('maxlength')")

    def assert_error_alert_shown(self) -> None:
        """
        Verify that error alert is shown when e.g. field length exceeded
        """
        expect(self.error).to_be_visible()
