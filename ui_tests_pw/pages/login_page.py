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
        self.cookie_consent_backdrop1 = self.page.locator("div[data-tag='cookieConsentBackdrop1']")
        self.cookie_consent_backdrop2 = self.page.locator("div[data-tag='cookieConsentBackdrop2']")

    def open(self) -> None:
        """
        Navigate to the login page.
        """
        self.goto("/login")
        self.assert_login_page_is_displayed()

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
        self.wait_for_the_users_table_page_to_load()

    def submit_credentials_error(self, username: str, password: str) -> None:
        """
        Expected: Failed login.
        Submitting the input credentials and waiting for the error message on the /login page
        """
        self.fill_credentials(username, password)
        self.submit.click()
        self.assert_login_page_is_displayed()
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
        # self.page.add_init_script("""
        #  () => {
        #    localStorage.setItem("cookie_consent_accepted_v1", "1");
        #    document.cookie = "cookie_consent=accepted; Path=/; SameSite=Lax";
        #  }
        # """)
        # self.reload()

        self.cookie_consent_div.evaluate("el => el.style.display = 'none'")
        expect(self.cookie_consent_div).not_to_be_visible()

        # if self.cookie_consent_div.count() > 0:
        #    self.cookie_consent_div.evaluate("el => el.remove()")
        # if self.cookie_consent_backdrop1.count() > 0:
        #    self.cookie_consent_backdrop1.evaluate("el => el.remove()")
        # if self.cookie_consent_backdrop2.count() > 0:
        #    self.cookie_consent_backdrop2.evaluate("el => el.remove()")
