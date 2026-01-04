"""
Base page object with shared helpers.
"""

from __future__ import annotations
import re

from playwright.sync_api import Page, expect
from django.utils import translation

from config import frontend_url
from utils.theme import Theme, set_theme
from utils.localization import set_locale, assert_locale_visible


class BasePage:
    """
    Base class for all page objects.

    Each specific page object wraps a Playwright Page instance and provides
    typed helpers for navigation and common UI actions (theme, localization).
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the base page.

        Args:
            page (Page): Playwright :class: Page instance.
        """
        self.page: Page = page
        # Common controls
        self.logout = self.page.locator('#logout')
        # /users page after logging in
        self.users_tab = self.page.locator('#users')
        self.profile_tab = self.page.locator('#profile')
        self.additional_tab = self.page.locator('#additional')
        self.users_stats_tab = self.page.locator('#userStats')
        self.app_settings_tab = self.page.locator('#settings')
        self.excel_import_tab = self.page.locator('#excelImport')
        self.search_input = self.page.locator('#search')

    def goto(self, path: str) -> None:
        """
        Open a relative path on the frontend.

        Args:
            path (str): Relative path such as /login or /users.
        """
        self.page.goto(frontend_url(path), wait_until="load")

    def reload(self) -> None:
        """
        Reload the current page
        """
        self.page.reload(wait_until="load")

    def ensure_theme(self, theme: Theme) -> None:
        """
        Ensure the UI uses the given theme.
        """
        set_theme(self.page, theme)

    def ensure_locale(self, locale_code: str) -> None:
        """
        Ensure the UI uses the given locale code.
        """
        set_locale(self.page, locale_code)

    def assert_locale_available(self, expected_code: str) -> None:
        """
        Assert that the given locale code is visible in the navbar dropdown.
        """
        assert_locale_visible(self.page, expected_code)

    def assert_text_localization(self,
                                 ui_locale_param: str,
                                 actual: str,
                                 expected: str,
                                 mode: str = "strict") -> None:
        """
        Check text localization

        Args:
            ui_locale_param (str): e.g. en-US
            actual (str): actual text localization retrieved from UI element
            expected (str): expected text localization, provide the text code to retrieve the localization with Django
            mode (str): one of (contans, strict)
        """
        with translation.override(ui_locale_param.lower()):
            expected = translation.gettext(expected)
        err_msg = f"Wrong text localization; actual '{actual}'; expected '{expected}'; mode '{mode}'"
        if mode.lower().strip() == "contains":
            assert expected in actual, err_msg
        else:
            # strict
            assert expected == actual, err_msg

    def wait_for_the_users_table_page_to_load(self):
        """
        Cross-page solution to wait for the Users Table page to show
        """
        self.page.wait_for_url(re.compile(r".*/users$"))
        expect(self.page).to_have_url(re.compile(r".*/users$"))
        # Wait for the login API call to succeed
        with self.page.expect_response(re.compile(r".*/api/v1/users/\?page.*"), timeout=60000) as res:
            pass  # we just wait for the /users page to load
        assert res.value.ok, f"Login failed: {res.value.status}"
        # Additional checks for elements on the /users page
        self.users_tab.wait_for(state="visible")
        self.search_input.wait_for(state="visible")

    def click_logout_and_wait_for_login_page(self):
        """
        Cross-page solution to logout in UI
        """
        self.logout.click()
        self.assert_login_page_is_displayed()

    def assert_login_page_is_displayed(self) -> None:
        """
        Verify if Login page is displayed
        """
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))
        expect(self.username).to_be_visible()

    def click_profile_tab(self) -> None:
        """
        Click Profile tab
        """
        self.profile_tab.click()
        self.page.wait_for_url(re.compile(r".*/profile-view$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-view$"))

    def click_additional_user_stats_tab(self) -> None:
        """
        Click Additional -> User Stats tab
        """
        self.additional_tab.click()
        self.users_stats_tab.click()
        self.page.wait_for_url(re.compile(r".*/stats$"))
        expect(self.page).to_have_url(re.compile(r".*/stats$"))

    def click_additional_app_settings_tab(self) -> None:
        """
        Click Additional -> App Settings tab
        """
        self.additional_tab.click()
        self.app_settings_tab.click()
        self.page.wait_for_url(re.compile(r".*/settings$"))
        expect(self.page).to_have_url(re.compile(r".*/settings$"))

    def click_additional_excel_import_tab(self) -> None:
        """
        Click Additional -> Excel Import tab
        """
        self.additional_tab.click()
        self.excel_import_tab.click()
        self.page.wait_for_url(re.compile(r".*/import-excel$"))
        expect(self.page).to_have_url(re.compile(r".*/import-excel$"))
