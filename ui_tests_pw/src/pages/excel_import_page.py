
from __future__ import annotations
from playwright.sync_api import Page, expect
from .base_page import BasePage
import os

class ExcelImportPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self):
        self.goto("/import-excel")

    def upload_template(self, path: str):
        self.page.set_input_files("input[type=file]", path)
        self.page.get_by_role("button", name="Upload").click()
        expect(self.page.get_by_role("alert")).to_be_visible()
