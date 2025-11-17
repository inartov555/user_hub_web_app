"""
conftest.py
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config import (
    frontend_url,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from utils.auth import ensure_regular_user
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Return the base URL of the frontend as configured by environment variables.
    """
    return frontend_url("/").rstrip("/")


@pytest.fixture(name="ui_theme", params=["light", "dark"], scope="function")
def ui_theme_fixture(request: pytest.FixtureRequest) -> Theme:
    """
    Parametrized fixture for light / dark themes.
    """
    return request.param  # type: ignore[return-value]


@pytest.fixture(name="ui_locale", params=["en-US", "uk-UA"], scope="function")
def ui_locale_fixture(request: pytest.FixtureRequest) -> str:
    """
    Parametrized fixture for a subset of locales to keep test time reasonable.
    """
    return request.param  # type: ignore[return-value]


@pytest.fixture(scope="function")
def logged_in_admin(page: Page, ui_theme: Theme, ui_locale: str) -> Page:
    """
    Return a Playwright page already logged in as the admin user.
    """

    login_page = LoginPage(page)
    login_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    login_page.fill_credentials(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    login_page.submit()
    page.wait_for_url("**/users")
    return page


@pytest.fixture(scope="function")
def logged_in_regular(page: Page, ui_theme: Theme, ui_locale: str) -> Page:
    """
    Return a Playwright page already logged in as the regular test user.
    """
    ensure_regular_user()
    login_page = LoginPage(page)
    login_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    login_page.fill_credentials(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    login_page.submit()
    page.wait_for_url("**/users")
    return page
