"""
Tests for the Signup page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from pages.signup_page import SignupPage
from pages.login_page import LoginPage
from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "es-ES"])
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_signup_page_renders(page: Page,
                             signup_page: SignupPage,
                             ui_theme_param: Theme,
                             ui_locale_param: str) -> None:
    """
    Signup page should render in all supported test themes/locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    expect(signup_page.username).to_be_visible()
    expect(signup_page.email).to_be_visible()
    expect(signup_page.password).to_be_visible()
    # Verifying localization
    actual = signup_page.page_title.text_content()
    expected = "Sign up"
    signup_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.parametrize("suffix", ["one", "two", "three"])
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
    signup_page.fill_form(email, username, password)
    signup_page.save.click()
    # The user is redirected to the Login page after successful user creation
    page.wait_for_url(re.compile(r".*/login$"))
    expect(page).to_have_url(re.compile(r".*/login$"))
    # Now, let's check if just created user can login
    login_page.fill_credentials(username, password)
    login_page.submit.click()
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    users_table_page = UsersTablePage(page)
    # Verifying if username of just created user is contained in the greeting message
    users_table_page.assert_username_contained_in_greeting_message(username)


def test_signup_link_back_to_login(page: Page,
                                   signup_page: SignupPage) -> None:
    """
    Signup page should link back to the login page.
    """
    signup_page.login.click()
    page.wait_for_url(re.compile(r".*/login$"))
    expect(page).to_have_url(re.compile(r".*/login$"))
