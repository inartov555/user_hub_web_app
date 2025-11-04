"""
Authentication runtime configuration API endpoint.
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
    """
    eff = get_effective_auth_settings()
    return Response({
        "ACCESS_TOKEN_LIFETIME": eff.access_token_lifetime_seconds,
        "JWT_RENEW_AT_SECONDS": eff.jwt_renew_at_seconds,
        "IDLE_TIMEOUT_SECONDS": eff.idle_timeout_seconds,
        "ROTATE_REFRESH_TOKENS": eff.rotate_refresh_tokens,
    })
