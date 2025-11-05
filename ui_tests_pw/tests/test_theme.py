"""
Tests related to the theme
"""

import pytest
from playwright.sync_api import expect

from ui_tests.src.pages.base_page import BasePage


@pytest.mark.theme
def test_light_dark_mode_toggle(logged_in_user_page, base_url):
    """
    Docstring placeholder
    """
    base = BasePage(logged_in_user_page, base_url)
    # Explicitly set to light first
    logged_in_user_page.evaluate("() => { localStorage.setItem('theme','light'); "
                                 "document.documentElement.classList.remove('dark'); }")
    logged_in_user_page.reload()
    base.expect_dark_mode(False)
    base.toggle_dark_mode()
    base.expect_dark_mode(True)
    base.toggle_dark_mode()
    base.expect_dark_mode(False)
