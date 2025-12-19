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
                     query_params: dict = None,
                     headers: dict = None):
        """
        Getting the Response object.
        Log lines are consolidated into single variable to support concurrent requests, if any are added.

        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
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
                                       "timeout": 30,
                                       "verify": True,
                                       },
                              "DELETE": {"method": method,
                                         "url": url,
                                         "headers": self.headers,
                                         "params": query_params,
                                         "data": payload,
                                         "timeout": 30,
                                         "verify": True,
                                         },
                              "PUT": {"method": method,
                                      "url": url,
                                      "headers": self.headers,
                                      "params": query_params,
                                      "data": payload,
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
                     query_params: dict = None,
                     headers: dict = None,
                     is_return_resp_obj: bool = False,
                     raise_error_if_failed: bool = None):
        """
        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
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
        response_obj = super().make_request(method, uri, payload, query_params, headers)
        if is_return_resp_obj:
            return response_obj
        resp_text = response_obj.text
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

    def get_access_token(self, username, password):
        """
        /api/v1/auth/jwt/create

        Returns:
            dict
        """
        payload = {"username": username, "password": password}
        response = self.make_request("post",
                                     "/api/v1/auth/jwt/create",
                                     payload=payload)
        return response

    def get_users(self, access: str, search: str = "", page_num: int = 1, page_size: int = 100, ordering: str = "id"):
        """
        /api/v1/users

        Returns:
            dict
        """
        params = {"search": search, "page": page_num, "page_size": page_size, "ordering": ordering}
        response = self.make_request("get",
                                     "/api/v1/users",
                                     query_params=params,
                                     headers=self.get_authorization_token_dict(access))
        return response

    def bulk_user_delete(self, access: str, user_id_list: list):
        """
        /api/v1/users/bulk-delete/

        Returns:
            dict, {"deleted": $number}
        """
        payload = {"ids": user_id_list}
        response = self.make_request("post",
                                     "/api/v1/users/bulk-delete/",
                                     payload=payload,
                                     headers=self.get_authorization_token_dict(access))
        return response

    def create_user(self, access: str, username: str, email: str, password: str):
        """
        /api/v1/auth/users/

        Returns:
            dict
        """
        payload = {"username": username, "email": email, "password": password}
        response = self.make_request("post",
                                     "/api/v1/auth/users/",
                                     payload=payload,
                                     headers=self.get_authorization_token_dict(access))
        return response
