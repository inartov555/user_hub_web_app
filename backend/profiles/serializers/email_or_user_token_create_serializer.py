"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from typing import Any, Dict
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import translation, timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import serializers

from ..boot import get_boot_id
from ..models.app_settings import get_effective_auth_settings


class EmailOrUsernameTokenCreateSerializer(TokenObtainPairSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """

    @classmethod
    def get_token(cls, user) -> dict:
        """
        Getting token
        """
        eff = get_effective_auth_settings()
        at = AccessToken.for_user(user)
        rt = RefreshToken.for_user(user)

        # Force expiries from DB-driven settings
        now = timezone.now()
        at.set_exp(from_time=now, lifetime=timedelta(seconds=eff.access_token_lifetime_seconds))
        rt.set_exp(from_time=now, lifetime=timedelta(seconds=eff.idle_timeout_seconds))  # note: “idle” drives refresh exp

        boot_id = get_boot_id
        if boot_id:
            at["boot_id"] = boot_id
            rt["boot_id"] = boot_id

        return at, rt

    def _resolve_login_field(self) -> str:
        """
        Prefer the underlying user's USERNAME_FIELD (what auth actually uses).
        Fall back to DJOSER['LOGIN_FIELD'], and finally 'email'.
        """
        user_model = get_user_model()
        # e.g., email for email-only user models, username for default
        username_field = getattr(user_model, "USERNAME_FIELD", None)
        if username_field:
            return username_field

        djoser_login = getattr(settings, "DJOSER", {}).get("LOGIN_FIELD")
        return djoser_login or "email"

    @staticmethod
    def _normalize(login: str, field: str) -> str:
        login = (login or "").strip()
        # emails are generally case-insensitive; normalize to lower
        if field == "email":
            return login.lower()
        return login

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accept either:
          - attrs['login'] OR
          - attrs['email'] / attrs['username']
        Then map it to the configured login field and call base validation.
        """
        # 1) extract provided login & password
        provided_login = (
            attrs.get("login")
            or attrs.get("email")
            or attrs.get("username")
            or ""
        )
        password = attrs.get("password")

        # 2) figure out which field the project actually uses
        login_field = self._resolve_login_field()  # "email" or "username" typically

        # 3) normalize & validate presence
        login_value = self._normalize(provided_login, login_field)
        if not login_value or not password:
            # consistent, frontend-friendly error shape
            raise serializers.ValidationError(
                {"detail": translation.gettext("Must include 'login' (or 'email'/'username') and 'password'.")}
            )

        # 4) put the login into the correct field; drop the others
        attrs[login_field] = login_value
        for k in ("login", "email", "username"):
            if k != login_field:
                attrs.pop(k, None)

        # 5) delegate to Djoser (this will validate credentials & active user)
        return super().validate(attrs)

    # DRF's BaseSerializer declares abstract create/update; implement stubs for pylint.
    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        # Not used by Djoser token creation; present to satisfy linter.
        return validated_data

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        # Not applicable for token creation.
        raise NotImplementedError("Update is not supported for this serializer.")
