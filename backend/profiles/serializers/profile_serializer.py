"""
Django REST Framework (DRF) serializer that converts your Profile model instances
to/from JSON for the API.
"""

from rest_framework import serializers

from ..models.profile import Profile
from ..serializers.user_serializer import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """
    Django REST Framework (DRF) serializer that converts your Profile model instances
    to/from JSON for the API.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        """
        If you want to prevent clients from writing last_activity, mark it read-only.
        """
        model = Profile
        fields = ["user", "bio", "avatar", "last_activity"]
