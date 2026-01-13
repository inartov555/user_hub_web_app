"""
Tests for the About website page.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config import (
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from core.constants import LocaleConsts, ThemeConsts
from pages.about_website_page import AboutWebsitePage
from pages.login_page import LoginPage
from utils.theme import Theme


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.unauthorized
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_verify_there_are_login_and_signup_links_for_logged_in_user(about_website_page: AboutWebsitePage,
                                                                    login_page: LoginPage,
                                                                    ui_theme_param: Theme,
                                                                    ui_locale_param: str) -> None:
    """
    About website page should render correctly under multiple themes and locales.
    Case: not logged in user.
    """
    login_page.click_about_website_tab()
    about_website_page.ensure_theme(ui_theme_param)
    about_website_page.ensure_locale(ui_locale_param)
    about_website_page.assert_info_message()
    about_website_page.assert_there_are_login_and_signup_links()
    # Verifying localization
    actual = about_website_page.page_title.text_content()
    expected = "About website"
    about_website_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.authorized
@pytest.mark.parametrize("ui_theme_param", ThemeConsts.ALL_SUPPORTED_THEMES)
@pytest.mark.parametrize("ui_locale_param", LocaleConsts.ALL_SUPPORTED_LOCALES)
@pytest.mark.usefixtures("cleanup_set_default_theme_and_locale")
def test_verify_that_there_s_no_login_and_signup_links_for_logged_in_user(about_website_page: AboutWebsitePage,
                                                                          login_page: LoginPage,
                                                                          ui_theme_param: Theme,
                                                                          ui_locale_param: str
                                                                         ) -> None:
    """
    The About website page should NOT have the Signup and Login link when user is logged in.
    Case: Logged in user.
    """
    login_page.submit_credentials_success(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    login_page.click_about_website_tab()
    about_website_page.ensure_theme(ui_theme_param)
    about_website_page.ensure_locale(ui_locale_param)
    about_website_page.assert_info_message()
    about_website_page.assert_no_login_and_sign_up_links()
    # Verifying localization
    actual = about_website_page.page_title.text_content()
    expected = "About website"
    about_website_page.assert_text_localization(ui_locale_param, actual, expected)


@pytest.mark.unauthorized
def test_links_to_signup_and_login(page: Page,
                                   login_page: LoginPage,
                                   about_website_page: AboutWebsitePage) -> None:
    """
    The About website page should expose links to the Signup and Login pages (only for unauthorized users).
    """
    login_page.click_about_website_tab()
    # Case: Log in page is opened after clicking the Log in link
    about_website_page.click_log_in_link()
    page.go_back()  # getting back to the Log in page to check the next case
    # Case: Sign up page is opened after clicking the Sign up link
    about_website_page.click_sign_up_link()
