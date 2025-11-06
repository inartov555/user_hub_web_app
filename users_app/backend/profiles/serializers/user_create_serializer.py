"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from profiles.validators import validate_and_normalize_email


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    username = serializers.CharField(min_length=3, max_length=40, required=True)
    password = serializers.CharField(
        min_length=8, max_length=40, write_only=True, required=True, trim_whitespace=False,
        allow_blank=False
    )
    email = serializers.EmailField(min_length=5, max_length=40, required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        """
        Configuration for the UserSerializer.
        """
        # include username so Djoser passes it into create_user()
        fields = ("id", "email", "username", "password")

    def validate_email(self, value: str) -> str:
        """
        Email validation
        """
        return validate_and_normalize_email(value=value, exists=True)
