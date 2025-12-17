"""
Page object for the Excel import page (admin-only).
"""

from __future__ import annotations

from playwright.sync_api import expect, Page

from .base_page import BasePage


class ExcelImportPage(BasePage):
    """
    Encapsulates the Excel import UI for bulk user operations.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.import_template_btn = self.page.locator("#importTemplate")
        self.download_template_btn = self.page.locator("#downloadTemplate")
        self.input_file = self.page.locator("input[type='file']")
        self.error = self.page.locator("p.text-red-600")
        self.success_title = page.locator("div.mt-4.text-sm.p-2.rounded-xl.border")

    def open(self) -> None:
        """
        Open the Excel import page.
        """
        self.goto("/import-excel")

    def download_template(self) -> None:
        """
        Click the 'Download template' button.
        """
        with self.page.expect_download() as _download:
            self.download_template_btn.click()

    def upload_template(self, path: str) -> None:
        """
        Upload an Excel template file from the given path.
        """
        expected(self.input_file).to_be_visible()
        self.page.set_input_files(self.input_file, path)
        self.import_template_btn.click()

    def assert_result_summary_visible(self) -> None:
        """
        Assert that the result summary area is visible after import.
        """
        expect(self.page.locator("text=processed")).to_be_visible()
