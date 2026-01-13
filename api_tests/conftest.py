"""
conftest.py
"""

import os
from configparser import ConfigParser, ExtendedInterpolation

import pytest

from core.app_config import AppConfig
from utils.logger.logger import Logger


log = Logger(__name__)
DEFAULT_BASE_URL = "http://host.docker.internal:5173"


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
    return AppConfig(**result_dict)


@pytest.fixture(name="base_url", scope="session")
def base_url_fixture() -> str:
    """
    Get base URL
    """
    return os.getenv("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
