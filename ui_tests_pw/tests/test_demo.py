"""
Tests for the Login page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, Browser, expect

from conftest import take_a_screenshot
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from utils.theme import Theme
from utils.auth import login_via_ui
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)


@pytest.mark.theme
@pytest.mark.localization
# @pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
# @pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.parametrize("ui_theme_param", ["light"])
# @pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_base_demo(request,
                   page: Page,
                   ui_theme_param: Theme) -> None:
    """
    Base DEMO test to run multiple pages and take screenshots
    """
    login_page = LoginPage(page)
    login_page.open()
    login_page.ensure_theme(ui_theme_param)
    # Screenshot -> Cookie consent pop-up
    take_a_screenshot(page)
    # Accepting the cookie consent pop-up
    login_page.accept_cookie_consent_if_present()
    # Screenshot -> Login page
    take_a_screenshot(page)
    login_via_ui(page, "invalid", "short")
    # Screenshot -> Login page -> Error
    take_a_screenshot(page)
    login_page.click_create_account_link()
    # Screenshot -> Signup page
    take_a_screenshot(page)
    signup_page = SignupPage(page)
    signup_page.fill_form("invalid", "invalid", "invalid")
