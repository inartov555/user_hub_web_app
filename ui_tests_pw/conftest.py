"""
conftest.py
"""

from __future__ import annotations
import os
from configparser import ConfigParser, ExtendedInterpolation
import re

import pytest
from playwright.sync_api import Page, Browser, expect

from config import (
    frontend_url,
    UI_BASE_URL,
    UI_BASE_PORT,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from utils.api_utils import UsersAppApi
from utils.theme import Theme, set_theme
from utils.localization import set_locale
from utils.auth import ensure_regular_user
from utils.file_utils import FileUtils
from utils.app_config import AppConfig
from utils.logger.logger import Logger
from pages.login_page import LoginPage
from pages.users_table_page import UsersTablePage
from pages.excel_import_page import ExcelImportPage
from pages.profile_edit_page import ProfileEditPage
from pages.profile_view_page import ProfileViewPage
from pages.reset_password_page import ResetPasswordPage
from pages.settings_page import SettingsPage
from pages.signup_page import SignupPage
from pages.stats_page import StatsPage


log = Logger(__name__)


def get_api_utils(request) -> UsersAppApi:
    """
    Get API Utils
    """
    _app_config = request.getfixturevalue("app_config")
    base_url = _app_config.base_url
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


@pytest.fixture(autouse=True, scope="session")
def add_loggers():
    """
    The fixture to configure loggers
    It uses built-in pytest arguments to configure loggigng level and files

    Parameters:
        log_level or --log-level general log level for capturing
        log_file_level or --log-file-level  level of log to be stored to a file. Usually lower than general log
        log_file or --log-file  path where logs will be saved
    """
    artifacts_folder_default = os.getenv("HOST_ARTIFACTS")
    log_level = "DEBUG"
    log_file_level = "DEBUG"
    log_file = os.path.join(FileUtils.timestamped_path("pytest", "log", artifacts_folder_default))
    log.setup_cli_handler(level=log_level)
    log.setup_filehandler(level=log_file_level, file_name=log_file)
    log.info(f"General loglevel: '{log_level}', File: '{log_file_level}'")


def validate_app_config_params(**kwargs) -> None:
    """
    Validation of the config parameters
    """
    if not kwargs.get("username"):
        raise ValueError("username parameter is required for tests")
    if not kwargs.get("password"):
        raise ValueError("password parameter is required for tests")


@pytest.fixture(scope="session")
def app_config(pytestconfig) -> AppConfig:
    """
    Set and get AppConfig from ini config
    """
    ini_config_file = pytestconfig.getoption("--ini-config")
    log.info(f"Reading config properties from '{ini_config_file}' and storing to a data class")
    result_dict = {}
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(ini_config_file)
    result_dict["wait_to_handle_capture_manually"] = cfg.getboolean("pytest",
                                                                    "wait_to_handle_capture_manually",
                                                                    fallback=False)
    result_dict["action_timeout"] = cfg.getfloat("pytest", "action_timeout", fallback=15000.0)
    result_dict["navigation_timeout"] = cfg.getfloat("pytest", "navigation_timeout", fallback=15000.0)
    result_dict["assert_timeout"] = cfg.getfloat("pytest", "assert_timeout", fallback=15000.0)
    result_dict["browser"] = cfg.get("pytest", "browser", fallback="chrome")
    result_dict["base_url"] = cfg.get("pytest", "base_url", fallback=UI_BASE_URL)
    result_dict["is_headless"] = cfg.getboolean("pytest", "is_headless", fallback=False)
    result_dict["width"] = cfg.getint("pytest", "width", fallback=1920)
    result_dict["height"] = cfg.getint("pytest", "height", fallback=1080)
    result_dict["username"] = cfg.get("pytest", "username")
    result_dict["password"] = cfg.get("pytest", "password")
    validate_app_config_params(**result_dict)
    result_dict["password"] = result_dict.get("password")
    return AppConfig(**result_dict)


@pytest.fixture(scope="session")
def screenshot_dir() -> str:
    """
    Getting screenshot directory
    """
    artifacts_folder_default = os.getenv("HOST_ARTIFACTS")
    os.makedirs(artifacts_folder_default, exist_ok=True)
    return artifacts_folder_default


def get_browser(playwright, request) -> Browser:
    """
    Set up a browser and return it
    """
    log.info("Getting a browser basing on the config properties")
    _app_config = request.getfixturevalue("app_config")
    if _app_config.browser in ("chromium", "chrome", "msedge"):
        # Chromium Google Chrome, MS Edge
        if _app_config.is_headless:
            args = [f"--window-size={_app_config.width},{_app_config.height}"]
        else:
            args = []
        browser = playwright.chromium.launch(headless=_app_config.is_headless,
                                             args=args)
    elif _app_config.browser in ("firefox"):
        # Firefox
        if _app_config.is_headless:
            args = [f"--window-size={_app_config.width},{_app_config.height}"]
        else:
            args = []
        browser = playwright.firefox.launch(headless=_app_config.is_headless,
                                            args=args)
    elif _app_config.browser in ("webkit", "safari"):
        # WebKit, Safari
        browser = playwright.webkit.launch(headless=_app_config.is_headless)
    else:
        raise ValueError(f"browser config param contains incorrect value: {_app_config.browser}")
    if _app_config.browser in ("webkit", "safari") or not _app_config.is_headless:
        context = browser.new_context(viewport={"width": _app_config.width, "height": _app_config.height})
    else:
        context = browser.new_context(viewport=None)
    page = context.new_page()
    # Setting default timeouts
    context.set_default_navigation_timeout(_app_config.navigation_timeout)
    context.set_default_timeout(_app_config.action_timeout)
    page.set_default_navigation_timeout(_app_config.navigation_timeout)
    page.set_default_timeout(_app_config.action_timeout)
    expect.set_options(timeout=_app_config.assert_timeout)
    request.node.stash["page_obj_fresh"] = page  # it is needed to pass an acutal page to BasePage objects
    log.info(f"{_app_config.browser} browser is selected")
    return browser


@pytest.fixture(autouse=True, name="browser", scope="function")
def browser_setup(playwright, request):
    """
    Set the browser driver
    """
    browser = get_browser(playwright, request)
    yield browser
    browser.close()


def pytest_addoption(parser):
    """
    Supported options
    """
    parser.addoption("--ini-config", action="store", default="pytest.ini", help="The path to the *.ini config file")


@pytest.fixture(name="base_url", scope="session")
def base_url_fixture() -> str:
    """
    Return the base URL of the frontend as configured by environment variables.
    """
    return frontend_url("/").rstrip("/")


# @pytest.fixture(name="ui_theme", params=["light", "dark"], scope="function")
@pytest.fixture(name="ui_theme", params=["light"], scope="function")
def ui_theme_fixture(request: pytest.FixtureRequest) -> Theme:
    """
    Parametrized fixture for light / dark themes.
    """
    return request.param  # type: ignore[return-value]


# @pytest.fixture(name="ui_locale", params=["en-US", "uk-UA"], scope="function")
@pytest.fixture(name="ui_locale", params=["en-US"], scope="function")
def ui_locale_fixture(request: pytest.FixtureRequest) -> str:
    """
    Parametrized fixture for a subset of locales to keep test time reasonable.
    """
    return request.param  # type: ignore[return-value]


@pytest.fixture(name="logged_in_admin", scope="function")
def logged_in_admin_fixture(page: Page, ui_theme: Theme, ui_locale: str) -> Page:
    """
    Return a Playwright page already logged in as the admin user.
    """
    login_page = LoginPage(page)
    login_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    login_page.fill_credentials(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    login_page.submit.click()
    page.wait_for_url(re.compile(r".*/users$"))
    users_tab_loc = page.locator('#users')
    users_tab_loc.wait_for(state="visible")
    return page


@pytest.fixture(name="logged_in_regular", scope="function")
def logged_in_regular_fixture(page: Page, ui_theme: Theme, ui_locale: str) -> Page:
    """
    Return a Playwright page already logged in as the regular test user.
    """
    ensure_regular_user()
    login_page = LoginPage(page)
    login_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    login_page.fill_credentials(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    login_page.submit.click()
    page.wait_for_url(re.compile(r".*/users$"))
    users_tab_loc = page.locator('#users')
    users_tab_loc.wait_for(state="visible")
    return page


@pytest.fixture(scope="function")
def admin_users_page(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> UsersTablePage:
    """
    Get Users table page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    users = UsersTablePage(logged_in_admin)
    users.open()
    return users


@pytest.fixture(scope="function")
def regular_users_page(logged_in_regular: Page, ui_theme: Theme, ui_locale: str) -> UsersTablePage:
    """
    Get Users table page
    """
    set_theme(logged_in_regular, ui_theme)
    set_locale(logged_in_regular, ui_locale)
    users = UsersTablePage(logged_in_regular)
    users.open()
    return users


@pytest.fixture(scope="function")
def admin_excel_import_page(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> ExcelImportPage:
    """
    Get Excel import page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    excel_import = ExcelImportPage(logged_in_admin)
    excel_import.open()
    return excel_import


@pytest.fixture(name="login_page", scope="function")
def login_page_fixture(page: Page, ui_theme: Theme, ui_locale: str) -> LoginPage:
    """
    Get Login page
    """
    login_page = LoginPage(page)
    login_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    return login_page


@pytest.fixture(name="reset_password_page", scope="function")
def reset_password_page_fixture(page: Page,
                                login_page: Page,  # pylint: disable=unused-argument
                                ui_theme: Theme,
                                ui_locale: str) -> ResetPasswordPage:
    """
    Get Reset Password page
    """
    reset_password_page = ResetPasswordPage(page)
    reset_password_page.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    return reset_password_page


@pytest.fixture(name="signup_page", scope="function")
def signup_page_fixture(page: Page,
                                login_page: Page,  # pylint: disable=unused-argument
                                ui_theme: Theme,
                                ui_locale: str) -> SignupPage:
    """
    Get Reset Password page
    """
    signup = SignupPage(page)
    signup.open()
    set_theme(page, ui_theme)
    set_locale(page, ui_locale)
    return signup


@pytest.fixture(name="profile_edit_page_regular", scope="function")
def profile_edit_page_regular_fixture(logged_in_regular: Page, ui_theme: Theme, ui_locale: str) -> ProfileEditPage:
    """
    Get Profile Edit page
    """
    set_theme(logged_in_regular, ui_theme)
    set_locale(logged_in_regular, ui_locale)
    profile_edit = ProfileEditPage(logged_in_regular)
    profile_edit.open()
    return profile_edit


@pytest.fixture(name="profile_edit_page_admin", scope="function")
def profile_edit_page_admin_fixture(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> ProfileEditPage:
    """
    Get Profile Edit page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    profile_edit = ProfileEditPage(logged_in_admin)
    profile_edit.open()
    return profile_edit


@pytest.fixture(name="profile_view_page_regular", scope="function")
def profile_view_page_regular_fixture(logged_in_regular: Page, ui_theme: Theme, ui_locale: str) -> ProfileViewPage:
    """
    Get Profile View page
    """
    set_theme(logged_in_regular, ui_theme)
    set_locale(logged_in_regular, ui_locale)
    profile_view = ProfileViewPage(logged_in_regular)
    profile_view.open()
    return profile_view


@pytest.fixture(name="profile_view_page_admin", scope="function")
def profile_view_page_admin_fixture(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> ProfileViewPage:
    """
    Get Profile View page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    profile_view = ProfileViewPage(logged_in_admin)
    profile_view.open()
    return profile_view


@pytest.fixture(name="settings_page", scope="function")
def settings_page_fixture(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> SettingsPage:
    """
    Get Profile View page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    settings_page = SettingsPage(logged_in_admin)
    settings_page.open()
    return settings_page


@pytest.fixture(name="user_stats_page", scope="function")
def user_stats_page_fixture(logged_in_admin: Page, ui_theme: Theme, ui_locale: str) -> StatsPage:
    """
    Get User Stats page
    """
    set_theme(logged_in_admin, ui_theme)
    set_locale(logged_in_admin, ui_locale)
    user_stats_page = StatsPage(logged_in_admin)
    user_stats_page.open()
    return user_stats_page


@pytest.fixture(scope="function")
def cleanup_delete_users_by_suffix(suffix: str, request) -> None:
    """
    Delete users by passed suffix.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
    """
    yield
    log.info("Cleanup. Deleting users created while running a test")
    api_utils = get_api_utils(request)
    username = f"ui-test-{suffix}"
    email = f"{username}@test.com"
    login_info = api_utils.get_access_token(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    users = api_utils.get_users(access=access_token, search=username)
    user_id_list = []
    for user in users.get("results"):
        resp_email = user.get("email")
        resp_username = user.get("username")
        if username == resp_username and email == resp_email:
            user_id_list.append(user.get("id"))
    if user_id_list:
        api_utils.bulk_user_delete(access_token, user_id_list)


@pytest.fixture(scope="function")
def setup_create_users_by_suffix(suffix: str, request) -> None:
    """
    Delete users by passed suffix.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
    """
    log.info("Setup. Creating users before running a test")
    api_utils = get_api_utils(request)
    username = f"ui-test-{suffix}"
    email = f"{username}@test.com"
    password = "Ch@ngeme123"
    login_info = api_utils.get_access_token(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    api_utils.create_user(access_token, username, email, password)
