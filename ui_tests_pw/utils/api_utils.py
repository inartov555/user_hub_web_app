"""
This file contains API base classes to be derived later
"""

import json
import time
from pprint import pformat

import requests
from requests import Response

from utils.logger.logger import Logger


log = Logger(__name__)


class ApiError(Exception):
    """
    Class for raising API errors
    """
    def __init__(self, error_msg: str):
        """
        Args:
            error_msg (str): error message
        """
        msg = f"Failed to make request: {error_msg}"
        super().__init__(msg)


class ApiBase:
    """
    Method for the derived classes
    """
    BEGIN_REQ = "========== BEGIN =========="
    END_REQ = "========== END =========="

    def __init__(self, protocol: str, host: str, port: str):
        """
        Args:
            protocol (str): http or https
            host (str): e.g. google.com
            port (str): e.g. "443"
        """
        self._unique_request_id_increment = 0
        self.protocol = protocol
        self.host = host
        self.port = port
        self.headers = {"User-Agent": "Test-UsersApp",
                        "Unique-RequestId": str(self._unique_request_id_increment) + "_" + hex(int(time.time()))}

    def append_headers(self, new_headers: dict):
        """
        Args:
            new_headers (dict): new headers to append
        """
        self.headers.update(new_headers)

    def make_request(self,
                     method: str,
                     uri: str,
                     payload: dict = None,
                     multipart: dict = None,
                     query_params: dict = None,
                     headers: dict = None):
        """
        Getting the Response object.
        Log lines are consolidated into single variable to support concurrent requests, if any are added.

        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
            multipart (dict): file data
            query_params (dict): these params will be used in URL
            headers (dict): headers to add to the default ones

        Returns:
            Response
        """
        if not payload:
            payload = {}
        if not query_params:
            query_params = {}
        if not headers:
            headers = {}
        client = requests.session()
        url = f"{self.protocol}://{self.host}:{self.port}{uri}"
        if headers:
            self.headers.update(headers)
        self._unique_request_id_increment += 1
        method = method.upper()
        methods_config = {}
        resp = Response()
        try:
            methods_config = {"GET": {"method": method,
                                      "url": url,
                                      "headers": self.headers,
                                      "params": query_params,
                                      "data": {},
                                      "timeout": 30,
                                      "verify": True,
                                      },
                              "POST": {"method": method,
                                       "url": url,
                                       "headers": self.headers,
                                       "params": query_params,
                                       "data": payload,
                                       "files": multipart,
                                       "timeout": 30,
                                       "verify": True,
                                       },
                              "DELETE": {"method": method,
                                         "url": url,
                                         "headers": self.headers,
                                         "params": query_params,
                                         "data": payload,
                                         "files": multipart,
                                         "timeout": 30,
                                         "verify": True,
                                         },
                              "PUT": {"method": method,
                                      "url": url,
                                      "headers": self.headers,
                                      "params": query_params,
                                      "data": payload,
                                      "files": multipart,
                                      "timeout": 30,
                                      "verify": True,
                                      },
                              }
        except Exception as ex:
            message = f"\n{self.BEGIN_REQ}"
            message += f"\nURL: {url} \nMethod: {method} \nheaders: {pformat(self.headers)} " \
                f"\nparams: {query_params} \npayload: {payload}"
            message += f"\nError: {ex}"
            message += f"\n{self.END_REQ}"
            log.error(message)
            raise ApiError(message) from ex
        if method in methods_config:
            message = f"\n{self.BEGIN_REQ}"
            message += f"\nRequest config: {methods_config[method]}"
            try:
                resp = client.request(**methods_config[method])
                message += f"\nResponse URL: {resp.url}"
                message += f"\nResponse text: {resp.text}"
                message += f"\nResponse headers: {resp.headers}"
                message += f"\nResponse status code: {resp.status_code}"
                message += f"\n{self.END_REQ}"
                log.debug(message)
            except Exception as ex:
                message += f"\nResponse URL: {resp.url}"
                message += f"\nResponse text: {resp.text}"
                message += f"\nResponse headers: {resp.headers}"
                message += f"\nResponse status code: {resp.status_code}"
                message += f"\n{self.END_REQ}"
                log.error(message)
                raise ApiError(message) from ex
            if resp.status_code not in (200, 201, 203, 204):
                raise ApiError(f"HTTP status code is not successful: {resp.status_code}")
            client.close()
        else:
            raise ApiError(f"HTTP method is not implemented: {method}\n")
        return resp


class ApiJsonRequest(ApiBase):
    """
    API methods for the service that returs data in JSON format
    """

    def __init__(self, protocol: str, host: str, port: str):
        """
        Args:
            protocol (str): http or https
            host (str): e.g. google.com
            port (str): e.g. "443"
        """
        super().__init__(protocol, host, port)
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        self.append_headers(headers)

    def make_request(self,
                     method: str,
                     uri: str,
                     payload: dict = None,
                     multipart: dict = None,
                     query_params: dict = None,
                     headers: dict = None,
                     is_return_resp_obj: bool = False,
                     raise_error_if_failed: bool = None):
        """
        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
            multipart (dict): file data
            query_params (dict): these params will be used in URL
            headers (dict): headers to add to the default ones
            raise_error_if_failed (bool): If a test should fail when response validation failed;
                                          TODO: needs to be implemented
            is_return_resp_obj (bool): True - returns the Response object, False - returns JSON;
                                       Note: it's needed for API testing

        Returns:
            json, (list/dict)
        """
        if not payload:
            payload = {}
        else:
            payload = json.dumps(payload)
        if not query_params:
            query_params = {}
        if not headers:
            headers = {}
        if multipart and self.headers.get("Content-Type"):
            self.headers.pop("Content-Type")
        response_obj = super().make_request(method=method,
                                            uri=uri,
                                            payload=payload,
                                            multipart=multipart,
                                            query_params=query_params,
                                            headers=headers)
        if is_return_resp_obj:
            return response_obj
        resp_text = response_obj.text
        response_json = None
        if response_obj.status_code != 204:
            response_json = json.loads(resp_text)
        # Response validation can be added here.
        # Use raise_error_if_failed and raise AssertionError if validation failed and raise_error_if_failed is True
        if raise_error_if_failed:
            pass
        return response_json


