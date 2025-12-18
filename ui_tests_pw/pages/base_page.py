"""
Base page object with shared helpers.
"""

from __future__ import annotations

from playwright.sync_api import Page

from config import frontend_url
from utils.theme import Theme, set_theme
from utils.localization import set_locale, get_visible_locales


class BasePage:
    """
    Base class for all page objects.

    Each specific page object wraps a Playwright Page instance and provides
    typed helpers for navigation and common UI actions (theme, localization).
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the base page.

        Args:
            page (Page): Playwright :class: Page instance.
        """
        self.page: Page = page

    def goto(self, path: str) -> None:
        """
        Open a relative path on the frontend.

        Args:
            path (str): Relative path such as /login or /users.
        """
        self.page.goto(frontend_url(path), wait_until="load")

    def ensure_theme(self, theme: Theme) -> None:
        """
        Ensure the UI uses the given theme.
        """
        set_theme(self.page, theme)

    def ensure_locale(self, locale_code: str) -> None:
        """
        Ensure the UI uses the given locale code.
        """
        set_locale(self.page, locale_code)

    def assert_locale_available(self, expected_code: str) -> None:
        """
        Assert that the given locale code is visible in the navbar dropdown.
        """
        visible = get_visible_locales(self.page)
        assert expected_code in visible, f"Locale {expected_code!r} not in {visible}"
