"""
Utility helpers for dealing with light / dark theme from tests.
"""

from __future__ import annotations
from typing import Literal
import re

from playwright.sync_api import Page, expect


Theme = Literal["light", "dark"]


def get_current_theme(page: Page) -> Theme:
    """
    Return the current theme according to the HTML root dark class.

    Args:
        page: Playwright page instance.

    Returns:
        Theme, one of (light, dark)
    """
    theme_toggler = page.locator("#lightDarkMode")
    value = theme_toggler.get_attribute("data-tag")
    return value.lower()


def set_theme(page: Page, desired: Theme) -> None:
    """
    Ensure that the UI uses the desired theme.

    If the current theme does not match desired, the dark-mode toggle button is clicked once.
    """
    theme_toggler = page.locator("#lightDarkMode")
    desir = desired.lower()
    current = get_current_theme(page)
    if current == desir:
        return
    theme_toggler.click()
    expect(theme_toggler).to_have_attribute(
        "data-tag",
        re.compile(r"^(?!{}$).+".format(re.escape(current))),  # pylint: disable=consider-using-f-string
        timeout=10000,
    )
