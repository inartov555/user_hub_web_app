"""
Page object for the Stats page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class StatsPage(BasePage):
    """
    Page object for the Stats page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

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
        # Depending on tests run before, there may be 1 or even more online users
        assert self.online_user_list.count() >= 1

    def assert_user_was_online_during_last_5_mins(self, username: str) -> None:
        """
        Assert that the passed username is displayed on the User Stats page
        """
        expect(self.page.locator(f"div[data-tag='username-{username}']")).to_be_visible()

    def assert_user_is_not_listed_on_the_page(self, username: str) -> None:
        """
        Assert that the passed username is not listed on the User Stats page
        """
        expect(self.page.locator(f"div[data-tag='username-{username}']")).not_to_be_visible()
