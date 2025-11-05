"""
Tests related to localization
"""

import pytest
from playwright.sync_api import expect

from src.pages.base_page import BasePage


@pytest.mark.i18n
@pytest.mark.parametrize("locale,expected_login_label", [
    ("en-US", "Sign in"),
    ("es-ES", "Iniciar sesión"),
    ("pl-PL", "Zaloguj się"),
    ("uk-UA", "Увійти"),
    ("et-EE", "Logi sisse"),
])
def test_login_page_localization(fresh_page, locale, expected_login_label):
    """
    Docstring placeholder
    """
    base = BasePage(fresh_page)
    base.set_locale(locale)
    base.goto("/login")
    expect(fresh_page.get_by_role("button", name=expected_login_label)).to_be_visible()


@pytest.mark.i18n
def test_nav_localization_logged_in(logged_in_user_page):
    """
    Docstring placeholder
    """
    # Switch locale via localStorage and reload
    logged_in_user_page.evaluate("""() => localStorage.setItem('i18nextLng','es-ES')""")
    logged_in_user_page.reload()
    expect(logged_in_user_page.get_by_role("link", name="Usuarios")).to_be_visible()
