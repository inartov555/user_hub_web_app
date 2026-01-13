"""
Tests for the Signup page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from core.constants import LocaleConsts, ThemeConsts
from pages.signup_page import SignupPage
from pages.login_page import LoginPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
def test_signup_page_renders(signup_page: SignupPage,
                             ui_theme_param: Theme,
                             ui_locale_param: str) -> None:
    """
    Signup page should render in all supported test themes/locales.
    """
    signup_page.ensure_theme(ui_theme_param)
    signup_page.ensure_locale(ui_locale_param)
    signup_page.assert_sign_up_is_loaded()
    # Verifying localization
    actual = signup_page.page_title.text_content()
    expected = "Sign up"
    signup_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.parametrize("suffix", ["oak", "viburnum", "spruce"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_signup_with_random_username(page: Page,
                                     signup_page: SignupPage,
                                     login_page: LoginPage,
                                     suffix: str) -> None:
    """
    Attempt signup with a random username; backend may accept or reject duplicates.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "changeme123"
    """
    username = f"ui-test-{suffix}"
    email = f"{username}@test.com"
    password = "changeme123"
    signup_page.submit_credentials_success(email, username, password)
    # The user is redirected to the Login page after successful user creation
    # Now, let's check if just created user can login
    login_page.submit_credentials_success(username, password)
    users_table_page = UsersTablePage(page)
    # Verifying if username of just created user is contained in the greeting message
    users_table_page.assert_username_contained_in_greeting_message(username)


def test_signup_link_back_to_login(signup_page: SignupPage) -> None:
    """
    Signup page should link back to the login page.
    """
    signup_page.click_sign_in_link()
