"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from typing import Any, Dict

from django.conf import settings
from djoser.serializers import TokenCreateSerializer as BaseTokenCreateSerializer
from rest_framework import serializers


class EmailOrUsernameTokenCreateSerializer(BaseTokenCreateSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    def validate(self, attrs):
        """
        Taking email as username
        """
        data = getattr(self, "initial_data", {})
        login = (data.get("email") or data.get("username") or "").strip()
        password = data.get("password") or attrs.get("password")

        if not login or not password:
            raise serializers.ValidationError(
                {"detail": 'Must include "username" or "email" and "password".'}
            )

        login_field = settings.DJOSER.get("LOGIN_FIELD", "email")
        # Put the value into whichever field Djoser expects
        attrs[login_field] = login
        attrs["password"] = password

        # Avoid confusing the base serializer with extra fields
        if login_field == "email":
            attrs.pop("username", None)
        else:
            attrs.pop("email", None)

        return super().validate(attrs)

    # DRF's BaseSerializer declares abstract create/update; implement stubs for pylint.
    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        # Not used by Djoser token creation; present to satisfy linter.
        return validated_data

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        # Not applicable for token creation.
        raise NotImplementedError("Update is not supported for this serializer.")
