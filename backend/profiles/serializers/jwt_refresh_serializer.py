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
        '''
        refresh_str = attrs.get("refresh")
        if not refresh_str:
            # Localized
            raise InvalidToken(translation.gettext("No refresh token provided"))

        try:
            refresh_in = RefreshToken(refresh_str)
        except TokenError as exc:
            # chain the cause
            raise InvalidToken(str(exc)) from exc

        current_boot = int(get_boot_id())
        token_boot = refresh_in.payload.get("boot_id")

        # Treat missing or mismatched boot_id as invalid -> forces login after reboot
        if token_boot != current_boot:
            raise InvalidToken(translation.gettext("Session expired due to server restart."))

        # boot_id matches -> proceed like normal SimpleJWT refresh
        access: AccessToken = refresh_in.access_token
        access["boot_id"] = current_boot  # keep it explicit

        data: Dict[str, Any] = {"access": str(access)}

        rotate = bool(settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False))
        blacklist_after_rotation = bool(settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False))

        if rotate:
            if blacklist_after_rotation and apps.is_installed("rest_framework_simplejwt.token_blacklist"):
                # Blacklist the *previous* refresh token (if using rotation/blacklist feature)
                self._try_blacklist_refresh(refresh_in)

            user = self._user_from_token(refresh_in)
            new_refresh: RefreshToken = RefreshToken.for_user(user)
            new_refresh["boot_id"] = current_boot
            data["refresh"] = str(new_refresh)

        return data
        '''
        eff = get_effective_auth_settings()
        prev_access = AccessToken.lifetime
        prev_refresh = RefreshToken.lifetime
        try:
            AccessToken.lifetime = timedelta(seconds=eff.access_token_lifetime_seconds)
            RefreshToken.lifetime = timedelta(seconds=eff.idle_timeout_seconds)

            # Build the new access token from the (possibly rotated) refresh
            rt = RefreshToken(data.get("refresh") or attrs.get("refresh"))
            at = rt.access_token
            at["boot_id"] = int(get_boot_id())
            # Optional: expose the current renew threshold in the token so client can read it
            at["jwt_renew_at_seconds"] = eff.jwt_renew_at_seconds

            data["access"] = str(at)

            # If you rotate refresh tokens here, ensure the rotated one gets proper lifetime & boot_id too.
            if "refresh" in data:
                new_rt = RefreshToken(data["refresh"])
                new_rt["boot_id"] = int(get_boot_id())
                data["refresh"] = str(new_rt)
        except TokenError as exc:
            # chain the cause
            raise InvalidToken(str(exc)) from exc
        finally:
            AccessToken.lifetime = prev_access
            RefreshToken.lifetime = prev_refresh
        current_boot = int(get_boot_id())
        token_boot = refresh_in.payload.get("boot_id")

        # Treat missing or mismatched boot_id as invalid -> forces login after reboot
        if token_boot != current_boot:
            raise InvalidToken(translation.gettext("Session expired due to server restart."))

        # boot_id matches -> proceed like normal SimpleJWT refresh
        access: AccessToken = refresh_in.access_token
        access["boot_id"] = current_boot  # keep it explicit

        data: Dict[str, Any] = {"access": str(access)}

        rotate = bool(settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False))
        blacklist_after_rotation = bool(settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False))

        if rotate:
            if blacklist_after_rotation and apps.is_installed("rest_framework_simplejwt.token_blacklist"):
                # Blacklist the *previous* refresh token (if using rotation/blacklist feature)
                self._try_blacklist_refresh(refresh_in)

            user = self._user_from_token(refresh_in)
            new_refresh: RefreshToken = RefreshToken.for_user(user)
            new_refresh["boot_id"] = current_boot
            data["refresh"] = str(new_refresh)

        return data

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
