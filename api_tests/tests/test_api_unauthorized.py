"""
Tests related to API.
Check requests without authentication token.
"""

from __future__ import annotations
import random

import pytest

from conftest import (
    get_api_utils,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
)
from api.api import ApiError


def test_logout_unauthorized() -> None:
    """
    Test POST 200 /api/v1/auth/jwt/logout/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    api_utils.get_profile_details(login_info.get("access"))
    # Verify that request passes without access token
    api_utils.logout(login_info.get("access"), use_authentication_header=False)


def test_get_users_unauthorized():
    """
    Test GET 200 /api/v1/users
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_users(login_info.get("access"), "admin", 1, 10, "id", use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/users did not fail without access token")


@pytest.mark.parametrize("suffix", ["testusername"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_bulk_delete_unauthorized(suffix: str):
    """
    Test POST 200 /api/v1/users/bulk-delete/
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.bulk_user_delete(login_info.get("access"),
                                   [int(created_user.get("id"))],
                                   use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/users/bulk-delete/ did not fail without access token")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_single_user_delete_unauthorized(suffix: str):
    """
    Test DELETE 200 /users/${id}/delete-user/
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.single_user_delete(login_info.get("access"),
                                     int(created_user.get("id")),
                                     use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("DELETE 204 /users/${id}/delete-user/ did not fail without access token")


def test_get_system_settings_unauthorized():
    """
    GET 200 /api/v1/system/settings/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_system_settings(login_info.get("access"), use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/system/settings/ did not fail without access token")


@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_update_system_settings_unauthorized():
    """
    PUT 200 /api/v1/system/settings/
    """
    new_settings = { "JWT_RENEW_AT_SECONDS": 9999, "IDLE_TIMEOUT_SECONDS": 9999,
                     "ACCESS_TOKEN_LIFETIME": 9999, "ROTATE_REFRESH_TOKENS": True }
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.update_system_settings(login_info.get("access"),
                                         new_settings,
                                         use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("PUT 200 /api/v1/system/settings/ did not fail without access token")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_import_excel_spreadsheet_unauthorized():
    """
    POST 200 /api/v1/import-excel/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.import_excel_spreadsheet(login_info.get("access"),
                                           "test_data/excel_import/import_template_test_20_users.xlsx",
                                           use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/import-excel/ did not fail without access token")


def test_get_excel_spreadsheet_unauthorized():
    """
    GET 200 /api/v1/import-excel/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_excel_spreadsheet(login_info.get("access"), use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/import-excel/ did not fail without access token")


def test_get_currently_logged_in_user_details_unauthorized():
    """
    GET 200 /api/v1/auth/users/me/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_currently_logged_in_user_details(login_info.get("access"),
                                                       use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/auth/users/me/ did not fail without access token")


def test_get_profile_details_unauthorized():
    """
    GET 200 /api/v1/me/profile/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_profile_details(login_info.get("access"), use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/me/profile/ did not fail without access token")


def test_edit_profile_details_unauthorized():
    """
    PUT 200 /api/v1/me/profile/
    """
    rand_num = random.randint(0, 1000)
    edit_data = {"first_name": f"API_{rand_num}",
                 "last_name": f"Tester_{rand_num}",
                 "bio": f"Bio from automated test._{rand_num}"}
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.edit_profile_details(login_info.get("access"),
                                       username=None,
                                       email=None,
                                       first_name=edit_data.get("first_name"),
                                       last_name=edit_data.get("last_name"),
                                       bio=edit_data.get("bio"),
                                       use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("PUT 200 /api/v1/me/profile/ did not fail without access token")


def test_get_online_user_stats_unauthorized():
    """
    GET 200 /api/v1/stats/online-users/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.get_online_user_stats(login_info.get("access"), use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/stats/online-users/ did not fail without access token")


def test_set_password_unauthorized():
    """
    POST 200 /api/v1/users/{user_id}/set-password/
    """
    password_new = "changeme123"
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.set_password(login_info.get("access"),
                               "1",
                               password_new,
                               password_new,
                               use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/users/{user_id}/set-password/ did not fail without access token")


@pytest.mark.parametrize("suffix", ["vesimeloni"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_update_user_unauthorized(request):
    """
    PUT 200 /api/v1/auth/users/${id}/
    """
    created_user = request.getfixturevalue("setup_create_users_by_suffix")
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    # Verify that request fails without access token
    was_failed = False
    try:
        api_utils.update_user(login_info.get("access"),
                              user_id=created_user.get("id"),
                              username=created_user.get("username"),
                              email=created_user.get("email"),
                              first_name=created_user.get("username"),
                              last_name=created_user.get("username"),
                              is_active=True,
                              is_staff=True,
                              is_superuser=True,
                              use_authentication_header=False)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("PUT 200 /api/v1/auth/users/${id}/ did not fail without access token")
