"""
Page object for the admin Settings page.
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Encapsulates the application settings form (admin-only).
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.rotate_refresh_token = self.page.locator("#rotateRefreshTokens")
        self.renew_at_sec = self.page.locator("#renewAtSeconds")
        self.idle_timeout_sec = self.page.locator("#idleTimeoutSeconds")
        self.access_token_lifetime = self.page.locator("#accessTokenLifetime")
        self.save = self.page.locator("form div button[type='submit']")

    def open(self) -> None:
        """
        Open the settings page.
        """
        self.goto("/settings")
        self.verify_app_settings_page_uri_is_open()

    def change_values_save_success(self,
                                   rotate_refresh_token: bool,
                                   renew_at_sec: int,
                                   idle_timeout_sec: int,
                                   access_token_lifetime: int) -> None:
        """
        Enter values -> Save -> Success
        """
        self.set_refresh_token_rotation(rotate_refresh_token)
        self.change_idle_timeout(idle_timeout_sec)
        self.change_access_token_lifetime(access_token_lifetime)
        # Consider UI logic: 70% of access_token_lifetime is set to renew_at_sec automatically
        # after setting access_token_lifetime, so update renew_at_sec after changing
        # access_token_lifetime
        if rotate_refresh_token:
            # This param is shown on UI only if self.rotate_refresh_token is set to true
            self.change_renew_token_at_seconds(renew_at_sec)
        self.save.click()
        # UI logic: button becomes disabled after clicking and before getting a response
        expect(self.save).to_be_enabled()
        self.assert_there_s_no_error()

    def change_values_save_error(self,
                                 rotate_refresh_token: bool,
                                 renew_at_sec: int,
                                 idle_timeout_sec: int,
                                 access_token_lifetime: int) -> None:
        """
        Enter values -> Save -> Error
        """
        self.set_refresh_token_rotation(rotate_refresh_token)
        self.change_idle_timeout(idle_timeout_sec)
        self.change_access_token_lifetime(access_token_lifetime)
        # Consider UI logic: 70% of access_token_lifetime is set to renew_at_sec automatically
        # after setting access_token_lifetime, so update renew_at_sec after changing
        # access_token_lifetime
        if rotate_refresh_token:
            # This param is shown on UI only if self.rotate_refresh_token is set to true
            self.change_renew_token_at_seconds(renew_at_sec)
        self.save.click()
        # UI logic: button becomes disabled after clicking and before getting a response
        expect(self.save).to_be_enabled()
        self.assert_error_visible()

    def assert_loaded(self) -> None:
        """
        Assert that core settings fields are visible.
        """
        cur_value = self.rotate_refresh_token.input_value()
        expect(self.rotate_refresh_token).to_be_visible()
        if cur_value == "true":
            # This param is shown on UI only if self.rotate_refresh_token is set to true
            expect(self.renew_at_sec).to_be_visible()
        else:
            expect(self.renew_at_sec).not_to_be_visible()
        expect(self.idle_timeout_sec).to_be_visible()
        expect(self.access_token_lifetime).to_be_visible()

    def set_refresh_token_rotation(self, value: bool) -> None:
        """
        Set True/False for the ROTATE_REFRESH_TOKENS param to enable/disable refresh token rotation
        """
        value_to_select = "true" if value else "false"
        self.rotate_refresh_token.select_option(value_to_select)

    def change_renew_token_at_seconds(self, value: int) -> None:
        """
        Set a new value for the JWT_RENEW_AT_SECONDS param
        """
        self.renew_at_sec.fill(str(int(value)))

    def change_idle_timeout(self, value: int) -> None:
        """
        Set a new value for the IDLE_TIMEOUT_SECONDS param
        """
        self.idle_timeout_sec.fill(str(int(value)))

    def change_access_token_lifetime(self, value: int) -> None:
        """
        Set a new value for the ACCESS_TOKEN_LIFETIME param
        """
        self.access_token_lifetime.fill(str(int(value)))
