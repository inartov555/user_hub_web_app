"""
Tests related to api
"""

from __future__ import annotations
import random

import pytest

from conftest import (
    get_api_utils,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_REGULAR_USERNAME,
    DEFAULT_REGULAR_PASSWORD,
)
from api.api import ApiError


def test_api_login():
    """
    Test POST 200 /api/v1/auth/jwt/create
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    if not login_info.get("access"):
        raise AssertionError("POST /api/v1/auth/jwt/create request did not return access token")


def test_refresh_token():
    """
    Test POST 200 /api/v1/auth/jwt/refresh/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    refresh = api_utils.refresh_token(login_info.get("refresh"))
    if not refresh.get("access"):
        raise AssertionError("POST /api/v1/auth/jwt/refresh/ request did not return access token")


def test_token_verify():
    """
    Test POST 200 /api/v1/auth/jwt/verify/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    verify = api_utils.verify_token(login_info.get("access"))
    if verify:
        raise AssertionError("POST 200 /api/v1/auth/jwt/verify/ should return {}, but now it returned some value")


@pytest.mark.parametrize("username, password",
                         [(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD),
                          (DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)])
def test_access_token_invalidated_after_logging_out_admin(username: str, password: str) -> None:
    """
    Test POST 200 /api/v1/auth/jwt/logout/

    1. Login via API as an admin
    2. Preserve the access token
    3. Do some actions to simulate real website activity, e.g. call /api/v1/auth/users/me/
    4. Log out /api/v1/auth/jwt/logout/
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
    except ApiError:
        did_invalidated_token_work = False
    if did_invalidated_token_work:
        raise AssertionError("/api/v1/auth/jwt/logout/ did not invalidate the access token")


def test_get_users():
    """
    Test GET 200 /api/v1/users
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    users = api_utils.get_users(login_info.get("access"), "admin", 1, 10, "id")
    if not users:
        raise AssertionError("GET 200 /api/v1/users did not return user list")


@pytest.mark.parametrize("suffix", ["testusername"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_create_user(suffix: str):
    """
    Test POST 201 /api/v1/auth/users/
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    users = api_utils.get_users(login_info.get("access"), suffix, 1, 10, "id")
    if not users.get("results"):
        raise AssertionError("POST 201 /api/v1/auth/users/ did not create a user")


