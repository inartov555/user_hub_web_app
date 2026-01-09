"""
Ensures that:
  - The returned *access* token always carries the CURRENT boot_id
  - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
This allows clients to recover after a server restart without forcing a full re-login.
"""

from typing import Any, Dict
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, Token

from ..models.app_settings import get_effective_auth_settings


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Ensures that:
      - The returned *access* token always carries the CURRENT boot_id
      - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
    This allows clients to recover after a server restart without forcing a full re-login.
    """

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validation
        """
        eff = get_effective_auth_settings()  # pulls DB overrides live
        raw = attrs.get("refresh")
        rt = RefreshToken(raw)

        # Enforce idle on refresh even if token's original exp is longer
        iat = datetime.fromtimestamp(int(rt["iat"]), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        if (now - iat).total_seconds() > eff.idle_timeout_seconds:
            raise ValidationError("Session expired due to inactivity.")

        data = super().validate(attrs)

        # Ensure new access token carries current BOOT_ID etc.
        boot_id = settings.SIMPLE_JWT.get("BOOT_ID")
        if boot_id:
            at = AccessToken(data["access"])
            at["boot_id"] = boot_id
            data["access"] = str(at)

        return data

    @staticmethod
    def _user_from_token(token: Token) -> "User":
        """
        Map token.sub (user id) to a user instance, honoring SIMPLE_JWT user id field/type.
        """
        user_model = get_user_model()
        user_id_field = settings.SIMPLE_JWT.get("USER_ID_FIELD", "id")
        user_id = token.get(settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id"))
        return user_model.objects.get(**{user_id_field: user_id})

    def create(self, validated_data) -> dict[str, Any]:
        # Not used for token refresh; defined to satisfy BaseSerializer interface.
        return validated_data

    def update(self, instance, validated_data) -> Any:
        # Not supported for this serializer.
        return instance
