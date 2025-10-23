"""
Stateless auth middleware that:
  - Extracts access token from Authorization header or 'access' cookie
  - Sets request.user when valid
  - If access expired and 'refresh' cookie exists, refreshes tokens
  - Proactively refreshes if access expires within RENEW_AT_SECONDS
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


def _get_settings():
    # small helper to avoid attribute errors in tests
    cfg = getattr(settings, "JWT_COOKIE", {})
    return {
        "ACCESS_COOKIE_NAME": cfg.get("ACCESS_COOKIE_NAME", "access"),
        "REFRESH_COOKIE_NAME": cfg.get("REFRESH_COOKIE_NAME", "refresh"),
        "RENEW_AT_SECONDS": int(cfg.get("RENEW_AT_SECONDS", 60)),
        "COOKIE_PATH": cfg.get("COOKIE_PATH", "/"),
        "COOKIE_DOMAIN": cfg.get("COOKIE_DOMAIN"),
        "COOKIE_SAMESITE": cfg.get("COOKIE_SAMESITE", "Lax"),
        "COOKIE_SECURE": bool(cfg.get("COOKIE_SECURE", not settings.DEBUG)),
        "COOKIE_HTTPONLY": bool(cfg.get("COOKIE_HTTPONLY", True)),
    }


def _set_cookie(resp, name, value, *, max_age=None):
    cfg = _get_settings()
    resp.set_cookie(
        name,
        value,
        max_age=max_age,
        path=cfg["COOKIE_PATH"],
        domain=cfg["COOKIE_DOMAIN"],
        secure=cfg["COOKIE_SECURE"],
        httponly=cfg["COOKIE_HTTPONLY"],
        samesite=cfg["COOKIE_SAMESITE"],
    )


def _delete_cookie(resp, name):
    cfg = _get_settings()
    resp.delete_cookie(
        name,
        path=cfg["COOKIE_PATH"],
        domain=cfg["COOKIE_DOMAIN"],
        samesite=cfg["COOKIE_SAMESITE"],
    )


class JWTAuthenticationMiddleware:
    """
    Stateless auth middleware that:
      - Extracts access token from Authorization header or 'access' cookie
      - Sets request.user when valid
      - If access expired and 'refresh' cookie exists, refreshes tokens
      - Proactively refreshes if access expires within RENEW_AT_SECONDS
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.user_model = get_user_model()

    def __call__(self, request):
        # Namespace to avoid "protected-access" (W0212)
        request.jwt = SimpleNamespace(
            new_access_token=None,   # type: Optional[str]
            new_refresh_token=None,  # type: Optional[str]
            auth_failed=False,
        )
        # Will hold any newly minted tokens to be set on the response
        request._new_access_token: Optional[str] = None
        request._new_refresh_token: Optional[str] = None
        request._jwt_auth_failed = False

        access = self._get_access_from_request(request)
        refresh = self._get_refresh_from_request(request)

        user = None
        access_token_obj = None

        if access:
            try:
                access_token_obj = AccessToken(access)
                user = self._user_from_token(access_token_obj)
                # Proactive refresh if near expiry
                if self._should_renew(access_token_obj) and refresh:
                    self._refresh_from_refresh(refresh, request)
            except (TokenError, InvalidToken):
                # Try refresh if access expired/invalid but we have refresh
                if refresh:
                    try:
                        self._refresh_from_refresh(refresh, request)
                        # decode the new access to set user
                        access_token_obj = AccessToken(request._new_access_token)
                        user = self._user_from_token(access_token_obj)
                    except (TokenError, InvalidToken):
                        request._jwt_auth_failed = True
                else:
                    request._jwt_auth_failed = True
        elif refresh:
            # No access but we have a refresh cookie → attempt refresh
            try:
                self._refresh_from_refresh(refresh, request)
                access_token_obj = AccessToken(request._new_access_token)
                user = self._user_from_token(access_token_obj)
            except (TokenError, InvalidToken):
                request._jwt_auth_failed = True

        # Defer DB hit with a lazy object; if user is None fall back to AnonymousUser
        request.user = SimpleLazyObject(lambda: user or AnonymousUser())

        response = self.get_response(request)

        # If we minted new tokens, set cookies
        if request._new_access_token:
            # Access lifetime is in SIMPLE_JWT; we won't set max_age to let the browser treat it as session
            _set_cookie(response, _get_settings()["ACCESS_COOKIE_NAME"], str(request._new_access_token))
        if request._new_refresh_token:
            # For refresh we usually want a persistent cookie; you can compute max_age from SIMPLE_JWT
            refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            _set_cookie(response,
                        _get_settings()["REFRESH_COOKIE_NAME"],
                        str(request._new_refresh_token),
                        max_age=int(refresh_lifetime.total_seconds()))
        # On hard failures, clean up cookies so the client can re-login
        if request._jwt_auth_failed:
            _delete_cookie(response, _get_settings()["ACCESS_COOKIE_NAME"])
            _delete_cookie(response, _get_settings()["REFRESH_COOKIE_NAME"])

        return response

    # ---- helpers ----

    def _get_access_from_request(self, request) -> Optional[str]:
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            return auth.split(" ", 1)[1].strip() or None
        return request.COOKIES.get(_get_settings()["ACCESS_COOKIE_NAME"])

    def _get_refresh_from_request(self, request) -> Optional[str]:
        return request.COOKIES.get(_get_settings()["REFRESH_COOKIE_NAME"])

    def _user_from_token(self, token: AccessToken):
        user_id = token.get("user_id") or token.get("sub")
        if not user_id:
            raise InvalidToken("user_id claim missing")
        return self.user_model.objects.get(pk=user_id)

    def _should_renew(self, token: AccessToken) -> bool:
        # token['exp'] is a UNIX timestamp
        exp_ts = int(token["exp"])
        now_ts = int(timezone.now().timestamp())
        threshold = _get_settings()["RENEW_AT_SECONDS"]
        return (exp_ts - now_ts) <= max(0, threshold)

    def _refresh_from_refresh(self, refresh_str: str, request):
        rt = RefreshToken(refresh_str)
        new_at = rt.access_token

        # Rotate refresh if enabled
        new_rt_str = None
        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            # When rotating, SimpleJWT expects you to blacklist and create a new one
            try:
                rt.blacklist()  # requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS
            except Exception:
                # If blacklist app not enabled, ignoring
                pass
            new_rt = RefreshToken.for_user(self._user_from_token(new_at))
            new_rt_str = str(new_rt)

        request._new_access_token = str(new_at)
        if new_rt_str:
            request._new_refresh_token = new_rt_str
