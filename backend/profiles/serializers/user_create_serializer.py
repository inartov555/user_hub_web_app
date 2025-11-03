"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from django.core.validators import validate_email as dj_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework.exceptions import ValidationError


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
        # Not blank
        if not value or not value.strip():
            raise ValidationError("This field may not be blank.")
        # Valid email format
        try:
            dj_validate_email(value)
        except DjangoValidationError:
            raise ValidationError("Enter a valid email address.")
        normalized = value.strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=normalized).exists():
            raise ValidationError("A user with this email already exists.")
        return normalized
