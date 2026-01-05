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

        self.page_title = self.page.locator("h2")
        self.online_user_list = self.page.locator("ul li")

    def open(self) -> None:
        """
        Open the stats page.
        """
        self.goto("/stats")
        self.verify_user_stats_page_uri_is_open()

    def assert_loaded(self) -> None:
        """
        Assert that the stats title and list are visible.
        """
        expect(self.page_title).to_be_visible()
        expect(self.online_user_list.first).to_be_visible()
        # Depending on tests run before, there may be 1 or 2, or even more users online
        assert self.online_user_list.count() >= 1
