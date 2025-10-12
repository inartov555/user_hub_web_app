"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


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
