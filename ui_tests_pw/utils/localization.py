"""
Utility helpers for handling localization in UI tests.
"""

from __future__ import annotations
from typing import Iterable, List

from playwright.sync_api import Page


def set_locale(page: Page, locale_code: str) -> None:
    """
    Set the current UI locale via the navbar dropdown.

    Args:
        page (Page): Playwright page instance.
        locale_code (str): Locale code such as en-US or uk-UA.
    """
    page.locator("#locale").select_option(locale_code)


def get_visible_locales(page: Page) -> List[str]:
    """
    Returns:
        list, the list of locale codes that are visible in the navbar dropdown.
    """
    options = page.locator("#locale option")
    values: List[str] = []
    for i in range(options.count()):
        values.append(options.nth(i).get_attribute("value") or "")
    return values


def assert_locale_visible(page: Page, expected: Iterable[str]) -> None:
    """
    Assert that the provided locale codes exist in the dropdown options.

    Args:
        page (Page): Playwright page instance.
        expected (Iterable[str]): Iterable of expected locale codes.
    """
    visible_draft = get_visible_locales(page)
    visible: Set[str] = {_ui_locale.lower() for _ui_locale in visible_draft}
    expected_set: Set[str] = {_ui_locale.lower() for _ui_locale in expected}
    missing = expected_set - visible
    assert not missing, f"Missing locales in UI: {sorted(missing)}; visible={sorted(visible)}"