@pytest.mark.parametrize("suffix", ["testusername"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_bulk_delete_regular_user(suffix: str):
    """
    Test POST 200 /api/v1/users/bulk-delete/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.bulk_user_delete(login_info.get("access"), [int(created_user.get("id"))])
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/users/bulk-delete/ was successfully called for a regular user")


@pytest.mark.parametrize("suffix", ["testusername"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_bulk_delete_admin(suffix: str):
    """
    Test POST 200 /api/v1/users/bulk-delete/
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    deleted_users = api_utils.bulk_user_delete(login_info.get("access"), [int(created_user.get("id"))])
    if not deleted_users.get("deleted"):
        raise AssertionError("POST 200 /api/v1/users/bulk-delete/ did not return deleted user count")
    users = api_utils.get_users(login_info.get("access"), suffix, 1, 10, "id")
    if users.get("results"):
        raise AssertionError("POST 200 /api/v1/users/bulk-delete/ did not delete user(s)")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_single_user_delete_regular_user(suffix: str):
    """
    Test DELETE 200 /users/${id}/delete-user/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.single_user_delete(login_info.get("access"), int(created_user.get("id")))
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("DELETE 204 /users/${id}/delete-user/ was successfully called for a regular user")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_single_user_delete_admin(suffix: str):
    """
    Test DELETE 204 /users/${id}/delete-user/
    """
    api_utils = get_api_utils()
    created_user = api_utils.create_user(suffix, f"{suffix}@{suffix}.com", "Ch@ngeme123")
    if not created_user:
        raise AssertionError("POST 201 /api/v1/auth/users/ did not return value")
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    api_utils.single_user_delete(login_info.get("access"), int(created_user.get("id")))
    users = api_utils.get_users(login_info.get("access"), suffix, 1, 10, "id")
    if users.get("results"):
        raise AssertionError("DELETE 204 /users/${id}/delete-user/ did not delete the user")


def test_get_system_settings_regular_user():
    """
    GET 200 /api/v1/system/settings/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.get_system_settings(login_info.get("access"))
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/system/settings/ was successfully called for a regular user")


def test_get_system_settings_admin():
    """
    GET 200 /api/v1/system/settings/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    get_system_settings = api_utils.get_system_settings(login_info.get("access"))
    if not get_system_settings:
        raise AssertionError("GET 200 /api/v1/system/settings/ did not return system settings")


@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_update_system_settings_regular_user():
    """
    PUT 200 /api/v1/system/settings/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    new_settings = { "JWT_RENEW_AT_SECONDS": 9999, "IDLE_TIMEOUT_SECONDS": 9999,
                     "ACCESS_TOKEN_LIFETIME": 9999, "ROTATE_REFRESH_TOKENS": True }
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.update_system_settings(login_info.get("access"), new_settings)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("PUT 200 /api/v1/system/settings/ was successfully called for a regular user")


@pytest.mark.usefixtures("setup_cleanup_update_app_settings")
def test_update_system_settings_admin():
    """
    PUT 200 /api/v1/system/settings/
    """
    new_settings = { "JWT_RENEW_AT_SECONDS": 9999, "IDLE_TIMEOUT_SECONDS": 9999,
                     "ACCESS_TOKEN_LIFETIME": 9999, "ROTATE_REFRESH_TOKENS": True }
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    update_system_settings = api_utils.update_system_settings(login_info.get("access"), new_settings)
    get_system_settings = api_utils.get_system_settings(login_info.get("access"))
    if not update_system_settings:
        raise AssertionError("PUT 200 /api/v1/system/settings/ did not return system settings")
    for key in update_system_settings:
        if get_system_settings[key] != update_system_settings[key]:
            raise AssertionError("PUT 200 /api/v1/system/settings/ did not update the settings; "
                                 f"get_system_settings {get_system_settings}; "
                                 f"update_system_settings {update_system_settings}")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_import_excel_spreadsheet_regular_user():
    """
    POST 200 /api/v1/import-excel/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.import_excel_spreadsheet(login_info.get("access"),
                                           "test_data/excel_import/import_template_test_20_users.xlsx")
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/import-excel/ was successfully called for a regular user")


@pytest.mark.parametrize("suffix", ["watermelon"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_import_excel_spreadsheet_admin():
    """
    POST 200 /api/v1/import-excel/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    import_excel = api_utils.import_excel_spreadsheet(login_info.get("access"),
                                                      "test_data/excel_import/import_template_test_20_users.xlsx")
    if not import_excel:
        raise AssertionError("POST 200 /api/v1/import-excel/ did not return import results")


def test_get_excel_spreadsheet_regular_user():
    """
    GET 200 /api/v1/import-excel/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.get_excel_spreadsheet(login_info.get("access"))
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/import-excel/ was successfully called for a regular user")


def test_get_excel_spreadsheet_admin():
    """
    GET 200 /api/v1/import-excel/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    import_excel = api_utils.get_excel_spreadsheet(login_info.get("access"))
    if not str(import_excel):
        raise AssertionError("GET 200 /api/v1/import-excel/ did not return Excel import template file")


@pytest.mark.parametrize("username, password",
                         [(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD),
                          (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)])
def test_get_currently_logged_in_user_details(username: str,
                                              password: str):
    """
    GET 200 /api/v1/auth/users/me/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(username, password)
    logged_in_user_details = api_utils.get_currently_logged_in_user_details(login_info.get("access"))
    if not logged_in_user_details:
        raise AssertionError("GET 200 /api/v1/auth/users/me/ did not return user details of the currently logged in user")


@pytest.mark.parametrize("username, password",
                         [(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD),
                          (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)])
def test_get_profile_details(username: str,
                             password: str):
    """
    GET 200 /api/v1/me/profile/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(username, password)
    logged_in_user_profile_details = api_utils.get_profile_details(login_info.get("access"))
    if not logged_in_user_profile_details:
        raise AssertionError("GET 200 /api/v1/me/profile/ did not return profile details of the currently logged in user")


@pytest.mark.parametrize("username, password",
                         [(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD),
                          (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)])
def test_edit_profile_details(username: str,
                              password: str):
    """
    PUT 200 /api/v1/me/profile/
    """
    rand_num = random.randint(0, 1000)
    edit_data = {"first_name": f"API_{rand_num}",
                 "last_name": f"Tester_{rand_num}",
                 "bio": f"Bio from automated test._{rand_num}"}
    api_utils = get_api_utils()
    login_info = api_utils.api_login(username, password)
    api_utils.edit_profile_details(login_info.get("access"),
                                   username=None,
                                   email=None,
                                   first_name=edit_data.get("first_name"),
                                   last_name=edit_data.get("last_name"),
                                   bio=edit_data.get("bio"))
    logged_in_user_profile_details = api_utils.get_profile_details(login_info.get("access"))
    if logged_in_user_profile_details["user"].get("first_name") != edit_data.get("first_name") or \
       logged_in_user_profile_details["user"].get("last_name") != edit_data.get("last_name") or \
       logged_in_user_profile_details.get("bio") != edit_data.get("bio"):
        raise AssertionError("PUT 200 /api/v1/me/profile/ did not update profile of the currently logged in user")


def test_get_online_user_stats_regular_user():
    """
    GET 200 /api/v1/stats/online-users/
    The operation is not allowed for a regular user, so the request is expected to fail
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.get_online_user_stats(login_info.get("access"))
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("GET 200 /api/v1/stats/online-users/ was successfully called for a regular user")


def test_get_online_user_stats_admin():
    """
    GET 200 /api/v1/stats/online-users/
    """
    api_utils = get_api_utils()
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    online_user_stats = api_utils.get_online_user_stats(login_info.get("access"))
    if not online_user_stats:
        raise AssertionError("GET 200 /api/v1/stats/online-users/ did not return online user stats")


@pytest.mark.parametrize("suffix", ["vesimeloni"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_set_password_to_self_regular_user(suffix: str):
    """
    POST 200 /api/v1/users/{user_id}/set-password/
    """
    username = f"api-{suffix}"
    email = f"{username}@{suffix}.com"
    password_old = "In1ti@lP@3$w0rd"
    password_new = "changeme123"
    api_utils = get_api_utils()
    login_info = api_utils.create_user_and_login(username, email, password_old)
    api_utils.set_password(login_info.get("access"), str(login_info.get("id")), password_new, password_new)
    login_info = api_utils.api_login(username, password_new)
    if not login_info.get("access"):
        raise AssertionError("POST 200 /api/v1/users/{user_id}/set-password/ did not change password")


@pytest.mark.parametrize("suffix", ["vesimeloni"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_set_password_to_other_user_regular_user(request, suffix: str):
    """
    POST 200 /api/v1/users/{user_id}/set-password/
    Regular user can change password for themselves only.
    """
    created_user = request.getfixturevalue("setup_create_users_by_suffix")
    password_old = "Ch@ngeme123"
    password_new = "New@lP@3$w0rd"
    api_utils = get_api_utils()
    login_info = api_utils.api_login(created_user.get("username"), password_old)
    if not login_info.get("access"):
        raise AssertionError("Access token was not returned after logging in previously created user")
    api_utils.logout(login_info.get("access"))
    login_info = api_utils.api_login(DEFAULT_REGULAR_USERNAME, DEFAULT_REGULAR_PASSWORD)
    was_failed = False
    try:
        api_utils.set_password(login_info.get("access"), created_user.get("id"), password_new, password_new)
    except ApiError:
        was_failed = True
    if not was_failed:
        raise AssertionError("POST 200 /api/v1/users/{user_id}/set-password/ was successful "
                             "when retular user changed password of another user")


@pytest.mark.parametrize("suffix", ["vesimeloni"])
@pytest.mark.usefixtures("cleanup_delete_users_by_suffix")
def test_set_password_to_self_admin(request, suffix: str):
    """
    POST 200 /api/v1/users/{user_id}/set-password/
    Admin user can change password as to themselves as to other users.
    """
    created_user = request.getfixturevalue("setup_create_users_by_suffix")
    username = f"api-{suffix}"
    email = f"{username}@{suffix}.com"
    password_old = "Ch@ngeme123"
    password_new = "New@lP@3$w0rd"
    api_utils = get_api_utils()
    # login_info = api_utils.create_user_and_login(username, email, password_old)
    login_info = api_utils.api_login(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    api_utils.update_user(login_info.get("access"),
                          user_id=created_user.get("id"),
                          username=created_user.get("username"),
                          email=created_user.get("email"),
                          first_name=created_user.get("username"),
                          last_name=created_user.get("username"),
                          is_active=True,
                          is_staff=True,
                          is_superuser=True)
    api_utils.logout(login_info.get("access"))
    login_info = api_utils.api_login(created_user.get("username"), password_old)
    api_utils.set_password(login_info.get("access"),created_user.get("id"),  password_new, password_new)
    api_utils.logout(login_info.get("access"))
    login_info = api_utils.api_login(created_user.get("username"), password_new)
    if not login_info.get("access"):
        raise AssertionError("POST 200 /api/v1/users/{user_id}/set-password/ did not change password")
