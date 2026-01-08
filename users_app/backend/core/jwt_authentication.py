"""
DRF authentication class that:
  - Extracts access token only from the Authorization: Bearer header
  - Sets request.user / request.auth when valid
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import Optional
import logging
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


logger = logging.getLogger(__name__)
BLACKLIST_PREFIX = "jwt:bl:"


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
        # eff = get_effective_auth_settings()  # pulls DB overrides live
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
            access_token = self.get_validated_token(raw_access)
            user = self._user_from_token(access_token)

            # Flag near-expiry (no auto-renew)
            seconds_left = self._seconds_to_expiry(access_token)
            request.jwt.seconds_to_expiry = seconds_left

            # On success, DRF expects (user, auth)
            return (user, access_token)

        except (TokenError, InvalidToken) as exc:
            # Preserve previous "auth failed" side-channel flag,
            # but fail the request in DRF terms for protected views.
            request.jwt_auth_failed = True
            request.jwt.auth_failed = True
            raise AuthenticationFailed(detail=str(exc)) from exc
        except AuthenticationFailed as exc:
            request.jwt_auth_failed = True
            request.jwt.auth_failed = True
            raise

    def authenticate_header(self, request) -> str:
        # Controls the WWW-Authenticate header on 401s
        return f'Bearer realm="{self.www_authenticate_realm}"'

    def _get_access_from_request(self, request) -> Optional[str]:
        """
        Read Authorization: Bearer <access> from headers. No cookies.
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
            raise ValidationError(
                {"non_field_errors": ["user_id claim missing"]}
            )
        return self.user_model.objects.get(pk=user_id)

    def _seconds_to_expiry(self, token: AccessToken) -> Optional[int]:
        try:
            exp_ts = int(token["exp"])
        except (KeyError, TypeError, ValueError):
            return None
        now_ts = int(datetime.now(timezone.utc).timestamp())
        return max(0, exp_ts - now_ts)

    def get_validated_token(self, raw_token: str) -> AccessToken:
        """
        Return a validated SimpleJWT AccessToken instance (or raise AuthenticationFailed)
        """
        try:
            return AccessToken(raw_token)
        except (TokenError, InvalidToken) as exc:
            raise AuthenticationFailed(detail=str(exc)) from exc



class JWTAuthenticationWithDenylist(JWTAuthentication):
    """
    Blacklisting tokens
    """
    def get_validated_token(self, raw_token):
        """
        Get valid token and raise error if it's blacklisted
        """
        token = super().get_validated_token(raw_token)
        jti = token.get("jti") if token else None
        if jti and cache.get(f"{BLACKLIST_PREFIX}{jti}"):
            raise AuthenticationFailed("Token is blacklisted", code="token_not_valid")
        return token
