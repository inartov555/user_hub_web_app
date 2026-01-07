"""
conftest.py
"""

from __future__ import annotations
import os
from configparser import ConfigParser, ExtendedInterpolation

import pytest
from playwright.sync_api import Page, Browser, expect

from core.constants import LocaleConsts, ThemeConsts
from config import (
    frontend_url,
    UI_BASE_URL,
    UI_BASE_PORT,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from utils.theme import set_theme
from utils.localization import set_locale
from utils.auth import ensure_regular_user, login_via_ui, get_api_utils
from utils.file_utils import FileUtils
from utils.app_config import AppConfig
from utils.logger.logger import Logger
from utils.django_localization import init_django
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


@pytest.fixture(scope="session", autouse=True)
def add_loggers() -> None:
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


@pytest.fixture(scope="session", autouse=True)
def _init_django_for_tests() -> None:
    """
    Initializing Django
    """
    log.info("Initializing Django")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("COPIED_PROJECT_PATH", "")
    init_django()


@pytest.fixture(scope="session", autouse=True)
def before_tests() -> None:
    """
    Actions to be done before running tests.
        1. Creating a regular user
    """
    ensure_regular_user()
    api = get_api_utils()
    login_info = api.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    api.import_excel_sheet(access_token, "test_data/import_template_test_50_users.xlsx")
    # yo['one']


@pytest.fixture(scope="session", autouse=True)
def screenshot_dir() -> str:
    """
    Getting screenshot directory
    """
    artifacts_folder_default = os.getenv("HOST_ARTIFACTS")
    os.makedirs(artifacts_folder_default, exist_ok=True)
    return artifacts_folder_default


@pytest.fixture(name="browser", scope="session", autouse=True)
def browser_setup(playwright, request):
    """
    Set the browser driver
    """
    browser = get_browser(playwright, request)
    yield browser
    browser.close()


def take_a_screenshot(page: Page) -> str:
    """
    Taking a screenshot of the currently shown page

    Returns:
        str, taken screenshot path
    """
    screenshot_path = os.path.join(FileUtils.timestamped_path("screenshot",
                                   "png",
                                   os.getenv("HOST_ARTIFACTS")))
    page.screenshot(path=screenshot_path, full_page=True, timeout=10000)
    return screenshot_path


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
    result_dict["browser"] = cfg.get("pytest", "browser", fallback="chromium")
    result_dict["base_url"] = \
        cfg.get("pytest",
                "base_url",
                fallback="%s:%s" % (UI_BASE_URL, UI_BASE_PORT))  # pylint: disable=consider-using-f-string
    result_dict["is_headless"] = cfg.getboolean("pytest", "is_headless", fallback=False)
    result_dict["width"] = cfg.getint("pytest", "width", fallback=1920)
    result_dict["height"] = cfg.getint("pytest", "height", fallback=1080)
    result_dict["username"] = cfg.get("pytest", "username")
    result_dict["password"] = cfg.get("pytest", "password")
    validate_app_config_params(**result_dict)
    result_dict["password"] = result_dict.get("password")
    return AppConfig(**result_dict)


def get_browser(playwright, request) -> Browser:
    """
    Set up a browser and return it
    """
    log.info("Getting a browser basing on the config properties")
    _app_config = request.getfixturevalue("app_config")
    if _app_config.browser in ("chromium", "chrome", "msedge",):
        # Chromium, Google Chrome, MS Edge
        if _app_config.is_headless:
            args = [f"--window-size={_app_config.width},{_app_config.height}"]
        else:
            args = []
        if _app_config.browser == "chromium":
            browser = playwright.chromium.launch(headless=_app_config.is_headless,
                                                 args=args)
        else:
            browser = playwright.chromium.launch(channel=_app_config.browser,
                                                 headless=_app_config.is_headless,
                                                 args=args)
    elif _app_config.browser == "firefox":
        # Firefox
        if _app_config.is_headless:
            args = [f"--window-size={_app_config.width},{_app_config.height}"]
        else:
            args = []
        browser = playwright.firefox.launch(headless=_app_config.is_headless,
                                            args=args)
    elif _app_config.browser in ("webkit", "safari",):
        # WebKit, Safari
        browser = playwright.webkit.launch(headless=_app_config.is_headless)
    else:
        raise ValueError(f"browser config param contains incorrect value: {_app_config.browser}")
    log.info(f"{_app_config.browser} browser is selected")
    return browser


@pytest.fixture(name="page", scope="function")
def page_fixture(browser: Browser, request) -> Page:
    """
    Page fixture
    """
    _app_config = request.getfixturevalue("app_config")
    if _app_config.browser in ("webkit", "safari",) or not _app_config.is_headless:
        context = browser.new_context(viewport={"width": _app_config.width, "height": _app_config.height})
    else:
        context = browser.new_context(viewport=None)
    page_context = context.new_page()
    # Setting default timeouts
    context.set_default_navigation_timeout(_app_config.navigation_timeout)
    context.set_default_timeout(_app_config.action_timeout)
    page_context.set_default_navigation_timeout(_app_config.navigation_timeout)
    page_context.set_default_timeout(_app_config.action_timeout)
    expect.set_options(timeout=_app_config.assert_timeout)
    request.node.stash["page_obj_fresh"] = page_context  # it is needed to pass an acutal page to BasePage objects

    yield page_context
    context.close()


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


@pytest.fixture(name="logged_in_admin", scope="function")
def logged_in_admin_fixture(page: Page) -> Page:
    """
    Return a Playwright page already logged in as the admin user.
    """
    login_page = LoginPage(page)
    login_page.open()
    login_page.accept_cookie_consent_if_present()
    login_via_ui(page,
                 DEFAULT_ADMIN_USERNAME,
                 DEFAULT_ADMIN_PASSWORD,
                 ThemeConsts.LIGHT,
                 LocaleConsts.ENGLISH_US)
    return page


@pytest.fixture(name="logged_in_regular", scope="function")
def logged_in_regular_fixture(page: Page) -> Page:
    """
    Return a Playwright page already logged in as the regular test user.
    """
    ensure_regular_user()
    login_page = LoginPage(page)
    login_page.open()
    login_page.accept_cookie_consent_if_present()
    login_via_ui(page,
                 DEFAULT_REGULAR_USERNAME,
                 DEFAULT_REGULAR_PASSWORD,
                 ThemeConsts.LIGHT,
                 LocaleConsts.ENGLISH_US)
    return page


@pytest.fixture(scope="function")
def admin_users_page(logged_in_admin: Page) -> UsersTablePage:
    """
    Get Users table page
    """
    users = UsersTablePage(logged_in_admin)
    users.open()
    return users


@pytest.fixture(scope="function")
def regular_users_page(logged_in_regular: Page) -> UsersTablePage:
    """
    Get Users table page
    """
    users = UsersTablePage(logged_in_regular)
    users.open()
    return users


@pytest.fixture(scope="function")
def admin_excel_import_page(logged_in_admin: Page) -> ExcelImportPage:
    """
    Get Excel import page
    """
    excel_import = ExcelImportPage(logged_in_admin)
    excel_import.open()
    return excel_import


@pytest.fixture(name="login_page", scope="function")
def login_page_fixture(page: Page) -> LoginPage:
    """
    Get Login page
    """
    login_page = LoginPage(page)
    login_page.open()
    login_page.accept_cookie_consent_if_present()
    return login_page


@pytest.fixture(name="reset_password_page", scope="function")
def reset_password_page_fixture(page: Page,
                                login_page: LoginPage,  # pylint: disable=unused-argument
                               ) -> ResetPasswordPage:
    """
    Get Reset Password page
    """
    reset_password_page = ResetPasswordPage(page)
    reset_password_page.open()
    return reset_password_page


@pytest.fixture(name="signup_page", scope="function")
def signup_page_fixture(page: Page,
                        login_page: Page,  # pylint: disable=unused-argument
                       ) -> SignupPage:
    """
    Get Reset Password page
    """
    signup = SignupPage(page)
    signup.open()
    return signup


@pytest.fixture(name="profile_edit_page_regular", scope="function")
def profile_edit_page_regular_fixture(logged_in_regular: Page) -> ProfileEditPage:
    """
    Get Profile Edit page
    """
    profile_edit = ProfileEditPage(logged_in_regular)
    profile_edit.open()
    return profile_edit


@pytest.fixture(name="profile_edit_page_admin", scope="function")
def profile_edit_page_admin_fixture(logged_in_admin: Page) -> ProfileEditPage:
    """
    Get Profile Edit page
    """
    profile_edit = ProfileEditPage(logged_in_admin)
    profile_edit.open()
    return profile_edit


@pytest.fixture(name="profile_view_page_regular", scope="function")
def profile_view_page_regular_fixture(logged_in_regular: Page) -> ProfileViewPage:
    """
    Get Profile View page
    """
    profile_view = ProfileViewPage(logged_in_regular)
    profile_view.open()
    return profile_view


@pytest.fixture(name="profile_view_page_admin", scope="function")
def profile_view_page_admin_fixture(logged_in_admin: Page) -> ProfileViewPage:
    """
    Get Profile View page
    """
    profile_view = ProfileViewPage(logged_in_admin)
    profile_view.open()
    return profile_view


@pytest.fixture(name="settings_page", scope="function")
def settings_page_fixture(logged_in_admin: Page) -> SettingsPage:
    """
    Get Profile View page
    """
    settings_page = SettingsPage(logged_in_admin)
    settings_page.open()
    return settings_page


@pytest.fixture(name="user_stats_page", scope="function")
def user_stats_page_fixture(logged_in_admin: Page) -> StatsPage:
    """
    Get User Stats page
    """
    user_stats_page = StatsPage(logged_in_admin)
    user_stats_page.open()
    return user_stats_page


def delete_users_by_suffix_via_api(suffix: str,
                                   compare: str = "contains",
                                   mode: str = "username") -> None:
    """
    Delete users by passed suffix, if found.

    Args:
        suffix (str): part of the username/email/first name/last name depending on compare
        compare (str): one of (strict, contains)
        mode (str): one of (username, email, first_name, last_name)
    """
    _suffix_lower = suffix.lower()
    _compare_lower = compare.lower()
    _mode_lower = mode.lower()
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    users = api_utils.get_users(access=access_token, search=_suffix_lower)

    def _compare(_suffix: str, _value_to_compare: str, _compare: str) -> bool:
        """
        Returns:
            bool, if the match happened
        """
        value_lower = _value_to_compare.lower() if _value_to_compare else ""
        if _compare == "strict" and _suffix == value_lower or \
           _compare == "contains" and _suffix in value_lower:
            return True
        return False

    user_id_list = []
    for user in users.get("results"):
        value_to_pass = ""
        if _mode_lower == "email":
            value_to_pass = user.get("email")
        elif _mode_lower == "username":
            value_to_pass = user.get("username")
        elif _mode_lower == "firstname":
            value_to_pass = user.get("firstName")
        elif _mode_lower == "lastname":
            value_to_pass = user.get("lastName")
        compare_result = _compare(_suffix_lower, value_to_pass, _compare_lower)
        if compare_result:
            user_id_list.append(user.get("id"))
    if user_id_list:
        api_utils.bulk_user_delete(access_token, user_id_list)


@pytest.fixture(scope="function")
def cleanup_delete_users_by_suffix(suffix: str) -> None:
    """
    Delete users by passed suffix, if found.

    Username & email are created with this logic:
        username_start = f"ui-test-{suffix}"
        email_end = f"@test.com"
    """
    yield

    log.info("Cleanup. Deleting users created while running a test")
    delete_users_by_suffix_via_api(suffix, "contains", "username")


@pytest.fixture(scope="function")
def cleanup_set_default_theme_and_locale(page: Page) -> None:
    """
    Cleanup. Default theme is ThemeConsts.LIGHT and default locale is LocaleConsts.ENGLISH_US.
    """
    yield

    log.info("Cleanup. Defaulting to light theme and en-US locale")
    set_theme(page, ThemeConsts.LIGHT)
    set_locale(page, LocaleConsts.ENGLISH_US)


@pytest.fixture(scope="function")
def setup_create_users_by_suffix(suffix: str) -> None:
    """
    Delete users by passed suffix.

    Username & email are created with this logic:
        username = f"ui-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    log.info("Setup. Creating users before running a test")
    api_utils = get_api_utils()
    username = f"ui-test-{suffix}"
    email = f"{username}@test.com"
    password = "Ch@ngeme123"
    api_utils.create_user(username, email, password)


@pytest.fixture(scope="function")
def setup_cleanup_update_app_settings() -> None:
    """
    1. Get current App Settings and keep them in memory
    2. Set short time settings for a test
    3. Once cleanup part started, get preserved old App Settings and set them
    """
    log.info("Setup. Set App Settings for a test")
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    old_settings = api_utils.get_system_settings(access_token)

    yield

    log.info("Cleanup. Returning old App Settings' values")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    api_utils.update_system_settings(access_token, old_settings)
