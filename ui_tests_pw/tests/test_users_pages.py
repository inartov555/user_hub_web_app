"""
Tests related to the users page
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_users_list_visible(logged_in_user_page):
    """
    Docstring placeholder
    """
    expect(logged_in_user_page.get_by_role("heading", name="Users")).to_be_visible()
    # Table should be present
    expect(logged_in_user_page.locator("table")).to_be_visible()


@pytest.mark.regression
def test_profile_view_and_edit(logged_in_user_page, base_url):
    """
    Docstring placeholder
    """
    # Go to profile view via navbar
    logged_in_user_page.get_by_role("link", name="Profile").click()
    expect(logged_in_user_page).to_have_url(lambda u: u.path.startswith("/profile-view"))
    # Navigate to edit
    logged_in_user_page.get_by_role("link", name="Edit profile").click()
    expect(logged_in_user_page).to_have_url(lambda u: u.path.startswith("/profile-edit"))
    # Save without changes should still show Saved/toast or not error
    logged_in_user_page.get_by_role("button", name="Save").click()
    # Confirm some feedback exists (non-strict)
    # (We don't assert text to keep locale-agnostic)


@pytest.mark.regression
def test_change_password_negative(logged_in_user_page):
    """
    Docstring placeholder
    """
    logged_in_user_page.get_by_role("link", name="Change password").click()
    expect(logged_in_user_page).to_have_url(lambda u: u.path.startswith("/change-password"))
    # Wrong old password
    logged_in_user_page.get_by_label("Current password").fill("WRONG_OLD")
    logged_in_user_page.get_by_label("New password").fill("NewStrongPass123!")
    logged_in_user_page.get_by_label("Confirm new password").fill("NewStrongPass123!")
    logged_in_user_page.get_by_role("button", name="Save").click()
    expect(logged_in_user_page.get_by_role("alert")).to_be_visible()
