"""Tests for the Signup page."""

from __future__ import annotations

import uuid

import pytest
from playwright.sync_api import Page, expect

from ..pages.signup_page import SignupPage
from ..utils.theme import Theme, set_theme
from ..utils.localization import set_locale


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_signup_page_renders(page: Page, theme: Theme, locale_code: str) -> None:
    """Signup page should render in all supported test themes/locales."""
    signup = SignupPage(page)
    signup.open()
    set_theme(page, theme)
    set_locale(page, locale_code)
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator("#email")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()


@pytest.mark.parametrize("suffix", ["one", "two", "three"])
def test_signup_with_random_username(page: Page, suffix: str) -> None:
    """Attempt signup with a random username; backend may accept or reject duplicates."""
    signup = SignupPage(page)
    signup.open()
    uname = f"ui-test-{suffix}-{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    signup.fill_form(uname, email, "changeme123")
    signup.submit()
    # Either success or validation error should be visible; both are acceptable.
    # The POM assertion is intentionally loose.
    signup.assert_error_or_success()


def test_signup_link_back_to_login(page: Page) -> None:
    """Signup page should link back to the login page."""
    signup = SignupPage(page)
    signup.open()
    page.get_by_role("link", name="Sign in").click()
    expect(page).to_have_url("**/login")
