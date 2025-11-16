"""Page object for the Users table page."""

from __future__ import annotations

from typing import List

from playwright.sync_api import Page, Locator, expect

from .base_page import BasePage


class UsersTablePage(BasePage):
    """Encapsulates the Users table view and its sorting / filtering actions."""

    def open(self) -> None:
        """Open the users table page."""
        self.goto("/users")

    @property
    def search_input(self) -> Locator:
        """Return the search input locator."""
        return self.page.locator("#search")

    @property
    def clear_sort_button(self) -> Locator:
        """Return the clear-sort button locator."""
        return self.page.locator("button:has-text('Clear sort')").or_(self.page.locator("#clearSort"))

    @property
    def delete_users_button(self) -> Locator:
        """Return the delete-users button locator."""
        return self.page.locator("#deleteUsers")

    def header_by_text(self, text: str) -> Locator:
        """Return a table header locator by its visible text.

        Args:
            text: Visible text of the column header.

        Returns:
            Playwright :class:`Locator` for the header.
        """
        return self.page.locator("thead th").filter(has_text=text)

    def sort_by_username_then_email(self) -> None:
        """Apply a multi-column sort: first by username, then by email."""
        self.header_by_text("Username").locator("button").click()
        self.header_by_text("Email").locator("button").click()

    def get_sort_order_labels(self) -> List[str]:
        """Return the list of ``#1``, ``#2`` labels rendered for multi-column sort."""
        labels = self.page.locator("thead th span.text-xs")
        return [labels.nth(i).inner_text().strip() for i in range(labels.count())]

    def assert_admin_controls_visible(self) -> None:
        """Assert that admin-only controls on the users table are visible."""
        expect(self.delete_users_button).to_be_visible()
        # Admins see the bulk select checkbox in the header.
        expect(self.page.locator("thead input[type='checkbox']")).to_be_visible()

    def assert_admin_controls_hidden_for_regular_user(self) -> None:
        """Assert that admin-only controls are hidden for a regular user."""
        expect(self.delete_users_button).not_to_be_visible()
        # No header-level checkbox for regular user.
        expect(self.page.locator("thead input[type='checkbox']")).to_have_count(0)
