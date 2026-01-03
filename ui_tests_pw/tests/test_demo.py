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
from pages.reset_password_page import ResetPasswordPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme
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
def test_base_demo(page: Page,
                   ui_theme_param: Theme) -> None:
    """
    Base DEMO test to run multiple pages and take screenshots
    """
    login_page = LoginPage(page)
    login_page.open()
    # To see the Cookie Consent overlay in different themens, the block needs to be removed from DOM
    # and then the theme changed, and page reloaded after that
    login_page.remove_cookie_consent_popup_from_dom()
    login_page.ensure_theme(ui_theme_param)
    login_page.reload()
    # Screenshot -> Cookie consent pop-up
    take_a_screenshot(page)
    # Accepting the cookie consent pop-up
    login_page.accept_cookie_consent_if_present()
    # Screenshot -> Login page
    take_a_screenshot(page)
    login_page.submit_credentials_error("invalid", "short")
    # Screenshot -> Login page -> Error
    take_a_screenshot(page)

    login_page.click_create_account_link()
    # Screenshot -> Signup page
    take_a_screenshot(page)
    signup_page = SignupPage(page)
    signup_page.submit_credentials_error("invalid", "invalid", "invalid")
    # Screenshot -> Signup page -> Error
    take_a_screenshot(page)
    # Getting back to the /login page
    signup_page.click_sign_in_link()

    # Now, let's open Forgot Password page
    login_page.click_forgot_password_link()
    # Screenshot -> Forgot Password page -> Email input
    take_a_screenshot(page)
    reset_password_page = ResetPasswordPage(page)
    reset_password_page.request_reset("invalid")
    reset_password_page.assert_error_visible()
    # Screenshot -> Reset Password page -> Error
    take_a_screenshot(page)
    # Clearing email field before entering a correct one
    reset_password_page.email.press("Control+A")
    reset_password_page.email.press("Backspace")
    reset_password_page.request_reset("test1@test.com")
    reset_password_page.assert_info_message()
    # Screenshot -> Forgot Password page -> Info page
    take_a_screenshot(page)
    # Let's get back to the Login page
    reset_password_page.click_sign_in_link()

    # Now, let's check the /users page
    login_page.submit_credentials_success("admin", "changeme123")
    


@pytest.mark.parametrize(
    "username,password",
    [
        ("invalid", "invalid"),
        (DEFAULT_ADMIN_USERNAME, "wrongpw"),
    ],
)
def test_login_invalid_credentials_show_error(login_page: LoginPage,
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
