"""
Tests for the Users table page, including multi-column sorting.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.users_table_page import UsersTablePage
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from config import DEFAULT_REGULAR_USERNAME


@pytest.mark.admin
@pytest.mark.theme
@pytest.mark.localization
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("locale_code", ["en-US", "uk-UA"])
def test_users_table_admin_theme_and_locale(logged_in_admin: Page, theme: Theme, locale_code: str) -> None:
    """
    Admin should see the users table in all tested themes/locales.
    """
    page = logged_in_admin
    set_theme(page, theme)
    set_locale(page, locale_code)
    users = UsersTablePage(page)
    users.open()
    expect(users.search_input).to_be_visible()
    users.assert_admin_controls_visible()


@pytest.mark.regular_user
def test_users_table_regular_user_has_restricted_controls(logged_in_regular: Page) -> None:
    """
    Regular user should not see admin-only controls on the users table.
    """
    users = UsersTablePage(logged_in_regular)
    users.open()
    users.assert_admin_controls_hidden_for_regular_user()


@pytest.mark.sorting
def test_users_table_multi_column_sort_admin(logged_in_admin: Page) -> None:
    """
    Admin can apply a multi-column sort (username then email) and see sort indices.
    """
    page = logged_in_admin
    users = UsersTablePage(page)
    users.open()
    users.sort_by_username_then_email()
    labels = users.get_sort_order_labels()
    assert "#1" in labels and "#2" in labels


@pytest.mark.sorting
def test_users_table_clear_sort_resets_order(logged_in_admin: Page) -> None:
    """
    Clear sort button should remove explicit multi-column sort labels.
    """
    page = logged_in_admin
    users = UsersTablePage(page)
    users.open()
    users.sort_by_username_then_email()
    users.clear_sort_btn.click()
    labels = users.get_sort_order_labels()
    assert labels == []


@pytest.mark.regular_user
def test_users_table_search_filters_results(logged_in_regular: Page) -> None:
    """
    Typing into the search box should filter table results.
    """
    users = UsersTablePage(logged_in_regular)
    users.open()
    users.search_input.fill(DEFAULT_REGULAR_USERNAME)
    # After a debounce & fetch round-trip, at least one row should remain.
    page = logged_in_regular
    page.wait_for_timeout(500)
    rows = page.locator("tbody tr")
    assert rows.count() >= 1
