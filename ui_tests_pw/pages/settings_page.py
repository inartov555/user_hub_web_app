"""
Page object for the admin Settings page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Encapsulates the application settings form (admin-only).
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.idle_timeout_sec = self.page.locator("#idleTimeoutSeconds")
        self.access_token_lifetime = self.page.locator("#accessTokenLifetime")
        self.renew_at_sec = self.page.locator("#renewAtSeconds")
        self.save = self.page.locator("form button[type='submit']")

    def open(self) -> None:
        """
        Open the settings page.
        """
        self.goto("/settings")

    def assert_loaded(self) -> None:
        """
        Assert that core settings fields are visible.
        """
        expect(self.idle_timeout_sec).to_be_visible()
        expect(self.page.locator("#accessTokenLifetime")).to_be_visible()
        expect(self.page.locator("#renewAtSeconds")).to_be_visible()

    def change_idle_timeout(self, value: int) -> None:
        """
        Set a new idle timeout value.
        """
        self.idle_timeout_sec.fill(str(value))
