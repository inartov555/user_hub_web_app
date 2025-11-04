"""
Authentication runtime configuration API endpoint.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.app_settings import get_effective_auth_settings, JWT_RENEW_AT_SECONDS_KEY, \
    IDLE_TIMEOUT_SECONDS_KEY, ACCESS_TOKEN_LIFETIME_KEY, ROTATE_REFRESH_TOKENS_KEY


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def runtime_auth_config(_request):
    """
    Return the effective authentication timing settings.
    """
    eff = get_effective_auth_settings()
    renew = eff.jwt_renew_at_seconds if eff.rotate_refresh_tokens else 0
    return Response({
        ACCESS_TOKEN_LIFETIME_KEY: eff.access_token_lifetime_seconds,
        JWT_RENEW_AT_SECONDS_KEY: renew,
        IDLE_TIMEOUT_SECONDS_KEY: eff.idle_timeout_seconds,
        ROTATE_REFRESH_TOKENS_KEY: eff.rotate_refresh_tokens,
    })
