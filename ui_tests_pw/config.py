"""
Global configuration for the UI automation framework.

This module centralizes configuration values so that tests and page objects
can rely on a single source of truth for URLs, credentials and timeouts.
"""

from __future__ import annotations

import os
from typing import Final


# UI_BASE_URL: Final[str] = os.environ.get("UI_BASE_URL", "http://localhost")
# UI_BASE_PORT: Final[int] = int(os.environ.get("UI_BASE_PORT", "5173"))
BACKEND_API_BASE: Final[str] = os.environ.get("BACKEND_API_BASE", "http://localhost:8000/api/v1")

DEFAULT_ADMIN_USERNAME: Final[str] = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD: Final[str] = os.environ.get("ADMIN_PASSWORD", "changeme123")

DEFAULT_REGULAR_USERNAME: Final[str] = os.environ.get("REGULAR_USERNAME", "test1")
DEFAULT_REGULAR_PASSWORD: Final[str] = os.environ.get("REGULAR_PASSWORD", "changeme123")


def frontend_url(path: str = "/") -> str:
    """
    Build a full frontend URL for the given path.

    Args:
        path: Relative path, e.g. "/login" or "users".

    Returns:
        Fully-qualified URL combining UI_BASE_URL, UI_BASE_PORT and the path.
    """
    trimmed = path if path.startswith("/") else f"/{path}"
    return f"{UI_BASE_URL}:{UI_BASE_PORT}{trimmed}"
