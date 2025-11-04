"""
Chooses the refresh serializer at request time
"""

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from profiles.models.app_settings import get_effective_auth_settings
from profiles.serializers.jwt_refresh_serializer import CustomTokenRefreshSerializer


class RuntimeAwareTokenRefreshView(TokenRefreshView):
    """
    Chooses the refresh serializer at request time:
    - ROTATE_REFRESH_TOKENS = True  -> use CustomTokenRefreshSerializer (rotates)
    - ROTATE_REFRESH_TOKENS = False -> use SimpleJWT's TokenRefreshSerializer (no rotation)
    """
    def get_serializer_class(self):
        eff = get_effective_auth_settings()  # pulls DB overrides live
        if bool(eff.rotate_refresh_tokens):
            return CustomTokenRefreshSerializer
        # fallback to the stock serializer (no rotation)
        return TokenRefreshSerializer
