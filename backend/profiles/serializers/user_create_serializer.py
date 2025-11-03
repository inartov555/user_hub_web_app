"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from django.core.validators import validate_email as dj_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

from profiles.validators import validate_and_normalize_email


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    class Meta(BaseUserCreateSerializer.Meta):
        """
        Configuration for the UserSerializer.
        """
        # include username so Djoser passes it into create_user()
        fields = ("id", "email", "username", "password")

    def validate_email(self, value: str) -> str:
        """
        Validating email
        """
        return validate_and_normalize_email(value=value, exists=True)
