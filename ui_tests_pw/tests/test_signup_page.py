"""
Tests for the Signup page.
"""

from __future__ import annotations
import re

import pytest
from playwright.sync_api import Page, expect

from utils.theme import Theme, set_theme
from utils.localization import set_locale


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_signup_page_renders(page: Page,
                             signup_page: Page,
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


@pytest.mark.parametrize("suffix", ["one", "two", "three"])
def test_signup_with_random_username(page: Page,
                                     signup_page: Page,
                                     cleanup_delete_users_by_suffix,  # pylint: disable=unused-argument
                                     suffix: str) -> None:
    """
    Attempt signup with a random username; backend may accept or reject duplicates.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
    """
    username = f"ui-test-{suffix}"
    email = f"{username}@test.com"
    signup_page.fill_form(username, email, "changeme123")
    signup_page.save.click()
    # The user is redirected to the Login page after successful user creation
    page.wait_for_url(re.compile(r".*/login$"))
    expect(page).to_have_url(re.compile(r".*/login$"))


def test_signup_link_back_to_login(page: Page,
                                   signup_page: Page) -> None:
    """
    Signup page should link back to the login page.
    """
    signup_page.login.click()
    page.wait_for_url(re.compile(r".*/login$"))
    expect(page).to_have_url(re.compile(r".*/login$"))
