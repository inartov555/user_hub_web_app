"""Page object for the Stats page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class StatsPage(BasePage):
    """Encapsulates the online-users stats page."""

    def open(self) -> None:
        """Open the stats page."""
        self.goto("/stats")

    def assert_loaded(self) -> None:
        """Assert that the stats title and list are visible."""
        expect(self.page.locator("h2")).to_be_visible()
        expect(self.page.locator("ul")).to_be_visible()
