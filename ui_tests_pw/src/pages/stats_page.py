"""
Stats page
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class StatsPage(BasePage):
    """
    Stats page
    """
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self) -> None:
        """
        Opening User stats page
        """
        self.goto("/stats")

    def expect_cards(self) -> None:
        """
        Checking if there are online users (at least one being currently watching the page)
        """
        expect(self.page.get_by_text("Online users")).to_be_visible()
