"""
Page object for the Excel import page (admin-only).
"""

from __future__ import annotations
import re

from playwright.sync_api import expect, Page, Download

from .base_page import BasePage


class ExcelImportPage(BasePage):
    """
    Encapsulates the Excel import UI for bulk user operations.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.import_template_btn = self.page.locator("#importTemplate")
        self.download_template_btn = self.page.locator("#downloadTemplate")
        self.input_file = self.page.locator("input[type='file']")
        self.error = self.page.locator("div[data-tag='simpleErrorMessage'] p")
        self.success_title = page.locator('div[data-tag="resultSuccessTitle"]')
        self.success_body = page.locator('div[data-tag="resultSuccessBody"]')

    def open(self) -> None:
        """
        Open the Excel import page.
        """
        self.goto("/import-excel")
        self.page.wait_for_url(re.compile(r".*/import-excel$"))
        expect(self.page).to_have_url(re.compile(r".*/import-excel$"))

    def download_template(self) -> Download:
        """
        Click the 'Download template' button.
        """
        with self.page.expect_download() as _download:
            self.download_template_btn.click()
        return _download

    def upload_template(self, path: str) -> None:
        """
        Upload an Excel template file from the given path.
        """
        expect(self.input_file).to_be_visible()
        self.page.set_input_files(self.input_file, path)
        self.import_template_btn.click()

    def assert_result_summary_visible(self) -> None:
        """
        Assert that the result summary area is visible after import.
        """
        expect(self.success_title).to_be_visible()
        expect(self.success_title).to_have_text(re.compile(r".+"))
        expect(self.success_body).to_be_visible()
        expect(self.success_body).to_have_text(re.compile(r".+"))

    def assert_error_alert_shown(self) -> None:
        """
        Verify that error message is shown
        """
        expect(self.error).to_be_visible()

    def assert_there_s_no_error(self) -> None:
        """
        Assert that there's no error after importing an excel spreadsheet
        """
        expect(self.error).not_to_be_visible()

    def assert_loaded(self) -> None:
        """
        Verify if Excel Import page is load and key elements are shown
        """
        expect(self.import_template_btn).to_be_visible()
        expect(self.download_template_btn).to_be_visible()
        expect(self.input_file).to_be_visible()

    def import_excel_file_success(self, file_to_import: str) -> None:
        """
        Select an Excel file -> Import -> Success
        """
        if file_to_import:
            self.input_file.set_input_files(file_to_import)
        self.import_template_btn.click()
        # UI logic: button becomes disabled after clicking and before getting response
        expect(self.import_template_btn).to_be_enabled()
        self.assert_there_s_no_error()

    def import_excel_file_error(self, file_to_import: str) -> None:
        """
        Select an Excel file -> Import -> Error
        """
        if file_to_import:
            self.input_file.set_input_files(file_to_import)
        self.import_template_btn.click()
        # UI logic: button becomes disabled after clicking and before getting response
        expect(self.import_template_btn).to_be_enabled()
        self.assert_error_alert_shown()
