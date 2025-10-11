"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    class Meta:
        """
        Configuration for the UserSerializer.
        """
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "is_active"]
        read_only_fields = ["id", "date_joined"]
