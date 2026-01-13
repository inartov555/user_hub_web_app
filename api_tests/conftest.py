import os
import httpx

import pytest


DEFAULT_BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def client(base_url: str):
    with httpx.Client(base_url=base_url, timeout=30.0, follow_redirects=True) as _client:
        yield _client
