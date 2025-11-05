"""
Tests related to the refresh token rotation
"""

import time

import pytest
# from playwright.sync_api import expect


@pytest.mark.auth
def test_refresh_token_rotation(logged_in_user_page):
    """
    Docstring placeholder
    """
    # Ensure we loaded runtime settings from backend
    logged_in_user_page.reload()
    # Observe initial refresh token
    initial_refresh = logged_in_user_page.evaluate("""() => localStorage.getItem('refresh')""")
    assert initial_refresh, "No refresh token found in localStorage"

    # Wait for proactive refresh window and trigger an API call by visiting Users
    time.sleep(5)  # past renew window
    logged_in_user_page.get_by_role("link", name="Users").click()
    # Give axios interceptor a moment to refresh
    logged_in_user_page.wait_for_timeout(1500)

    rotated = logged_in_user_page.evaluate("""() => localStorage.getItem('refresh')""")
    assert rotated, "No refresh token present after refresh"
    assert rotated != initial_refresh, "Refresh token did not rotate"


@pytest.mark.auth
def test_access_expiration_redirect_to_login(logged_in_user_page):
    """
    Docstring placeholder
    """
    # Let the short access token expire fully
    logged_in_user_page.reload()
    time.sleep(10)  # access_life=8 in fixture
    # Now attempt an API call (navigate within app)
    logged_in_user_page.get_by_role("link", name="Users").click()
    # If refresh flow also expired (idle / refresh too old), you'll be returned to /login
    logged_in_user_page.wait_for_url("**/login", timeout=5000)
