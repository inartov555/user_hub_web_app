"""
DRF authentication class that:
  - Extracts access token only from the Authorization: Bearer header
  - Sets request.user / request.auth when valid
  - Does not refresh via cookies; clients call the refresh API explicitly
  - Optionally flags near-expiry (JWT_RENEW_AT_SECONDS), but does not set cookies
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import Optional
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone, translation
from django.db import DatabaseError, IntegrityError

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    Header-only, stateless JWT auth for DRF.
    - No cookie handling
    - No automatic refresh/rotation
    - Near-expiry flagged on the request for clients/UI to act on
    """

    www_authenticate_realm = "api"
    keyword = b"bearer"  # lower-cased for comparison

    def __init__(self) -> None:
        self.user_model = get_user_model()

    def authenticate(self, request):
        # Provide a namespace for side-channel info (mirrors prior middleware)
        if not hasattr(request, "jwt"):
            request.jwt = SimpleNamespace(
                new_access_token=None,  # type: Optional[str]
                new_refresh_token=None,  # type: Optional[str]
                auth_failed=False,
                near_expiry=False,
                seconds_to_expiry=None,
            )
        # Public mirrors (kept for backward compat with code that read these)
        request.new_access_token: Optional[str] = None
        request.new_refresh_token: Optional[str] = None
        request.jwt_auth_failed: bool = False

        raw_access = self._get_access_from_request(request)
        if not raw_access:
            # No credentials supplied -> let DRF treat as unauthenticated
            return None

        try:
            access_token = AccessToken(raw_access)
            user = self._user_from_token(access_token)

            # Optionally flag near-expiry (no auto-renew)
            seconds_left = self._seconds_to_expiry(access_token)
            request.jwt.seconds_to_expiry = seconds_left
            if self._should_renew(access_token):
                request.jwt.near_expiry = True

            # On success, DRF expects (user, auth)
            return (user, str(access_token))

        except (TokenError, InvalidToken) as exc:
            # Preserve previous "auth failed" side-channel flag,
            # but fail the request in DRF terms for protected views.
            request.jwt_auth_failed = True
            request.jwt.auth_failed = True
            raise AuthenticationFailed(detail=str(exc)) from exc

    def authenticate_header(self, request) -> str:
        # Controls the WWW-Authenticate header on 401s
        return f'Bearer realm="{self.www_authenticate_realm}"'

    def _get_access_from_request(self, request) -> Optional[str]:
        """
        Read `Authorization: Bearer <access>` from headers. No cookies.
        Accepts any case for "Bearer"; ignores malformed headers.
        """
        auth = get_authorization_header(request)
        if not auth:
            return None

        parts = auth.split()
        if len(parts) != 2:
            return None

        scheme, token = parts[0].lower(), parts[1]
        if scheme != self.keyword:
            return None

        try:
            return token.decode("utf-8")
        except UnicodeDecodeError:
            return token if isinstance(token, str) else None

    def _user_from_token(self, token: AccessToken):
        user_id = token.get("user_id") or token.get("sub")
        if not user_id:
            raise InvalidToken(translation.gettext("user_id claim missing"))
        return self.user_model.objects.get(pk=user_id)

    def _seconds_to_expiry(self, token: AccessToken) -> Optional[int]:
        try:
            exp_ts = int(token["exp"])
        except (KeyError, TypeError, ValueError):
            return None
        now_ts = int(timezone.now().timestamp())
        return max(0, exp_ts - now_ts)

    def _should_renew(self, token: AccessToken) -> bool:
        seconds_left = self._seconds_to_expiry(token)
        if seconds_left is None:
            return False

        threshold = getattr(settings, "JWT_RENEW_AT_SECONDS", None)
        try:
            threshold_int = int(threshold)
        except (TypeError, ValueError):
            threshold_int = 0

        return seconds_left <= max(0, threshold_int)

    # Kept for parity with previous implementation (not used automatically).
    # If you later decide to rotate on a dedicated endpoint, this is handy.
    def _refresh_from_refresh(self, refresh_str: str, request):
        rt = RefreshToken(refresh_str)
        new_at = rt.access_token

        # Rotate refresh if enabled
        new_rt_str = None
        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
                try:
                    rt.blacklist()
                except (DatabaseError, IntegrityError) as exc:
                    logger.warning("Failed to blacklist refresh token: %s", exc)
            new_rt = RefreshToken.for_user(self._user_from_token(new_at))
            new_rt_str = str(new_rt)

        request.new_access_token = str(new_at)
        request.jwt.new_access_token = str(new_at)
        if new_rt_str:
            request.new_refresh_token = new_rt_str
            request.jwt.new_refresh_token = new_rt_str
