"""
Settings page
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Settings page
    """
    def __init__(self, page: Page, base_url: str):
        # super().__init__(page, base_url)
        pass

    def open(self) -> None:
        """
        Open Settings page
        """
        self.goto("/settings")

    def set_auth_numbers(self, renew_sec: int, idle_sec: int, access_life: int, rotate: bool = True) -> None:
        """
        Inputs are labeled by translation values (keys match visible text)
        """
        self.page.get_by_label("JWT_RENEW_AT_SECONDS").fill(str(renew_sec))
        self.page.get_by_label("IDLE_TIMEOUT_SECONDS").fill(str(idle_sec))
        self.page.get_by_label("ACCESS_TOKEN_LIFETIME").fill(str(access_life))
        chk = self.page.get_by_role("checkbox")
        if rotate:
            if not chk.is_checked():
                chk.check()
        else:
            if chk.is_checked():
                chk.uncheck()

    def save(self) -> None:
        """
        Saving the changes
        """
        self.page.get_by_role("button", name="Save").click()
        expect(self.page.get_by_text("App settings have been saved.")).to_be_visible()
