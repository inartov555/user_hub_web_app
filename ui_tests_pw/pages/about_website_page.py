"""
Page object for the About website page.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class AboutWebsitePage(BasePage):
    """
    Page object for the About website page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.login = self.page.locator("a[href='/login']")
        self.signup = self.page.locator("a[href='/signup']")

    def open(self) -> None:
        """
        Open the reset password page.
        """
        self.goto("/about")
        self.verify_about_website_page_uri_is_open()

    def click_log_in_link(self) -> None:
        """
        Clicking the Log in link on the About website page
        """
        self.login.click()
        self.verify_login_page_uri_is_open()

    def click_sign_up_link(self) -> None:
        """
        Clicking the Sign up link on the About website page
        """
        self.login.click()
        self.verify_login_page_uri_is_open()

    def assert_there_are_login_and_signup_links(self) -> None:
        """
        Assert that the Log in and Sign up links are present on the About website page
        for not logged in users
        """
        expect(self.login).to_be_visible()
        expect(self.signup).to_be_visible()

    def assert_no_login_and_sign_up_links(self) -> None:
        """
        Assert that there are NO Log in and/or Sign up page on the About website page
        for logged in users
        """
        expect(self.login).not_to_be_visible()
        expect(self.signup).not_to_be_visible()
