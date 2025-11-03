"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

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
        Email validation
        """
        return validate_and_normalize_email(value=value, exists=True)
