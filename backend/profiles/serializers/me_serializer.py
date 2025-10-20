"""
Django REST Framework serializer for the authenticated user ("me") endpoint.

This serializer exposes core `User` fields along with a nested `profile`
object. It supports reading and partially updating both the `User` and
their related `Profile` in a single request. When updating, any fields
present under `profile` are applied to the user's `Profile` instance; if
a profile does not yet exist, it is created automatically.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models.profile import Profile
from ..serializers.profile_serializer import ProfileSerializer
# Note: This file assumes `get_user_model` and `ProfileSerializer` are available
# in the import path, as referenced below.


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for the currently authenticated user, including their Profile.

    Fields:
        - id, username, email, first_name, last_name: standard User fields.
        - profile: nested Profile representation handled by `ProfileSerializer`.

    Behavior:
        - Read: returns user fields plus nested profile.
        - Update (PATCH/PUT): updates user fields and *only* the provided
          profile fields (partial update). If a Profile does not exist yet
          for the user, it will be created during update.
    """
    profile = ProfileSerializer(read_only=False)

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "last_name"]

    def update(self, instance, validated_data):
        """
        Update the User and their nested Profile with the provided data.

        This method:
          1) Extracts nested `profile` data from `validated_data`.
          2) Updates the User via the base `ModelSerializer.update`.
          3) If `profile` data was provided, fetches or creates the user's
             Profile and applies only the provided fields (partial update).

        Args:
            instance: The User instance to update.
            validated_data: The already-validated data dict. May contain a
                nested "profile" key with partial profile fields.

        Returns:
            The updated User instance (the associated Profile is updated
            and saved as a side effect when profile data is present).
        """
        profile_data = validated_data.pop("profile", {})
        user = super().update(instance, validated_data)

        if profile_data:
            prof, _ = Profile.objects.get_or_create(user=user)
            # Apply only provided fields; omit absent keys (partial update).
            for k, v in profile_data.items():
                setattr(prof, k, v)
            prof.save()

        return user
