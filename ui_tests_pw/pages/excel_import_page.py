"""Page object for the Excel import page (admin-only)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class ExcelImportPage(BasePage):
    """Encapsulates the Excel import UI for bulk user operations."""

    def open(self) -> None:
        """Open the Excel import page."""
        self.goto("/import-excel")

    def download_template(self) -> None:
        """Click the 'Download template' button."""
        with self.page.expect_download() as _download:
            self.page.locator("#downloadTemplate").click()

    def upload_template(self, path: str) -> None:
        """Upload an Excel template file from the given path."""
        self.page.set_input_files("input[type='file']", path)
        self.page.locator("#importTemplate").click()

    def assert_result_summary_visible(self) -> None:
        """Assert that the result summary area is visible after import."""
        expect(self.page.locator("text=processed")).to_be_visible()
