"""
Base page object with shared helpers.
"""

from __future__ import annotations
import re
import time

from playwright.sync_api import Page, expect
from django.utils import translation

from config import frontend_url
from utils.theme import Theme, set_theme
from utils.localization import set_locale, assert_locale_visible
from utils.logger.logger import Logger


log = Logger(__name__)


class BasePage:
    """
    Base class for all page objects.
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the base page.

        Args:
            page (Page): Playwright :class: Page instance.
        """
        self.page: Page = page
        # Not logged in user
        self.username = self.page.locator('#username')
        # Common controls
        self.page_title = self.page.locator('h2')
        self.about_website = self.page.locator('#aboutWebsite')
        self.logout = self.page.locator('#logout')
        self.error_msg = self.page.locator("div[data-tag='simpleErrorMessage']")
        self.info_msg = self.page.locator("div[data-tag='simpleInfoMessage']")
        self.success_msg = self.page.locator("div[data-tag='simpleSuccessMessage']")
        # /users page after logging in
        self.users_tab = self.page.locator('#users')
        self.profile_tab = self.page.locator('#profile')
        self.additional_tab = self.page.locator('#additional')
        self.users_stats_tab = self.page.locator('#userStats')
        self.app_settings_tab = self.page.locator('#settings')
        self.excel_import_tab = self.page.locator('#excelImport')
        self.search_input = self.page.locator('#search')

        # Cookie consent pop-up related elements
        self.cookie_consent_title = self.page.locator("div[data-tag='cookieConsentTitle']")
        self.cookie_consent_body = self.page.locator("p[data-tag='cookieConsentBody']")
        self.cookie_consent_accept = self.page.locator("#cookieAccept")
        self.cookie_consent_div = self.page.locator("div[data-tag='cookieConsentContainer']")

    def goto(self, path: str) -> None:
        """
        Open a relative path on the frontend.

        Args:
            path (str): Relative path such as /login or /users.
        """
        self.page.goto(frontend_url(path), wait_until="load")

    def wait_a_bit(self, timeout: int) -> None:
        """
        Hard-coded wait. Be careful with it, use it responsibly.

        Args:
            timeout (int): timeout >= 0
        """
        log.info(f"Waiting before starting the next step; timeout {timeout}")
        _timeout = timeout if timeout >= 0 else 0
        time.sleep(_timeout)

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
                                 expected_suffix: str = None,
                                 mode: str = "strict") -> None:
        """
        Check text localization

        Args:
            ui_locale_param (str): e.g., en-US
            actual (str): actual text localization retrieved from UI element
            expected (str): expected text localization, provide the text code to retrieve the localization with Django
            expected_suffix (str): e.g., when some numbers added,
                                   'Processed: 50' (expected = 'Processed:', expected_suffix = ' 50'), etc.
            mode (str): one of (contains, strict)
        """
        with translation.override(ui_locale_param.lower()):
            expected = translation.gettext(expected)
        _expected = expected + expected_suffix if expected_suffix else expected
        err_msg = f"Wrong text localization; actual '{actual}'; expected '{_expected}'; mode '{mode}'"
        if mode.lower().strip() == "contains":
            assert _expected in actual, err_msg
        else:
            # strict
            assert _expected == actual, err_msg

    def wait_for_the_users_table_page_to_load(self) -> None:
        """
        Cross-page solution to wait for the Users Table page to show
        """
        self.verify_users_table_page_uri_is_open()

        # Wait for the login API call to succeed
        # with self.page.expect_response(re.compile(r".*/api/v1/users/\?page.*"), timeout=20000) as res:
        #    pass  # we just wait for the /users page to load
        # assert res.value.ok, f"Login failed: {res.value.status}"

        # Additional checks for elements on the /users page
        self.users_tab.wait_for(state="visible")
        self.search_input.wait_for(state="visible")

    def click_logout_and_wait_for_login_page(self) -> None:
        """
        Cross-page solution to log out in UI
        """
        self.logout.click()
        self.assert_login_page_is_displayed()

    def assert_login_page_is_displayed(self) -> None:
        """
        Verify if the Login page is displayed
        """
        self.verify_login_page_uri_is_open()

    def click_about_website_tab(self) -> None:
        """
        Click the About Website tab
        """
        self.about_website.click()
        self.verify_about_website_page_uri_is_open()

    def click_users_tab(self) -> None:
        """
        Click the Users tab
        """
        self.users_tab.click()
        self.wait_for_the_users_table_page_to_load()

    def click_profile_tab(self) -> None:
        """
        Click the Profile tab
        """
        self.profile_tab.click()
        self.verify_profile_view_page_uri_is_open()

    def click_additional_user_stats_tab(self) -> None:
        """
        Click Additional -> User Stats tab
        """
        self.additional_tab.click()
        self.users_stats_tab.click()
        self.verify_user_stats_page_uri_is_open()

    def click_additional_app_settings_tab(self) -> None:
        """
        Click the Additional -> App Settings tab
        """
        self.additional_tab.click()
        self.app_settings_tab.click()
        self.verify_app_settings_page_uri_is_open()

    def click_additional_excel_import_tab(self) -> None:
        """
        Click the Additional -> Excel Import tab
        """
        self.additional_tab.click()
        self.excel_import_tab.click()
        self.verify_excel_import_page_uri_is_open()

    def accept_cookie_consent_if_present(self) -> None:
        """
        Handling the cookie consent overlay, if present
        """
        try:
            self.cookie_consent_accept.wait_for(state="visible")
        except TimeoutError:
            return  # No cookie consent overlay
        self.cookie_consent_accept.click()
        expect(self.cookie_consent_accept).to_be_hidden()

    def hide_cookie_consent_popup_in_dom(self) -> None:
        """
        Hide the cookie consent's whole div block in the DOM by setting display: none.
        It may be needed when, e.g., changing the theme and then reloading the page to see that the pop-up
        can still be applied.
        """
        self.cookie_consent_div.evaluate("el => el.style.display = 'none'")
        expect(self.cookie_consent_div).not_to_be_visible()

    def verify_login_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /login URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))

    def verify_sign_up_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /signup URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/signup$"))
        expect(self.page).to_have_url(re.compile(r".*/signup$"))

    def verify_reset_password_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /reset-password URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/reset-password$"))
        expect(self.page).to_have_url(re.compile(r".*/reset-password$"))

    def verify_users_table_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /users URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/users$"))
        expect(self.page).to_have_url(re.compile(r".*/users$"))

    def verify_confirm_user_delete_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /users/confirm-delete URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/users/confirm-delete$"))
        expect(self.page).to_have_url(re.compile(r".*/users/confirm-delete$"))

    def verify_profile_view_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /profile-view URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/profile-view$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-view$"))

    def verify_change_password_page_uri_is_open(self) -> None:
        """
        Verify that page with /users/${userId}/change-password URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/users/\d+/change-password$"))
        expect(self.page).to_have_url(re.compile(r".*/users/\d+/change-password$"))

    def verify_profile_edit_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /profile-edit URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/profile-edit$"))
        expect(self.page).to_have_url(re.compile(r".*/profile-edit$"))

    def verify_user_stats_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /stats URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/stats$"))
        expect(self.page).to_have_url(re.compile(r".*/stats$"))

    def verify_app_settings_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /settings URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/settings$"))
        expect(self.page).to_have_url(re.compile(r".*/settings$"))

    def verify_excel_import_page_uri_is_open(self) -> None:
        """
        Verify that the page with the /import-excel URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/import-excel$"))
        expect(self.page).to_have_url(re.compile(r".*/import-excel$"))

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible when failure happened
        """
        expect(self.error_msg).to_be_visible()

    def assert_there_s_no_error(self) -> None:
        """
        Assert that there's no error after performing an action
        """
        expect(self.error_msg).not_to_be_visible()

    def assert_info_message(self) -> None:
        """
        Assert that an info message is shown
        """
        expect(self.info_msg).to_be_visible()

    def assert_success_message(self) -> None:
        """
        Assert that a success message is shown
        """
        expect(self.success_msg).to_be_visible()

    def verify_about_website_page_uri_is_open(self) -> None:
        """
        Verify that the page with /about URI is shown now
        """
        self.page.wait_for_url(re.compile(r".*/about$"))
        expect(self.page).to_have_url(re.compile(r".*/about$"))
