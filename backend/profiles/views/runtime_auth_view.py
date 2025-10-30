"""
Authentication runtime configuration API endpoint.

This module exposes a small read-only API that returns the *effective*
authentication-related timing settings currently active in the application.
It is intended for front-end clients to discover values that affect UX
(e.g., token lifetime, idle timeout, and when to renew JWTs).

Response (HTTP 200, JSON):
    {
        "ACCESS_TOKEN_LIFETIME": <int>,  # seconds
        "JWT_RENEW_AT_SECONDS":  <int>,  # seconds before expiry to renew
        "IDLE_TIMEOUT_SECONDS":  <int>,  # seconds of user inactivity allowed
    }

Permissions:
    - Requires an authenticated user (DRF `IsAuthenticated`).
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.app_settings import get_effective_auth_settings


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def runtime_auth_config(_request):
    """
    Return the effective authentication timing settings.

    Fetches values from the server-side configuration source
    (`get_effective_auth_settings`) and returns them as a JSON payload.
    Useful for clients that need to align UI timers (e.g., countdowns,
    auto-logout warnings) with backend policy.

    Args:
        _request: DRF `Request` object. The value is not used directly;
            authentication is enforced by the `IsAuthenticated` permission.

    Returns:
        Response: A DRF `Response` with HTTP 200 and a JSON body containing:
            - ACCESS_TOKEN_LIFETIME (int): Access token lifetime in seconds.
            - JWT_RENEW_AT_SECONDS (int): Seconds before expiry when the client
              should proactively renew its JWT.
            - IDLE_TIMEOUT_SECONDS (int): Idle timeout window in seconds.

    Raises:
        Not directly raised here. DRF may return:
            - 401 Unauthorized: if the user is not authenticated.
            - 403 Forbidden: if authentication passes but access is denied by
              additional permission checks (none beyond `IsAuthenticated` here).

    Example:
        >>> # curl example (token omitted for brevity)
        >>> # curl -H "Authorization: Bearer <token>" https://api.example.com/auth/runtime-config/
        >>> # -> {"ACCESS_TOKEN_LIFETIME": 3600, "JWT_RENEW_AT_SECONDS": 300, "IDLE_TIMEOUT_SECONDS": 900}
    """
    eff = get_effective_auth_settings()
    return Response({
        "ACCESS_TOKEN_LIFETIME": eff.access_token_lifetime_seconds,
        "JWT_RENEW_AT_SECONDS": eff.jwt_renew_at_seconds,
        "IDLE_TIMEOUT_SECONDS": eff.idle_timeout_seconds,
    })
