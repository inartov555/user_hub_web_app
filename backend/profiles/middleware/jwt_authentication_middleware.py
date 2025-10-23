"""
Stateless auth middleware that:
  - Extracts access token only from Authorization header (no cookies)
  - Sets request.user when valid
  - Does not refresh via cookies; clients refresh via API
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
from django.db import DatabaseError, IntegrityError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from ..tools.logger.logger import Logger


logger = Logger(__name__)


def _get_settings():
    # small helper to avoid attribute errors in tests
    cfg = getattr(settings, "JWT_COOKIE", {})
    return {
        "ACCESS_COOKIE_NAME": cfg.get("ACCESS_COOKIE_NAME"),
        "REFRESH_COOKIE_NAME": cfg.get("REFRESH_COOKIE_NAME"),
        "RENEW_AT_SECONDS": cfg.get("RENEW_AT_SECONDS"),
        "COOKIE_PATH": cfg.get("COOKIE_PATH"),
        "COOKIE_DOMAIN": cfg.get("COOKIE_DOMAIN"),
        "COOKIE_SAMESITE": cfg.get("COOKIE_SAMESITE"),
        "COOKIE_SECURE": bool(cfg.get("COOKIE_SECURE")),
        "COOKIE_HTTPONLY": bool(cfg.get("COOKIE_HTTPONLY")),
    }


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
        # Public attributes; avoid protected access warnings.
        # These mirror the previous underscore fields but without leading underscores.
        request.new_access_token: Optional[str] = None
        request.new_refresh_token: Optional[str] = None
        request.jwt_auth_failed: bool = False

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
                        access_token_obj = AccessToken(request.new_access_token)  # type: ignore[arg-type]
                        user = self._user_from_token(access_token_obj)
                    except (TokenError, InvalidToken):
                        request.jwt_auth_failed = True
                else:
                    request.jwt_auth_failed = True
        elif refresh:
            # No access but we have a refresh cookie → attempt refresh
            try:
                self._refresh_from_refresh(refresh, request)
                access_token_obj = AccessToken(request.new_access_token)  # type: ignore[arg-type]
                user = self._user_from_token(access_token_obj)
            except (TokenError, InvalidToken):
                request.jwt_auth_failed = True

        return response

    # ---- helpers ----

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
            # When rotating, SimpleJWT expects you to blacklist and create a new one.
            # Only swallow expected DB/blacklist errors; don't hide everything.
            if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
                try:
                    rt.blacklist()  # requires 'token_blacklist' app + migrations
                except (DatabaseError, IntegrityError) as exc:
                    logger.warning(f"Failed to blacklist refresh token: {exc}")
            new_rt = RefreshToken.for_user(self._user_from_token(new_at))
            new_rt_str = str(new_rt)

        request.new_access_token = str(new_at)
        if new_rt_str:
            request.new_refresh_token = new_rt_str
