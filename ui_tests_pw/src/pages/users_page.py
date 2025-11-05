"""
Users table page
"""

from __future__ import annotations

# from playwright.sync_api import expect
from playwright.sync_api import Page

from .base_page import BasePage


class UsersPage(BasePage):
    """
    Users table page
    """
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.title = page.get_by_role("heading", name="Users")
        self.table = page.locator("table")
        self.delete_selected = page.locator("#deleteSelected, button:has-text('Delete selected')")

    def open(self) -> None:
        """
        Opening Users table page
        """
        self.goto("/users")

    def open_profile(self) -> None:
        """
        Select the Profile tab
        """
        self.page.get_by_role("link", name="Profile").click()
