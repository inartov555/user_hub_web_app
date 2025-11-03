"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from django.contrib.auth import get_user_model
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
        model = get_user_model()
        # is_staff: allow admin panel
        # is_superuser: all permissions, admin user
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "is_active",
                  "is_staff", "is_superuser"]
        read_only_fields = ["id", "date_joined"]

    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        email = getattr(obj, "email", "") or ""
        return email.split("@", 1)[0] if email else ""

        fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "is_active",
                  "is_staff", "is_superuser"]
        read_only_fields = ["id", "date_joined"]
