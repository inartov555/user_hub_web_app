"""
Tests for the Login page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from pages.login_page import LoginPage
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from utils.theme import Theme


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_login_page_renders_in_theme_and_locale(login_page: LoginPage,
                                                ui_theme_param: Theme,
                                                ui_locale_param: str) -> None:
    """
    Verify that the login page renders correctly for each theme and locale combination.
    """
    login_page.ensure_theme(ui_theme_param)
    login_page.ensure_locale(ui_locale_param)
    login_page.assert_login_page_is_displayed()
    # Verifying localization
    actual = login_page.page_title.text_content()
    expected = "Log in"
    login_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.parametrize("username, password",
                         [("invalid", "invalid"), (DEFAULT_ADMIN_USERNAME, "wrongpw")])
def test_login_invalid_credentials_show_error(login_page: LoginPage,
                                              username: str,
                                              password: str) -> None:
    """
    Invalid credentials should keep the user on the login page and show an error.
    """
    login_page.submit_credentials_error(username, password)


@pytest.mark.regular_user
def test_regular_user_can_login_and_redirects_to_users(login_page: LoginPage) -> None:
    """
    A regular test user should be able to log in and land on /users.
    """
    login_page.submit_credentials_success(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)


@pytest.mark.admin
def test_admin_can_login_and_see_users_nav(login_page: LoginPage) -> None:
    """
    Admin user should log in successfully and see the Users nav item.
    """
    login_page.submit_credentials_success(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)


@pytest.mark.regular_user
def test_login_links_to_signup_and_reset_password(login_page: LoginPage,
                                                  page: Page) -> None:
    """
    The Login page should expose links to the Signup and Reset Password pages.
    """
    # Case: /signup page is opened after clicking Sign Up
    login_page.click_create_account_link()
    page.go_back()  # getting back to the Log in page to check Forgot Password
    # Case: /reset-password page is opened after clicking Forgot Password
    login_page.click_forgot_password_link()
