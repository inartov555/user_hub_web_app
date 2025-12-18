"""
Page object for the Stats page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class StatsPage(BasePage):
    """
    Encapsulates the online-users stats page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.title = self.page.locator("h2")
        self.online_user_list = self.page.locator("ul li")

    def open(self) -> None:
        """
        Open the stats page.
        """
        self.goto("/stats")

    def assert_loaded(self) -> None:
        """
        Assert that the stats title and list are visible.
        """
        expect(self.title).to_be_visible()
        expect(self.online_user_list).to_be_visible()
