"""
Base page object with shared helpers.
"""

from __future__ import annotations

from playwright.sync_api import Page
from django.utils import translation

from config import frontend_url
from utils.theme import Theme, set_theme
from utils.localization import set_locale, assert_locale_visible


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
        assert_locale_visible(self.page, expected_code)

    def assert_text_localization(self,
                                 ui_locale_param: str,
                                 actual: str,
                                 expected: str,
                                 mode: str = "strict") -> None:
        """
        Check text localization

        Args:
            ui_locale_param (str): e.g. en-US
            actual (str): actual text localization retrieved from UI element
            expected (str): expected text localization, provide the text code to retrieve the localization with Django
            mode (str): one of (contans, strict)
        """
        with translation.override(ui_locale_param.lower()):
            expected = translation.gettext(expected)
        err_msg = f"Wrong text localization; actual '{actual}'; expected '{expected}'; mode '{mode}'"
        if mode.lower().strip() == "contains":
            assert expected in actual, err_msg
        else:
            # strict
            assert expected == actual, err_msg
