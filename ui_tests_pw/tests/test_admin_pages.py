
import os
import time
import pytest
from playwright.sync_api import expect

def open_additional(page):
    # Admin's "Additional" toggle reveals row 2 nav items
    page.get_by_role("button", name="Additional").click()

@pytest.mark.regression
def test_admin_settings_update(logged_in_admin_page):
    open_additional(logged_in_admin_page)
    logged_in_admin_page.get_by_role("link", name="Settings").click()
    expect(logged_in_admin_page).to_have_url(lambda u: u.path.startswith("/settings"))
    # Set some values
    logged_in_admin_page.get_by_label("JWT_RENEW_AT_SECONDS").fill("120")
    logged_in_admin_page.get_by_label("IDLE_TIMEOUT_SECONDS").fill("900")
    logged_in_admin_page.get_by_label("ACCESS_TOKEN_LIFETIME").fill("600")
    # Save
    logged_in_admin_page.get_by_role("button", name="Save").click()
    # Confirmation
    expect(logged_in_admin_page.get_by_text("App settings")).to_be_visible()

@pytest.mark.regression
def test_excel_import(logged_in_admin_page, base_url):
    open_additional(logged_in_admin_page)
    logged_in_admin_page.get_by_role("link", name="Import from Excel").click()
    expect(logged_in_admin_page).to_have_url(lambda u: u.path.startswith("/import-excel"))
    # Upload the example template
    logged_in_admin_page.set_input_files("input[type=file]", "test_data/import_template_EXAMPLE.xlsx")
    logged_in_admin_page.get_by_role("button", name="Upload").click()
    expect(logged_in_admin_page.get_by_role("alert")).to_be_visible()

@pytest.mark.regression
def test_stats_page(logged_in_admin_page):
    open_additional(logged_in_admin_page)
    logged_in_admin_page.get_by_role("link", name="Stats").click()
    expect(logged_in_admin_page).to_have_url(lambda u: u.path.startswith("/stats"))
    # Some chart/text present
    expect(logged_in_admin_page.get_by_text("Online users")).to_be_visible()
