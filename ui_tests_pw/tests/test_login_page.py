"""
Tests for the Login page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme", ["light", "dark"])
@pytest.mark.parametrize("ui_locale", ["en-US", "uk-UA"])
def test_login_page_renders_in_theme_and_locale(login_page: LoginPage,  # pylint: disable=unused-argument
                                                page: Page,
                                                ui_theme: Theme,
                                                ui_locale: str) -> None:
    """
    Verify that the login page renders correctly for each theme and locale combination.
    """
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    login_page.assert_on_login_page()


@pytest.mark.parametrize(
    "username,password",
    [
        ("invalid", "invalid"),
        (DEFAULT_ADMIN_USERNAME, "wrongpw"),
    ],
)
def test_login_invalid_credentials_show_error(login_page: LoginPage,
                                              page: Page,  # pylint: disable=unused-argument
                                              username: str,
                                              password: str) -> None:
    """
    Invalid credentials should keep the user on the login page and show an error.
    """
    login_page.fill_credentials(username, password)
    login_page.submit.click()
    login_page.assert_on_login_page()
    login_page.assert_error_visible()


@pytest.mark.regular_user
def test_regular_user_can_login_and_redirects_to_users(page: Page) -> None:
    """
    Regular test user should be able to log in and land on /users.
    """
    login = LoginPage(page)
    login.open()
    login.fill_credentials(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    login.submit()
    page.wait_for_url("**/users")
    expect(page).to_have_url("**/users")


@pytest.mark.admin
def test_admin_can_login_and_see_users_nav(page: Page) -> None:
    """
    Admin user should log in successfully and see the Users nav item.
    """
    login = LoginPage(page)
    login.open()
    login.fill_credentials(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    login.submit()
    page.wait_for_url("**/users")
    expect(page.locator("#users")).to_be_visible()


@pytest.mark.localization
def test_login_links_to_signup_and_reset_password(page: Page) -> None:
    """
    Login page should expose links to signup and reset-password pages.
    """
    login = LoginPage(page)
    login.open()
    page.get_by_role("link", name="Create account").click()
    expect(page).to_have_url("**/signup")
    page.go_back()
    page.get_by_role("link", name="Forgot password?").click()
    expect(page).to_have_url("**/reset-password")
