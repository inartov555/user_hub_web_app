"""
Ensures that:
  - The returned *access* token always carries the CURRENT boot_id
  - If ROTATE_REFRESH_TOKENS is enabled, the *rotated refresh* also carries the CURRENT boot_id
This allows clients to recover after a server restart without forcing a full re-login.
"""

from typing import Any, Dict, Optional, Callable
from datetime import datetime

from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.utils import translation, timezone
from rest_framework.exceptions import APIException, ValidationError  # <-- add imports
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, Token
from rest_framework_simplejwt.exceptions import TokenError

from ..boot import get_boot_id
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

        # (Optional) ensure new access token carries current BOOT_ID etc.
        boot_id = settings.SIMPLE_JWT.get("BOOT_ID")
        if boot_id:
            at = AccessToken(data["access"])
            at["boot_id"] = boot_id
            data["access"] = str(at)

        return data

    def _inject_boot_id_into_tokens(self, result: Dict[str, Any]) -> None:
        """
        Add current boot_id to the returned access token (and rotated refresh if present).
        """
        boot_id = int(get_boot_id())
        # Access token
        access_str = result.get("access")
        if access_str:
            access_tok = AccessToken(access_str)
            access_tok["boot_id"] = boot_id
            result["access"] = str(access_tok)
        # Rotated refresh token (only present when ROTATE_REFRESH_TOKENS=True)
        refresh_str = result.get("refresh")
        if refresh_str:
            try:
                ref_tok = RefreshToken(refresh_str)
            except TokenError:
                ref_tok = None
            if ref_tok is not None:
                ref_tok["boot_id"] = boot_id
                # Also attempt to blacklist when enabled
                self._try_blacklist_refresh(ref_tok)
                result["refresh"] = str(ref_tok)

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
