"""
conftest.py
"""

import os
import httpx
from configparser import ConfigParser, ExtendedInterpolation

import pytest

from core.app_config import AppConfig


DEFAULT_BASE_URL = "http://localhost:8000"


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
    return AppConfig(**result_dict)


@pytest.fixture(name="base_url", scope="session")
def base_url_fixture() -> str:
    """
    Get base URL
    """
    return os.getenv("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(name="client", scope="session")
def client_fixture(base_url: str):
    """
    Get client
    """
    with httpx.Client(base_url=base_url, timeout=30.0, follow_redirects=True) as _client:
        yield _client
