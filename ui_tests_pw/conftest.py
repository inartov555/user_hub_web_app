"""
conftest.py
"""

import os
# import time
# import json
# from typing import Generator
from urllib.parse import urljoin

import pytest
# from playwright.sync_api import Browser, BrowserContext, expect
from playwright.sync_api import Page
import requests


BASE_URL = os.getenv("BASE_URL", "http://localhost:5173").rstrip("/")
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1").rstrip("/")

ADMIN = (os.getenv("ADMIN_USERNAME", "admin"), os.getenv("ADMIN_PASSWORD", "changeme123"))
USER = (os.getenv("USER_USERNAME", "test1"), os.getenv("USER_PASSWORD", "megaboss19"))


@pytest.fixture(name="base_url", scope="session")
def base_url_new() -> str:
    """
    Base URL
    """
    return BASE_URL


@pytest.fixture(name="api_url", scope="session")
def api_url_new() -> str:
    """
    API URL
    """
    return API_URL


@pytest.fixture(scope="session", autouse=True)
def ensure_runtime(api_url: str):
    """
    Try to warm backend & ensure runtime-auth is cached
    """
    try:
        requests.get(urljoin(api_url + "/", "system/runtime-auth/"), timeout=10)
    except requests.exceptions.Timeout:
        pass


@pytest.fixture(name="admin_tokens", scope="session")
def admin_tokens_new(api_url: str):
    """
    Admin user's token
    """
    r = requests.post(urljoin(api_url + "/", "auth/jwt/create/"),
                      json={"username": ADMIN[0], "password": ADMIN[1]}, timeout=15)
    r.raise_for_status()
    tokens = r.json()
    return tokens


@pytest.fixture(name="user_tokens", scope="session")
def user_tokens_new(api_url: str):
    """
    Regular user's token
    """
    r = requests.post(urljoin(api_url + "/", "auth/jwt/create/"),
                      json={"username": USER[0], "password": USER[1]}, timeout=15)
    r.raise_for_status()
    return r.json()


# @pytest.fixture()
# def fresh_page(context: BrowserContext, base_url: str, page: Page) -> Page:
@pytest.fixture()
def fresh_page(base_url: str, page: Page) -> Page:
    """
    Reset storage for each test to avoid cross-test leakage
    """
    page.goto(base_url + "/login")
    page.evaluate("""() => { localStorage.clear(); sessionStorage.clear(); }"""
    )
    return page


def _apply_tokens_to_page(page: Page, tokens: dict):
    """
    Apply tokens to paged to the web browser's localStorage
    """
    access = tokens.get("access")
    refresh = tokens.get("refresh")
    page.add_init_script(
        """
        (token, rtoken) => {
          localStorage.setItem('access', token);
          if (rtoken) localStorage.setItem('refresh', rtoken);
        }
    """,
        access,
        refresh,
    )


@pytest.fixture()
def logged_in_admin_page(page: Page, base_url: str, admin_tokens):
    """
    Logged in users table page (admin user)
    """
    _apply_tokens_to_page(page, admin_tokens)
    page.goto(base_url + "/users")
    return page


@pytest.fixture()
def logged_in_user_page(page: Page, base_url: str, user_tokens):
    """
    Logged in users table page (regular user)
    """
    _apply_tokens_to_page(page, user_tokens)
    page.goto(base_url + "/users")
    return page


# A small helper to set app auth settings via API (admin only)
def set_auth_settings(access_token: str, renew: int, idle: int, access_life: int, rotate: bool):
    """
    Set authentication settings
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "JWT_RENEW_AT_SECONDS": int(renew),
        "IDLE_TIMEOUT_SECONDS": int(idle),
        "ACCESS_TOKEN_LIFETIME": int(access_life),
        "ROTATE_REFRESH_TOKENS": bool(rotate),
    }
    r = requests.put(urljoin(API_URL + "/", "system/settings/"), json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    # Also prime /system/runtime-auth/ (frontend reads these into localStorage)
    requests.get(urljoin(API_URL + "/", "system/runtime-auth/"), headers=headers, timeout=10)


@pytest.fixture()
def short_lived_tokens(admin_tokens):
    """
    Keep access small to exercise refresh flow
    """
    set_auth_settings(admin_tokens["access"], renew=3, idle=30, access_life=8, rotate=True)
    return True
