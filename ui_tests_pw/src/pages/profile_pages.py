"""
Profile pages
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class ProfileViewPage(BasePage):
    """
    Profile View page
    """
    def __init__(self, page: Page, base_url: str):  # pylint: disable=useless-parent-delegation
        super().__init__(page, base_url)

    def open(self) -> None:
        """
        Open Profile View page
        """
        self.goto("/profile-view")


class ProfileEditPage(BasePage):
    """
    Profile Edit page
    """
    def __init__(self, page: Page, base_url: str):  # pylint: disable=useless-parent-delegation
        super().__init__(page, base_url)

    def open(self) -> None:
        """
        Open Profile Edit page
        """
        self.goto("/profile-edit")

    def set_first_last(self, first: str, last: str) -> None:
        """
        Set first and last names
        """
        self.page.get_by_label("First name").fill(first)
        self.page.get_by_label("Last name").fill(last)

    def save(self) -> None:
        """
        Save the profile changes
        """
        self.page.get_by_role("button", name="Save").click()
        expect(self.page.get_by_text("Saved")).to_be_visible()
