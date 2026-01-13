"""
conftest.py
"""

import os
import httpx

import pytest


DEFAULT_BASE_URL = "http://localhost:8000"


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
