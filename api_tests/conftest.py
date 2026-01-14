"""
conftest.py
"""

import os
from configparser import ConfigParser, ExtendedInterpolation

import pytest

from api.api import UsersAppApi, ApiError
from core.app_config import AppConfig
from utils.logger.logger import Logger
from utils.file_utils import FileUtils


log = Logger(__name__)
DEFAULT_BASE_URL = "http://host.docker.internal"
DEFAULT_BASE_PORT = "5173"
DEFAULT_API_URI = "/api/v1/"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "changeme123"
DEFAULT_REGULAR_USERNAME = "test1"
DEFAULT_REGULAR_EMAIL = "test1@test.com"
DEFAULT_REGULAR_PASSWORD = "changeme123"


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
    result_dict["base_url"] = cfg.get("pytest", "base_url", fallback=DEFAULT_BASE_URL)
    result_dict["base_port"] = cfg.get("pytest", "base_port", fallback=DEFAULT_BASE_PORT)
    result_dict["base_api_uri"] = cfg.get("pytest", "base_api_uri", fallback=DEFAULT_API_URI)
    return AppConfig(**result_dict)


def get_api_utils() -> UsersAppApi:
    """
    Get API Utils
    """
    base_url = DEFAULT_BASE_URL
    ind_protocol = base_url.find("://")
    protocol = "http"
    host = base_url
    port = DEFAULT_BASE_PORT
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


@pytest.fixture(scope="session", autouse=True)
def before_tests() -> None:
    """
    Actions to be done before running tests.
        1. Creating a regular user
    """
    api_utils = get_api_utils()
    try:
        api_utils.create_user(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_EMAIL, DEFAULT_REGULAR_PASSWORD)
    except ApiError as ex:
        # Usually, it means that user exists
        log.warning(f"before_tests fixture failed with: {ex}")


@pytest.fixture(name="base_url", scope="session")
def base_url_fixture(request) -> str:
    """
    Get base API URL
    """
    _app_config = request.getfixturevalue("app_config")
    return f"{_app_config.base_url}:{_app_config.base_port}{_app_config.base_api_uri}"


def pytest_addoption(parser) -> None:
    """
    Supported options
    """
    parser.addoption("--ini-config", action="store", default="pytest.ini", help="The path to the *.ini config file")


def delete_users_by_suffix_via_api(suffix: str) -> None:
    """
    Delete users by passed suffix, if found.

    Args:
        suffix (str): part/full value of the username/email/first_name/last_name
    """
    api_utils = get_api_utils()
    user_id_list = []
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    access_token = login_info.get("access")
    users = api_utils.get_users(access=access_token, search=suffix)
    if users and users.get("results"):
        for _user in users.get("results"):
            user_id_list.append(int(_user.get("id")))
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
    delete_users_by_suffix_via_api(suffix)


@pytest.fixture(scope="function")
def setup_create_users_by_suffix(suffix: str) -> None:
    """
    Delete users by passed suffix.

    Username & email are created with this logic:
        username = f"api-test-{suffix}"
        email = f"{username}@test.com"
        password = "Ch@ngeme123"
    """
    log.info("Setup. Creating users before running a test")
    api_utils = get_api_utils()
    username = f"api-test-{suffix}"
    email = f"{username}@test.com"
    password = "Ch@ngeme123"
    created_user = api_utils.create_user(username, email, password)
    yield created_user


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
