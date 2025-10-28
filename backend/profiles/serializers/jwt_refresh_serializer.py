"""
Ensures that:
  - The returned *access* token always carries the CURRENT boot_id
  - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
This allows clients to recover after a server restart without forcing a full re-login.
"""

from typing import Any, Dict

from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.utils import translation
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
        token_boot = refresh_in.payload.get("boot_id")

        # *** CRITICAL CHANGE ***
        # Treat missing or mismatched boot_id as invalid -> forces login after reboot
        if token_boot != current_boot:
            raise InvalidToken("Session expired due to server restart.")

        # boot_id matches -> proceed like normal SimpleJWT refresh
        access: AccessToken = refresh_in.access_token
        access["boot_id"] = current_boot  # keep it explicit

        data: Dict[str, Any] = {"access": str(access)}

        rotate = bool(settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False))
        blacklist_after_rotation = bool(settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False))

        if rotate:
            if blacklist_after_rotation and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
                # Blacklist the *previous* refresh token (if using rotation/blacklist feature)
                _try_blacklist_refresh(refresh_in)

            user = self._user_from_token(refresh_in)
            new_refresh: RefreshToken = RefreshToken.for_user(user)
            new_refresh["boot_id"] = current_boot
            data["refresh"] = str(new_refresh)

        return data

    def _try_blacklist_refresh(refresh_token) -> None:
        """
        Attempt to blacklist a refresh token safely.
        - No-op if the blacklist app is not installed (keeps behavior compatible).
        - Raises localized, specific exceptions for expected failure modes.
        """
        # Fast exit if the blacklist app isn’t installed
        if not apps.is_installed("rest_framework_simplejwt.token_blacklist"):
            return

        # Optional: honor SIMPLE_JWT settings
        blacklist_after_rotation = getattr(
            settings, "SIMPLE_JWT", {}
        ).get("BLACKLIST_AFTER_ROTATION", True)
        if not blacklist_after_rotation:
            return

        try:
            refresh_token.blacklist()
        except TokenError:
            # e.g., malformed/expired token object being blacklisted
            # Surface as a field validation error for the client
            raise ValidationError({"refresh": [translation.gettext("Invalid refresh token.")]})
        except (IntegrityError, DatabaseError):
            # Database write failed (duplicate/DB down). Tell the client clearly.
            # Your exception handler will wrap this into the standard error envelope.
            raise APIException(detail=translation.gettext("Failed to blacklist token."), code="auth.blacklist_failed")
        # Note: do NOT catch a bare Exception here; let unexpected errors surface.

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
