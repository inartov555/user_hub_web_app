"""
Common methods related to page objects
"""

from __future__ import annotations
from typing import Optional

from playwright.sync_api import Page, expect


class BasePage:
    """
    Base page
    """
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')

    def goto(self, path: str = "/") -> None:
        """
        Open URL
        """
        self.page.goto(self.base_url + path)

    # Navbar helpers common to many pages
    def open_additional_if_needed(self) -> None:
        """
        Open the "Additional" row if present and hidden
        """
        additional = self.page.locator("#additional")
        if additional.is_visible():
            additional.click()

    def set_locale(self, locale_code: str) -> None:
        """
        i18next reads from localStorage key 'i18nextLng'
        """
        self.page.evaluate("""(code) => { localStorage.setItem('i18nextLng', code); }""", locale_code)
        self.page.reload()

    def toggle_dark_mode(self) -> None:
        """
        Toggling light/dark button to change the theme
        """
        self.page.locator("#lightDarkMode").click()

    def expect_dark_mode(self, is_dark: bool) -> None:
        """
        Check if dark mode is on
        """
        html = self.page.locator("html")
        if is_dark:
            expect(html).to_have_class(lambda c: "dark" in c, timeout=3000)
        else:
            expect(html).not_to_have_class(lambda c: "dark" in c, timeout=3000)

    # Auth storage helpers
    def get_access_token(self) -> Optional[str]:
        """
        Get actual access token (fron web browser localStorage)
        """
        return self.page.evaluate("""() => localStorage.getItem('access')""")

    def get_refresh_token(self) -> Optional[str]:
        """
        Get actual refresh token (fron web browser localStorage)
        """
        return self.page.evaluate("""() => localStorage.getItem('refresh')""")
