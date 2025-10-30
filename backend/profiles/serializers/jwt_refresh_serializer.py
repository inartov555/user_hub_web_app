"""
Ensures that:
  - The returned *access* token always carries the CURRENT boot_id
  - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
This allows clients to recover after a server restart without forcing a full re-login.
"""

from typing import Any, Dict, Optional, Callable
from datetime import timedelta

from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.utils import translation
from rest_framework.exceptions import APIException, ValidationError  # <-- add imports
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from ..boot import get_boot_id
from ..models.app_settings import get_effective_auth_settings
from ..utils.auth_tokens import temporary_token_lifetimes


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
        eff = get_effective_auth_settings()
        with temporary_token_lifetimes(
            access_seconds=eff.access_token_lifetime_seconds,
            refresh_seconds=eff.idle_timeout_seconds,
        ):
            result = super().validate(attrs)
            # ensure boot_id on access (and on rotated refresh if present)
            self._inject_boot_id_into_tokens(result)
            return result

    def _try_blacklist_refresh(self, refresh_token: RefreshToken) -> None:
        """
        Attempt to blacklist a refresh token safely.
        - No-op if the blacklist app is not installed (keeps behavior compatible).
        - Raises localized, specific exceptions for expected failure modes.
        """
        # Fast exit if the blacklist app isn’t installed
        if not apps.is_installed("rest_framework_simplejwt.token_blacklist"):
            return

        # Honor SIMPLE_JWT setting (should already be true in caller, but keep defensive)
        if not settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", True):
            return

        # Access blacklist() safely to satisfy linters when the attribute may not exist on the type
        blacklister: Optional[Callable[[], None]] = getattr(refresh_token, "blacklist", None)
        if not callable(blacklister):
            return

        try:
            blacklister()  # pylint: disable=no-member
        except TokenError as exc:
            # Surface as a field validation error for the client (localized)
            raise ValidationError({"refresh": [translation.gettext("Invalid refresh token.")]}) from exc
        except (IntegrityError, DatabaseError) as exc:
            # Database write failed (duplicate/DB down). Tell the client clearly (localized).
            # Your global exception handler will wrap this into the standard error envelope.
            raise APIException(
                detail=translation.gettext("Failed to blacklist token."),
                code="auth.blacklist_failed",
            ) from exc

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
