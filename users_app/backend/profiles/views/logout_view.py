"""
JWTs are stateless, so there is no server-side session to destroy.
We invalidate the current ACCESS token by denylisting its JTI.
"""

import time
import logging
from datetime import datetime, timezone as dt_timezone

from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import AccessToken

# Best-effort DB blacklist (won't crash if tables aren't available)
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

logger = logging.getLogger(__name__)

BLACKLIST_PREFIX = "jwt:bl:"


class LogoutView(APIView):
    """
    Log out
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Log out
        """
        token = request.auth  # should be AccessToken instance from your auth class
        if not token:
            raise ValidationError({"details": "No token found"})

        # Ensure we have an AccessToken object
        if isinstance(token, str):
            token = AccessToken(token)

        jti = token.get("jti")
        exp = token.get("exp")  # epoch seconds
        if not (jti and exp):
            raise ValidationError({"details": "Invalid token"})

        # 1) Always denylist in cache (fast + no DB dependency)
        ttl = max(0, int(exp) - int(time.time()))
        cache.set(f"{BLACKLIST_PREFIX}{jti}", 1, timeout=ttl)

        # 2) Best-effort DB blacklist (prevents multi-worker issues if tables exist)
        try:
            raw_access = str(token)  # encoded token string
            expires_at = datetime.fromtimestamp(int(exp), tz=dt_timezone.utc)

            outstanding, _ = OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "user": request.user,
                    "token": raw_access,
                    "expires_at": expires_at,
                },
            )
            BlacklistedToken.objects.get_or_create(token=outstanding)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("DB blacklist failed; cache blacklist still applied: %s", exc)

        return Response(status=204)