class UsersAppApi(ApiJsonRequest):
    """
    API methods
    """

    def get_authorization_token_dict(self, access: str) -> dict:
        """
        Args:
            access (str): access token
            headers (dict): the headers to be used in the request, adding only Athorization
                            header item even when empty
        """
        auth = {"Authorization": f"Bearer {access}"}
        return auth

    def api_login(self, username, password) -> dict:
        """
        POST /api/v1/auth/jwt/create

        Returns:
            dict, e.g. {"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                        "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        """
        payload = {"username": username, "password": password}
        response = self.make_request("post",
                                     "/api/v1/auth/jwt/create",
                                     payload=payload)
        return response

    def logout(self, access: str) -> dict:
        """
        POST /api/v1/auth/jwt/logout/
        """
        response = self.make_request("post",
                                     "/api/v1/auth/jwt/logout/",
                                     headers=self.get_authorization_token_dict(access))
        return response

    def get_users(self,
                  access: str,
                  search: str = "",
                  page_num: int = 1,
                  page_size: int = 1000000,
                  ordering: str = "id"):
        """
        GET /api/v1/users

        Returns:
            dict
        """
        params = {"search": search, "page": page_num, "page_size": page_size, "ordering": ordering}
        response = self.make_request("get",
                                     "/api/v1/users",
                                     query_params=params,
                                     headers=self.get_authorization_token_dict(access))
        return response

    def bulk_user_delete(self, access: str, user_id_list: list) -> dict:
        """
        POST /api/v1/users/bulk-delete/

        Returns:
            dict, {"deleted": $number}
        """
        payload = {"ids": user_id_list}
        response = self.make_request("post",
                                     "/api/v1/users/bulk-delete/",
                                     payload=payload,
                                     headers=self.get_authorization_token_dict(access))
        return response

    def create_user(self, username: str, email: str, password: str) -> dict:
        """
        POST /api/v1/auth/users/

        Returns:
            dict
        """
        payload = {"username": username, "email": email, "password": password}
        response = self.make_request("post",
                                     "/api/v1/auth/users/",
                                     payload=payload)
        return response

    def get_system_settings(self, access: str) -> dict:
        """
        GET /api/v1/system/settings/

        Only Admin user can call it.

        Returns:
            dict, example:
                    { "JWT_RENEW_AT_SECONDS": 9999,
                      "IDLE_TIMEOUT_SECONDS": 9999,
                      "ACCESS_TOKEN_LIFETIME": 9999,
                      "ROTATE_REFRESH_TOKENS": true }
        """
        response = self.make_request("get",
                                     "/api/v1/system/settings/",
                                     payload={},
                                     headers=self.get_authorization_token_dict(access))
        return response

    def update_system_settings(self, access: str, payload: dict) -> dict:
        """
        PUT /api/v1/system/settings/

        Only Admin user can call it.

        Args:
            payload (dict): example:
                                { "JWT_RENEW_AT_SECONDS": 9999,
                                  "IDLE_TIMEOUT_SECONDS": 9999,
                                  "ACCESS_TOKEN_LIFETIME": 9999,
                                  "ROTATE_REFRESH_TOKENS": true }

        Returns:
            dict, example:
                    { "JWT_RENEW_AT_SECONDS": 9999,
                      "IDLE_TIMEOUT_SECONDS": 9999,
                      "ACCESS_TOKEN_LIFETIME": 9999,
                      "ROTATE_REFRESH_TOKENS": true }
        """
        response = self.make_request("put",
                                     "/api/v1/system/settings/",
                                     payload=payload,
                                     headers=self.get_authorization_token_dict(access))
        return response

    def import_excel_spreadsheet(self, access: str, file_name: str) -> dict:
        """
        PUT /api/v1/import-excel/

        Only Admin user can call it.

        Returns:
            dict, example: {created: 0, updated: 0, processed: 0}
        """
        headers=self.get_authorization_token_dict(access)
        with open(file_name, "rb") as _file:
            multipart={
                "file": (
                    file_name,
                    _file.read(),
                    "multipart/form-data; boundary=----WebKitFormBoundary5ilIG8AS3AbGlqdB"
                ),
            }

        response = self.make_request(
            "post",
            "/api/v1/import-excel/",
            headers=headers,
            multipart=multipart
        )
        return response

    def get_profile_details(self, access: str) -> dict:
        """
        PUT /api/v1/auth/users/me/

        Only logged in user can call it.

        Returns:
            dict, example:
                    {
                      "id": 121,
                      "username": "test1",
                      "email": "test1@test.com",
                      "first_name": "string",
                      "last_name": "string",
                      "date_joined": "2026-01-07T09:03:07.050Z",
                      "is_active": true,
                      "is_staff": false,
                      "is_superuser": false
                    }
        """
        response = self.make_request("get",
                                     "/api/v1/auth/users/me/",
                                     headers=self.get_authorization_token_dict(access))
        return response

    def create_user_and_login(self, username: str, email: str, password: str) -> dict:
        """
        1. Create user
        2. Log in as a just created user
        3. Return login info like access token

        Returns:
            dict, e.g. {"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                        "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        """
        self.create_user(username, email, password)
        login_info = self.api_login(username, password)
        return login_info
