"""
Tests for the logout
"""

from __future__ import annotations

import pytest

from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from utils.auth import get_api_utils


@pytest.mark.admin
@pytest.mark.regular_user
@pytest.mark.parametrize("username, password",
                         [(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD),
                          (DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)])
def test_access_token_invalidated_after_logging_out_admin(username: str, password: str) -> None:
    """
    1. Login via API as an admin
    2. Preserve the access token
    3. Do some actions to simulate real website activity, e.g. call /api/v1/auth/users/me/
    4. Logout
    5. Try to call some requests that require access token with value from step #2
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(username, password)
    access_token = login_info.get("access")
    api_utils.get_profile_details(access=access_token)
    # Now, let's logout
    api_utils.logout(access_token)
    did_invalidated_token_work = True
    # Verify that now request that requires access token fails when calling it with invalidated access token
    try:
        api_utils.get_profile_details(access=access_token)
    except Exception:  # pylint: disable=broad-exception-caught
        did_invalidated_token_work = False
    if did_invalidated_token_work:
        raise AssertionError("/api/v1/auth/jwt/logout did not invalidate the access token")
