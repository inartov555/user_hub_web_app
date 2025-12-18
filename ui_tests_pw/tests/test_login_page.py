"""
Tests for the Login page.
"""

from __future__ import annotations
import re

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
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_login_page_renders_in_theme_and_locale(login_page: LoginPage,  # pylint: disable=unused-argument
                                                page: Page,
                                                ui_theme_param: Theme,
                                                ui_locale_param: str) -> None:
    """
    Verify that the login page renders correctly for each theme and locale combination.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
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
def test_regular_user_can_login_and_redirects_to_users(login_page: LoginPage,
                                                       page: Page) -> None:
    """
    Regular test user should be able to log in and land on /users.
    """
    login_page.fill_credentials(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    login_page.submit.click()
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    expect(login_page.users_tab).to_be_visible()


@pytest.mark.admin
def test_admin_can_login_and_see_users_nav(login_page: LoginPage,
                                           page: Page) -> None:
    """
    Admin user should log in successfully and see the Users nav item.
    """
    login_page.fill_credentials(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    login_page.submit.click()
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    expect(login_page.users_tab).to_be_visible()


@pytest.mark.localization
def test_login_links_to_signup_and_reset_password(login_page: LoginPage,
                                                  page: Page) -> None:
    """
    Login page should expose links to signup and reset-password pages.
    """
    # Case: /signup page is opened after clicking Sign Up
    login_page.signup.click()
    page.wait_for_url(re.compile(r".*/signup$"))
    expect(page).to_have_url(re.compile(r".*/signup$"))
    # Case: /reset-password page is opened after clicking Forgot Password
    page.go_back()
    login_page.forgot_password.click()
    page.wait_for_url(re.compile(r".*/reset-password$"))
    expect(page).to_have_url(re.compile(r".*/reset-password$"))
