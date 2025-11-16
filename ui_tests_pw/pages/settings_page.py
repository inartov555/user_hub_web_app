"""Page object for the admin Settings page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class SettingsPage(BasePage):
    """Encapsulates the application settings form (admin-only)."""

    def open(self) -> None:
        """Open the settings page."""
        self.goto("/settings")

    def assert_loaded(self) -> None:
        """Assert that core settings fields are visible."""
        expect(self.page.locator("#idleTimeoutSeconds")).to_be_visible()
        expect(self.page.locator("#accessTokenLifetime")).to_be_visible()
        expect(self.page.locator("#renewAtSeconds")).to_be_visible()

    def change_idle_timeout(self, value: int) -> None:
        """Set a new idle timeout value."""
        self.page.fill("#idleTimeoutSeconds", str(value))

    def save(self) -> None:
        """Submit the settings form."""
        self.page.locator("form button[type='submit']").click()
