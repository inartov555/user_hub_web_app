"""
Page object for the Login page.
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Encapsulates interactions with the login page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        # /users page after logging in
        self.users_tab = self.page.locator('#users')

        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.submit = self.page.locator("form button[type='submit']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")

        self.cookie_consent_title = self.page.locator("div[data-tag='cookieConsentTitle']")
        self.cookie_consent_body = self.page.locator("p[data-tag='cookieConsentBody']")
        self.cookie_consent_accept = self.page.locator("#cookieAccept")

        self.signup = self.page.locator("a[href='/signup']")
        self.forgot_password = self.page.locator("a[href='/reset-password']")

        self.cookie_consent_div = self.page.locator("div[data-tag='cookieConsentContainer']")

    def open(self) -> None:
        """
        Navigate to the login page.
        """
        self.goto("/login")
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))
        expect(self.username).to_be_visible()

    def fill_credentials(self, username: str, password: str) -> None:
        """
        Fill the username and password fields.

        Args:
            username: Username to type into the form.
            password: Password to type into the form.
        """
        self.username.fill(username)
        self.password.fill(password)

    def submit_credentials_success(self, username: str, password: str) -> None:
        """
        Expected: Successful login.
        Submitting the input credentials and waiting for the /users page
        """
        self.fill_credentials(username, password)
        self.submit.click()
        self.page.wait_for_url(re.compile(r".*/users$"))
        expect(self.page).to_have_url(re.compile(r".*/users$"))
        # Wait for the login API call to succeed
        with self.page.expect_response(re.compile(r".*/api/v1/users/\?page.*"), timeout=60000) as res:
            pass  # we just wait for the /users page to load
        assert res.value.ok, f"Login failed: {res.value.status}"
        # Additional checks for elements on the /users page
        users_tab_loc.wait_for(state="visible")
        search_input_loc.wait_for(state="visible")

    def submit_credentials_error(self, username: str, password: str) -> None:
        """
        Expected: Failed login.
        Submitting the input credentials and waiting for the error message on the /login page
        """
        self.fill_credentials(username, password)
        self.submit.click()
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))
        self.assert_error_visible()

    def click_create_account_link(self) -> None:
        """
        Clicking the Create account link on the Login page
        """
        self.signup.click()
        self.page.wait_for_url(re.compile(r".*/signup$"))
        expect(self.page).to_have_url(re.compile(r".*/signup$"))

    def click_forgot_password_link(self) -> None:
        """
        Clicking the Forgot password? link on the Login page
        """
        self.forgot_password.click()
        self.page.wait_for_url(re.compile(r".*/reset-password$"))
        expect(self.page).to_have_url(re.compile(r".*/reset-password$"))

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed login attempt.
        """
        expect(self.error).to_be_visible()

    def assert_on_login_page(self) -> None:
        """
        Assert that the current page is still the login page.
        """
        expect(self.username).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/login$"))

    def accept_cookie_consent_if_present(self) -> None:
        """
        Handling cookie consent overlay, if present
        """
        try:
            self.cookie_consent_accept.wait_for(state="visible")
        except TimeoutError:
            return  # No cookie consent overlay
        self.cookie_consent_accept.click()
        expect(self.cookie_consent_accept).to_be_hidden()

    def remove_cookie_consent_popup_from_dom(self) -> None:
        """
        Remove cookie consent's whole div block from DOM
        """
        self.cookie_consent_div.evaluate("el => el.remove()")
