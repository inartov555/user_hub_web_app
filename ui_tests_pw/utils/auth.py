"""
Helpers for logging in and preparing test users.
"""

from __future__ import annotations
from typing import Dict, Tuple

import requests
from playwright.sync_api import Page

from .theme import set_theme
from .localization import set_locale
from config import (
    BACKEND_API_BASE,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
    frontend_url,
)


def api_login(username: str, password: str) -> Tuple[str, str]:
    """
    Perform a backend JWT login via the Djoser endpoint.

    Args:
        username: Username to authenticate with.
        password: Password to authenticate with.

    Returns:
        A tuple of (access_token, refresh_token).

    Raises:
        AssertionError: If the login request fails.
    """
    url = f"{BACKEND_API_BASE}/auth/jwt/create/"
    resp = requests.post(url, json={"username": username, "password": password}, timeout=10)
    assert resp.status_code == 200, f"API login failed for {username}: {resp.status_code} {resp.text}"
    data: Dict[str, str] = resp.json()
    return data["access"], data["refresh"]


def ensure_regular_user() -> None:
    """
    Ensure that the default regular user exists.

    The assignment mentions that ``test1`` is created *after* deploying
    the website. To make tests robust, this helper:
    1. Tries to log in as ``test1``.
    2. If login fails (e.g. user not yet created), it creates the user via
       the Djoser registration endpoint.
    """
    try:
        api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
        return  # user already exists
    except AssertionError:
        pass

    # Create user via Djoser registration endpoint (open registration).
    url = f"{BACKEND_API_BASE}/auth/users/"
    payload = {
        "username": DEFAULT_REGULAR_USERNAME,
        "email": f"{DEFAULT_REGULAR_USERNAME}@example.com",
        "password": DEFAULT_REGULAR_PASSWORD,
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code in (201, 400), (
        f"Unexpected status when creating regular user: {resp.status_code} {resp.text}"
    )
    # If the user already exists we can ignore 400; otherwise a 201 means it was created.


def login_via_ui(
    page: Page,
    username: str,
    password: str,
    *,
    theme: str | None = None,
    locale_code: str | None = None,
) -> None:
    """
    Log in via the UI login page, optionally setting theme and locale.

    Args:
        page: Playwright page instance.
        username: Username.
        password: Password.
        theme: Optional theme ("light" or "dark").
        locale_code: Optional locale code such as "en-US".
    """
    page.goto(frontend_url("/login"))
    if theme is not None:
        set_theme(page, theme)  # type: ignore[arg-type]
    if locale_code is not None:
        set_locale(page, locale_code)

    page.fill("#username", username)
    page.fill("#password", password)
    page.locator("form button[type='submit']").click()
    # Wait for navigation to complete — /users is the default redirect.
    page.wait_for_url("**/users")
