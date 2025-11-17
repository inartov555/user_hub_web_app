"""
Utility helpers for dealing with light / dark theme from tests.
"""

from __future__ import annotations
from typing import Literal

from playwright.sync_api import Page


Theme = Literal["light", "dark"]


def get_current_theme(page: Page) -> Theme:
    """
    Return the current theme according to the HTML root `dark` class.

    Args:
        page: Playwright page instance.

    Returns:
        "dark" if the `<html>` element has the `dark` class, otherwise "light".
    """
    has_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    return "dark" if has_dark else "light"


def set_theme(page: Page, desired: Theme) -> None:
    """
    Ensure that the UI uses the desired theme.

    If the current theme does not match `desired`, the dark-mode toggle button
    (with id ``lightDarkMode``) is clicked once.
    """
    current = get_current_theme(page)
    if current == desired:
        return
    page.locator("#lightDarkMode").click()
