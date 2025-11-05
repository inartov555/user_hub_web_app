
from __future__ import annotations
from playwright.sync_api import Page, expect
from .base_page import BasePage

class ProfileViewPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self):
        self.goto("/profile-view")

class ProfileEditPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
    def open(self):
        self.goto("/profile-edit")
    def set_first_last(self, first: str, last: str):
        self.page.get_by_label("First name").fill(first)
        self.page.get_by_label("Last name").fill(last)
    def save(self):
        self.page.get_by_role("button", name="Save").click()
        expect(self.page.get_by_text("Saved")).to_be_visible()
