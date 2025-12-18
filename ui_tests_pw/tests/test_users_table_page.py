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
@pytest.mark.parametrize("ui_theme_param", ["light", "dark"])
@pytest.mark.parametrize("ui_locale_param", ["en-US", "uk-UA"])
def test_users_table_admin_theme_and_locale(logged_in_admin: Page,  # pylint: disable=unused-argument
                                            page: Page,
                                            ui_theme_param: Theme,
                                            ui_locale_param: str,
                                            admin_users_page: UsersTablePage) -> None:
    """
    Admin should see the users table in all tested themes/locales.
    """
    set_theme(page, ui_theme_param)
    set_locale(page, ui_locale_param)
    expect(admin_users_page.search_input).to_be_visible()
    admin_users_page.assert_admin_controls_visible()


@pytest.mark.regular_user
def test_users_table_regular_user_has_restricted_controls(logged_in_regular: Page,  # pylint: disable=unused-argument
                                                          regular_users_page: UsersTablePage) -> None:
    """
    Regular user should not see admin-only controls on the users table.
    """
    regular_users_page.assert_admin_controls_hidden_for_regular_user()


@pytest.mark.sorting
def test_users_table_multi_column_sort_admin(logged_in_admin: Page,  # pylint: disable=unused-argument
                                             admin_users_page: UsersTablePage) -> None:
    """
    Admin can apply a multi-column sort (username then email) and see sort indices.
    """
    admin_users_page.sort_by_username_then_email()
    labels = admin_users_page.get_sort_order_labels()
    assert "#1" in labels and "#2" in labels


@pytest.mark.sorting
def test_users_table_clear_sort_resets_order(logged_in_admin: Page,  # pylint: disable=unused-argument
                                             admin_users_page: UsersTablePage) -> None:
    """
    Clear sort button should remove explicit multi-column sort labels.
    """
    admin_users_page.sort_by_username_then_email()
    admin_users_page.clear_sort_btn.click()
    labels = admin_users_page.get_sort_order_labels()
    assert labels == []


@pytest.mark.regular_user
def test_users_table_search_filters_results(logged_in_regular: Page,  # pylint: disable=unused-argument
                                            regular_users_page: UsersTablePage) -> None:
    """
    Typing into the search box should filter table results.
    """
    regular_users_page.search_and_wait_for_results(DEFAULT_REGULAR_USERNAME)
    result_rows = regular_users_page.table_rows
    assert result_rows.count() >= 1
