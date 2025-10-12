"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import TokenCreateSerializer as BaseTokenCreateSerializer
from rest_framework import serializers


class EmailOrUsernameTokenCreateSerializer(BaseTokenCreateSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    class Meta(BaseTokenCreateSerializer.Meta):
        """
        Allow any of these; none required at field level
        """
        fields = ("password", "email", "username", "login")
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "username": {"required": False, "allow_blank": True},
            "login": {"required": False, "allow_blank": True},
        }

    def _resolve_login_field(self) -> str:
        """
        Prefer the underlying user's USERNAME_FIELD (what auth actually uses).
        Fall back to DJOSER['LOGIN_FIELD'], and finally 'email'.
        """
        user_model = get_user_model()
        # e.g., "email" for email-only user models, "username" for default
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
                {"detail": 'Must include "login" (or "email"/"username") and "password".'}
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
