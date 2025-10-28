"""
Ensures that:
  - The returned *access* token always carries the CURRENT boot_id
  - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
This allows clients to recover after a server restart without forcing a full re-login.
"""

from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from ..boot import get_boot_id


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
        refresh_str = attrs.get("refresh")
        if not refresh_str:
            raise InvalidToken("No refresh token provided")

        try:
            refresh_in = RefreshToken(refresh_str)
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc

        current_boot = int(get_boot_id())

        # Always mint a new access token and stamp current boot_id
        access: AccessToken = refresh_in.access_token
        access["boot_id"] = current_boot

        data: Dict[str, Any] = {"access": str(access)}

        # If rotation enabled, blacklist old refresh (when applicable) and create a NEW refresh
        rotate = bool(settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False))
        blacklist_after_rotation = bool(settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False))

        if rotate:
            # Blacklist the old refresh if blacklist app is installed
            if blacklist_after_rotation and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
                try:
                    refresh_in.blacklist()
                except (AttributeError, TokenError):
                    pass

            # Create a fresh refresh for the same user and stamp current boot_id
            user = self._user_from_token(refresh_in)
            new_refresh: RefreshToken = RefreshToken.for_user(user)
            new_refresh["boot_id"] = current_boot
            data["refresh"] = str(new_refresh)

        return data

    @staticmethod
    def _user_from_token(token: Token):
        """
        Map token.sub (user id) to a user instance, honoring SIMPLE_JWT user id field/type.
        """
        user_model = get_user_model()
        user_id_field = settings.SIMPLE_JWT.get("USER_ID_FIELD", "id")
        user_id = token.get(settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id"))
        return user_model.objects.get(**{user_id_field: user_id})

    def create(self, validated_data):
        # Not used for token refresh; defined to satisfy BaseSerializer interface.
        return validated_data

    def update(self, instance, validated_data):
        # Not supported for this serializer.
        return instance
