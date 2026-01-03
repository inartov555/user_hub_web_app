"""
Page object for the Signup page.
"""

from __future__ import annotations
import re

from playwright.sync_api import Page, expect

from .base_page import BasePage


class SignupPage(BasePage):
    """
    Encapsulates the registration / signup page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.email = self.page.locator("#email")
        self.username = self.page.locator("#username")
        self.password = self.page.locator("#password")
        self.save = self.page.locator("#create")
        self.login = self.page.locator("a[href='/login']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")

    def open(self) -> None:
        """
        Open the signup page.
        """
        self.goto("/signup")

    def fill_form(self, username: str, email: str, password: str) -> None:
        """
        Fill the signup form fields.
        """
        self.username.fill(username)
        self.email.fill(email)
        self.password.fill(password)

    def submit_credentials_success(self, username: str, email: str, password: str) -> None:
        """
        Expected: Successful user creation.
        Submitting the input credentials and waiting for the /login page
        """
        self.fill_form(username, email, password)
        self.save.click()
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))

    def submit_credentials_error(self, username: str, email: str, password: str) -> None:
        """
        Expected: Failed user creation.
        Submitting the input credentials and waiting for the error message on the /signup page
        """
        self.fill_form(username, email, password)
        self.save.click()
        self.page.wait_for_url(re.compile(r".*/signup$"))
        expect(self.page).to_have_url(re.compile(r".*/signup$"))
        self.assert_error_visible()

    def click_sign_in_link(self) -> None:
        """
        Clicking the Sign in link on the Sign up page
        """
        self.login.click()
        self.page.wait_for_url(re.compile(r".*/login$"))
        expect(self.page).to_have_url(re.compile(r".*/login$"))

    def assert_error_visible(self) -> None:
        """
        Assert that an error message is visible after a failed signup attempt.
        """
        expect(self.error).to_be_visible()
