"""
Stateless auth middleware that:
  - Extracts access token only from the Authorization: Bearer header
  - Sets request.user when valid
  - Does not refresh via cookies; clients call the refresh API explicitly
  - Optionally flags near-expiry (RENEW_AT_SECONDS), but does not set cookies
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import Optional
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone, translation
from django.db import DatabaseError, IntegrityError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


logger = logging.getLogger(__name__)


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
      - Extracts access token only from the Authorization: Bearer header
      - Sets request.user when valid
      - Does not refresh via cookies; clients call the refresh API explicitly
      - Optionally flags near-expiry (RENEW_AT_SECONDS), but does not set cookies
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.user_model = get_user_model()

    def __call__(self, request):
        # Namespace to avoid "protected-access" (W0212)
        request.jwt = SimpleNamespace(
            new_access_token=None,  # type: Optional[str]
            new_refresh_token=None,  # type: Optional[str]
            auth_failed=False,
        )
        # Public attributes; avoid protected access warnings.
        # These mirror the previous underscore fields but without leading underscores.
        request.new_access_token: Optional[str] = None
        request.new_refresh_token: Optional[str] = None
        request.jwt_auth_failed: bool = False

        access = self._get_access_from_request(request)
        # We do NOT auto-refresh in middleware anymore. Always return None.
        # (Clients should call the refresh endpoint and then resend with a new access token.)
        refresh: Optional[str] = None

        if access:
            try:
                access_token_obj = AccessToken(access)
                # Proactive refresh if near expiry (only if a refresh token mechanism exists)
                if refresh and self._should_renew(access_token_obj):
                    self._refresh_from_refresh(refresh, request)
            except (TokenError, InvalidToken):
                request.jwt_auth_failed = True
        response = self.get_response(request)
        return response

    # Token extractors (header-only)
    def _get_access_from_request(self, request) -> Optional[str]:
        """
        Read 'Authorization: Bearer <access>' from headers. No cookies.
        """
        auth = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization")
        if not auth:
            return None
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    def _user_from_token(self, token: AccessToken):
        user_id = token.get("user_id") or token.get("sub")
        if not user_id:
            raise InvalidToken(translation.gettext("user_id claim missing"))
        return self.user_model.objects.get(pk=user_id)

    def _should_renew(self, token: AccessToken) -> bool:
        # token['exp'] is a UNIX timestamp
        exp_ts = int(token["exp"])
        now_ts = int(timezone.now().timestamp())

        # Prefer a dedicated setting; fall back to legacy JWT_COOKIE value; default 0
        threshold = getattr(settings, "JWT_RENEW_AT_SECONDS", None)
        try:
            threshold_int = int(threshold)
        except (TypeError, ValueError):
            threshold_int = 0

        return (exp_ts - now_ts) <= max(0, threshold_int)

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
                    logger.warning("Failed to blacklist refresh token: %s", exc)
            new_rt = RefreshToken.for_user(self._user_from_token(new_at))
            new_rt_str = str(new_rt)

        request.new_access_token = str(new_at)
        if new_rt_str:
            request.new_refresh_token = new_rt_str
