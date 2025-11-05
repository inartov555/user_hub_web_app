"""
Tests related to login
"""

import os
import time

import pytest
from playwright.sync_api import expect

from ui_tests.src.pages.base_page import BasePage
from ui_tests.src.pages.login_page import LoginPage


@pytest.mark.auth
@pytest.mark.parametrize("username,password,ok", [
    (os.getenv("USER_USERNAME", "test1"), os.getenv("USER_PASSWORD", "megaboss19"), True),
    ("admin", os.getenv("ADMIN_PASSWORD", "changeme123"), True),
    ("nosuch", "bad", False),
    ("", "", False),
])
def test_login_flow(fresh_page, base_url, username, password, ok):
    """
    Docstring placeholder
    """
    login = LoginPage(fresh_page, base_url)
    login.open()
    login.login(username, password)
    if ok:
        # Should land on Users page
        expect(fresh_page).to_have_url(lambda url: url.path.startswith("/users"))
        expect(fresh_page.get_by_role("heading", name="Users")).to_be_visible()
    else:
        # Should remain on login and display error
        expect(fresh_page).to_have_url(lambda url: url.path.startswith("/login"))
        expect(fresh_page.get_by_role("alert")).to_be_visible()


def test_protected_redirect_requires_login(fresh_page, base_url):
    """
    Docstring placeholder
    """
    # Directly visit a protected page — should redirect to login
    fresh_page.goto(base_url + "/users")
    expect(fresh_page).to_have_url(lambda u: u.path.startswith("/login"))
