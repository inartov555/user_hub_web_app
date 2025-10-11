"""
DRF serializer used to update a user’s Profile together with a couple of fields
on the related User in one request.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models.profile import Profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    DRF serializer used to update a user’s Profile together with a couple of fields
    on the related User in one request.
    """
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)

    class Meta:
        model = Profile
        fields = ["bio", "avatar", "first_name", "last_name"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)
