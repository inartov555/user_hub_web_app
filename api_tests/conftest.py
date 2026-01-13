"""
conftest.py
"""

import os
from configparser import ConfigParser, ExtendedInterpolation

import pytest

from api.api import UsersAppApi
from core.app_config import AppConfig
from utils.logger.logger import Logger


log = Logger(__name__)
DEFAULT_BASE_URL = "http://host.docker.internal:5173"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "changeme123"
DEFAULT_REGULAR_USERNAME = "test1"
DEFAULT_REGULAR_PASSWORD = "changeme123"


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
    result_dict["admin_user_login"] = cfg.get("pytest", "admin_user_login", fallback=DEFAULT_ADMIN_USERNAME)
    result_dict["admin_user_password"] = cfg.get("pytest", "admin_user_password", fallback=DEFAULT_ADMIN_PASSWORD)
    result_dict["regular_user_login"] = cfg.get("pytest", "regular_user_login", fallback=DEFAULT_REGULAR_USERNAME)
    result_dict["regular_user_password"] = cfg.get("pytest", "regular_user_password", fallback=DEFAULT_REGULAR_PASSWORD)
    return AppConfig(**result_dict)


@pytest.fixture(scope="session", autouse=True)
def before_tests(app_config: AppConfig) -> None:
    """
    Actions to be done before running tests.
        1. Creating a regular user
    """
    api_utils = get_api_utils()
    api_utils.create_user(username, email, password)


@pytest.fixture(name="base_url", scope="session")
def base_url_fixture() -> str:
    """
    Get base URL
    """
    return os.getenv("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
