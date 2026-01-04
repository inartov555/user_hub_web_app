"""
Page object for the Users table page.
"""

from __future__ import annotations
from typing import List

from playwright.sync_api import expect, Page

from pages.base_page import BasePage
from utils.logger.logger import Logger


log = Logger(__name__)


class UsersTablePage(BasePage):
    """
    Encapsulates the Users table view and its sorting / filtering actions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = self.page.locator("h2")
        self.greeting_mes = self.page.locator('#greeting')
        self.addtional_tab = self.page.locator('#additional')

        self.clear_sort_btn = self.page.locator("#clearSort")
        self.delete_users_btn = self.page.locator("#deleteUsers")

        self.check_all_header = self.page.locator('input[data-tag="check-all-rows"]')
        # This locator returs all checkboxes (NON-header ones) for the current page
        self.check_rows = self.page.locator('input[data-tag="check-a-row"]')
        self.sortable_columl_header_str = 'button[data-tag="sort-by-{}"]'
        self.change_password_header = self.page.locator('div[data-tag="changePasswordHeader"]')

        # The list of all Change Password buttons
        self.change_password_btn = self.page.locator('button[data-tag="change-password"]')

        self.sort_labels = self.page.locator("thead th span.text-xs")
        self.is_updating_top = self.page.locator('span[data-tag="isUpdatingTop"]')
        self.table_rows = self.page.locator('tbody tr')

    def open(self) -> None:
        """
        Open the users table page.
        """
        self.goto("/users")

    def search_and_wait_for_results(self, text: str) -> None:
        """
        Typing text to search and waiting while Users Table finishes refreshing data
        """
        expect(self.search_input).to_be_visible()
        self.search_input.fill(text)
        self.wait_till_users_table_update_finished()

    def wait_till_users_table_update_finished(self) -> None:
        """
        There's isUpdating element's text shown while Users Table data is refreshed
        """
        self.is_updating_top.wait_for(state="detached", timeout=30000)

    def sort_by_username_then_email(self) -> None:
        """
        Apply a multi-column sort: first by username, then by email.
        """
        self.change_column_sorting("username", "asc")
        self.change_column_sorting("email", "asc")

    def get_sort_order_labels(self) -> List[str]:
        """
        Return the list of #1, #2 labels rendered for multi-column sort.
        """
        return [self.sort_labels.nth(i).inner_text().strip() for i in range(self.sort_labels.count())]

    def assert_admin_controls_visible(self) -> None:
        """
        Assert that admin-only controls on the users table are visible.
        """
        expect(self.delete_users_btn).to_be_visible()
        # Admins see the bulk select checkbox in the header.
        expect(self.check_all_header).to_be_visible()
        expect(self.change_password_header).to_be_visible()

    def assert_admin_controls_hidden_for_regular_user(self) -> None:
        """
        Assert that admin-only controls are hidden for a regular user.
        """
        expect(self.delete_users_btn).not_to_be_visible()
        # No header-level checkbox for regular user.
        expect(self.check_all_header).to_have_count(0)
        expect(self.change_password_header).to_have_count(0)

    def assert_username_contained_in_greeting_message(self, text: str) -> List[str]:
        """
        Assert that username is contained in the greeting message
        """
        expect(self.greeting_mes).to_contain_text(text)

    def get_current_column_sort_order(self, column: str) -> str:
        """
        Get current column sort order.
        svg contains arrow-down/arrow-up/arrow-up-down in the className attribute.

        Args:
            column (str): one of (username, email, firstname, lastname)

        Returns:
            str, one of (asc, desc, default)
        """
        _column = column.lower()
        if _column not in ("username", "email", "firstname", "lastname"):
            raise ValueError(f"Current value of the column param ({column}) is not correct")
        sorted_column_header_loc = self.page.locator(self.sortable_columl_header_str.format(_column))
        svg_class_attr = sorted_column_header_loc.locator("svg").get_attribute("class")
        # lucide lucide-arrow-up h-4 w-4 = ascending
        # lucide lucide-arrow-down h-4 w-4 = descending
        # lucide lucide-arrow-up-down h-4 w-4 opacity-40 = default
        if "lucide-arrow-up " in svg_class_attr:
            return "asc"
        if "lucide-arrow-down " in svg_class_attr:
            return "desc"
        if "lucide-arrow-up-down " in svg_class_attr:
            return "default"
        return None  # most likely, changed styles

    def change_column_sorting(self, column: str, sort_order: str) -> None:
        """
        Assert that username is contained in the greeting message.

        Args:
            column (str): one of (username, email, firstname, lastname)
            sort_order (str): one of (asc, desc, default)
        """
        _column = column.lower()
        _sort_order = sort_order.lower()
        if _sort_order not in ("asc", "desc", "default"):
            raise ValueError(f"Current value of the sort order ({sort_order}) is not correct")

        cur_sort_order = self.get_current_column_sort_order(_column)
        sorted_column_header_loc = self.page.locator(self.sortable_columl_header_str.format(_column))

        icon_by_order = {
            "asc": "svg.lucide-arrow-up",
            "desc": "svg.lucide-arrow-down",
            "default": "svg.lucide-arrow-up-down",
        }

        def click_until(expected: str) -> None:
            """
            Click column header once and assert the expected icon is visible.
            """
            # If not step, it means that sorting order already is in the expected state
            if step:
                sorted_column_header_loc.click()
                expect(sorted_column_header_loc.locator(icon_by_order[expected])).to_be_visible()

        if _sort_order == cur_sort_order:
            log.warning("Current sort order already is set, no need to change it; "
                        f"column {_column}; current {cur_sort_order}; expected {_sort_order}")

        transition_steps = {
            ("default", "asc"): ["asc"],
            ("default", "desc"): ["asc", "desc"],
            ("asc", "default"): ["desc", "default"],
            ("asc", "desc"): ["desc"],
            ("desc", "default"): ["default"],
            ("desc", "asc"): ["default", "asc"],
            ("default", "default"): [None],
            ("asc", "asc"): [None],
            ("desc", "desc"): [None],
        }

        for step in transition_steps[(cur_sort_order, _sort_order)]:
            click_until(step)

        """
        if cur_sort_order == "default" and _sort_order == "asc":
            # Click to get ascending order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        elif cur_sort_order == "default" and _sort_order == "desc":
            # Click to get ascending order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
            # Click to get desceing order
            _next_expected_sort_loc_str = "svg.lucide-arrow-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        elif cur_sort_order == "asc" and _sort_order == "default":
            # Click to get descending order
            _next_expected_sort_loc_str = "svg.lucide-arrow-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
            # Click to get default order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        elif cur_sort_order == "asc" and _sort_order == "desc":
            # Click to get desceing order
            _next_expected_sort_loc_str = "svg.lucide-arrow-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        elif cur_sort_order == "desc" and _sort_order == "default":
            # Click to get default order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        elif cur_sort_order == "desc" and _sort_order == "asc":
            # Click to get default order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up-down"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
            # Click to get ascending order
            _next_expected_sort_loc_str = "svg.lucide-arrow-up"
            sorted_column_header_loc.click()
            next_expected_sort_order = sorted_column_header_loc.locator(_next_expected_sort_loc_str)
            expect(next_expected_sort_order).to_be_visible()
        """

    def assert_column_sorting(self, column: str, sort_order: str) -> None:
        """
        Assert that the passed sort order for the passed column is actually applied on UI.
        svg contains arrow-down/arrow-up/arrow-up-down in the className attribute.

        Args:
            column (str): one of (username, email, firstname, lastname)
            sort_order (str): one of (asc, desc, default)
        """
        _column = column.lower()
        _sort_order = sort_order.lower()
        if _sort_order not in ("asc", "desc", "default"):
            raise ValueError(f"Current value of the sort order ({sort_order}) is not correct")

        cur_sort_order = self.get_current_column_sort_order(_column)

        if cur_sort_order != sort_order:
            raise AssertionError(f"{_column} column sort order does not match; actual {cur_sort_order}; "
                                 f"expected {_sort_order}")
