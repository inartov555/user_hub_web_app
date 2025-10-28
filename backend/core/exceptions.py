"""
Localized DRF exception handler that returns a consistent, translatable error envelope.

Response shape
--------------
Every error response follows this envelope:

{
  "error": {
    "code": "<stable.machine.code>",  # e.g. "auth.not_authenticated"
    "message": "<localized.human.message>",  # translated with gettext
    "i18n_key": "<namespaced.i18n.key>",  # e.g. "errors.auth.not_authenticated"
    "details": null | list | dict,  # validation fields, nested, translated
    "lang": "<active-language-code>"  # e.g. "en", "et"
  }
}
"""

from typing import Any, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import translation
from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from rest_framework.response import Response


# Optional: a small catalog to map common DRF exception classes to our error codes & i18n keys
EXC_MAP = {
    exceptions.NotAuthenticated: ("auth.not_authenticated",
                                  "errors.auth.not_authenticated",
                                  translation.gettext("Not authenticated.")),
    exceptions.AuthenticationFailed: ("auth.auth_failed",
                                      "errors.auth.auth_failed",
                                      translation.gettext("Authentication credentials were not provided.")),
    exceptions.PermissionDenied: ("auth.permission_denied",
                                  "errors.auth.permission_denied",
                                  translation.gettext("You do not have permission to perform this action.")),
    exceptions.NotFound: ("common.not_found",
                          "errors.common.not_found",
                          translation.gettext("Not found.")),
    exceptions.MethodNotAllowed: ("common.method_not_allowed",
                                  "errors.common.method_not_allowed",
                                  translation.gettext('Method "%(method)s" not allowed.')),
    exceptions.Throttled: ("common.throttled",
                           "errors.common.throttled",
                           translation.gettext("Request was throttled.")),
    exceptions.ParseError: ("common.parse_error",
                            "errors.common.parse_error",
                            translation.gettext("Malformed request.")),
    exceptions.UnsupportedMediaType: ("common.unsupported_media_type",
                                      "errors.common.unsupported_media_type",
                                      translation.gettext("Unsupported media type.")),
    exceptions.NotAcceptable: ("common.not_acceptable",
                               "errors.common.not_acceptable",
                               translation.gettext("Not acceptable.")),
    exceptions.APIException: ("common.server_error",
                              "errors.common.server_error",
                              translation.gettext("A server error occurred.")),
}

def _to_str(value: Any) -> str:
    """
    Convert ErrorDetail/lazy strings/anything to a plain string in the active language.
    """
    try:
        return str(translation.gettext(value))  # translate if it's a raw string key
    except Exception:
        try:
            return str(value)  # fall back, return the save string, if localization not found
        except Exception:
            return translation.gettext("Unknown error.")

def _serialize_validation_errors(detail) -> Any:
    """
    DRF ValidationError.detail can be a dict/list/str. Keep structure but translate strings.
    """
    if isinstance(detail, dict):
        return {k: _serialize_validation_errors(v) for k, v in detail.items()}
    if isinstance(detail, list):
        return [_serialize_validation_errors(x) for x in detail]
    if isinstance(detail, str):
        return str(_to_str(detail))
    return _to_str(detail)

def _resolve_mapping(exc) -> Optional[tuple[str, str, str]]:
    for cls, triple in EXC_MAP.items():
        if isinstance(exc, cls):
            return triple
    return None

def localized_exception_handler(exc, context):
    """
    Wrap DRF's exception handling, then output our normalized, localized envelope.
    """
    response = exception_handler(exc, context)

    # Django ValidationError (not DRF)
    if isinstance(exc, DjangoValidationError) and response is None:
        data = _serialize_validation_errors(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
        return Response(
            {
                "error": {
                    "code": "validation.error",
                    "message": _to_str("Invalid input."),
                    "i18n_key": "errors.validation.invalid",
                    "details": data,
                    "lang": translation.get_language(),
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if response is None:
        # Unhandled → 500
        return Response(
            {
                "error": {
                    "code": "common.server_error",
                    "message": _to_str("A server error occurred."),
                    "i18n_key": "errors.common.server_error",
                    "details": None,
                    "lang": translation.get_language(),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # DRF produced a response (has .data and .status_code)
    mapped = _resolve_mapping(exc)
    if mapped:
        code, i18n_key, default_msg = mapped
        # If DRF attached a string/detail, prefer it but translate; else use our default
        if isinstance(response.data, dict) and "detail" in response.data:
            msg = response.data["detail"]
            msg = str(_to_str(msg))  # translate
            details = None
        else:
            msg = str(default_msg)
            details = _serialize_validation_errors(response.data)
        response.data = {
            "error": {
                "code": code,
                "message": msg,
                "i18n_key": i18n_key,
                "details": details,
                "lang": translation.get_language(),
            }
        }
        return response

    # ValidationError from DRF
    if isinstance(exc, exceptions.ValidationError):
        response.data = {
            "error": {
                "code": "validation.error",
                "message": _to_str("Invalid input."),
                "i18n_key": "errors.validation.invalid",
                "details": _serialize_validation_errors(exc.detail),
                "lang": translation.get_language(),
            }
        }
        return response

    # Fallback: translate "detail" if present and attach a generic code
    if isinstance(response.data, dict):
        detail = response.data.get("detail")
        response.data = {
            "error": {
                "code": "common.error",
                "message": str(_to_str(detail)) if detail else _to_str("A server error occurred."),
                "i18n_key": "errors.common.error",
                "details": None if detail else _serialize_validation_errors(response.data),
                "lang": translation.get_language(),
            }
        }
    return response
