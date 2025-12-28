"""
Helpers for logging in and preparing test users.
"""

from __future__ import annotations
from typing import Dict, Tuple
import re

import requests
from playwright.sync_api import Page, expect

from config import (
    BACKEND_API_BASE,
    UI_BASE_PORT,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
    frontend_url,
)
from .theme import set_theme
from .localization import set_locale
from .api_utils import UsersAppApi, ApiError
from .logger.logger import Logger


log = Logger(__name__)


def get_api_utils() -> UsersAppApi:
    """
    Get API Utils
    """
    base_url = BACKEND_API_BASE
    ind_protocol = base_url.find("://")
    protocol = "http"
    host = base_url
    port = UI_BASE_PORT
    if ind_protocol > 0:
        protocol = base_url[0:ind_protocol]
        host = base_url[ind_protocol + 3:]
    ind_port = host.find(":")
    if ind_port > 0:
        host = host[0:ind_port]
        next_symb = base_url[ind_port + 1:ind_port + 2]
        if next_symb != "/":
            temp_port = ""
            for cur_symb in base_url[ind_port + 1:]:
                try:
                    cur_num = int(cur_symb)
                    temp_port += str(cur_num)
                except Exception:  # pylint: disable=broad-exception-caught
                    break
            if temp_port:
                port = temp_port
    api_utils = UsersAppApi(protocol, host, port)
    return api_utils


def ensure_regular_user() -> None:
    """
    Ensure that the default regular user exists.

    The assignment mentions that test1 is created after deploying
    the website. To make tests robust, this helper:
    1. Tries to log in as test1.
    2. If login fails (e.g. user not yet created), it creates the user via
       the Djoser registration endpoint.
    """
    log.info("Ensuring the regular user exists and creating it, if not present")
    try:
        get_api_utils().api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
        return  # user already exists
    except ApiError:
        pass
    access_token =  get_api_utils().api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    get_api_utils().create_user(None,
                                DEFAULT_REGULAR_USERNAME,
                                f"{DEFAULT_REGULAR_USERNAME}@test.com",
                                DEFAULT_REGULAR_PASSWORD)


def login_via_ui(
    page: Page,
    username: str,
    password: str,
    ui_theme: str | None = None,
    ui_locale: str | None = None,
) -> None:
    """
    Log in via the UI login page, optionally setting theme and locale.

    Args:
        page (Page): Playwright page instance.
        username (str): Username.
        password (str): Password.
        ui_theme (str): theme (light or dark).
        ui_locale (str): locale code such as en-US.
    """
    log.info("Log in via UI")
    username_loc = page.locator("#username")
    password_loc = page.locator("#password")
    login_btn_loc = page.locator("form button[type='submit']")
    users_tab_loc = page.locator('#users')

    page.goto(frontend_url("/login"))
    if ui_theme is not None:
        set_theme(page, ui_theme)
    if ui_locale is not None:
        set_locale(page, ui_locale)
    username_loc.fill(username)
    password_loc.fill(password)
    login_btn_loc.click()
    page.wait_for_url(re.compile(r".*/users$"))
    expect(page).to_have_url(re.compile(r".*/users$"))
    users_tab_loc.wait_for(state="visible")
