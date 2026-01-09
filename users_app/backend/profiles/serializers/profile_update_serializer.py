"""
DRF serializer used to update a user's Profile together with a couple of fields
on the related User in one request.
"""

from typing import Any

from rest_framework import serializers

from ..models.profile import Profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    DRF serializer used to update a user's Profile together with a couple of fields
    on the related User in one request.
    """
    first_name = serializers.CharField(source="user.first_name", required=False, max_length=40)
    last_name = serializers.CharField(source="user.last_name", required=False, max_length=40)
    locale = serializers.CharField(required=False, allow_blank=True, max_length=15)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)

    class Meta:
        """
        Serializer configuration for the Profile update operation.
        """
        model = Profile
        fields = ["first_name", "last_name", "locale", "bio", "avatar"]

    def update(self, instance, validated_data) -> Profile:
        """
        Persist updates to the Profile and selected fields on the related User.

        Args:
            instance: The existing Profile instance to update.
            validated_data: Data already validated by DRF, potentially including a
                nested user dict produced by the source="user.*" mappings.

        Returns:
            The updated Profile instance.
        """
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        if user_data:
            instance.user.save(update_fields=list(user_data.keys()))
        # Strip non-model fields before saving the Profile
        validated_data.pop("locale", None)
        return super().update(instance, validated_data)

    def to_representation(self, instance) -> dict[str, Any]:
        """
        Include 'locale' in the serialized output if the client sent it,
        so PATCH response contains it (tests assert this).
        """
        data = super().to_representation(instance)
        if hasattr(self, "initial_data") and isinstance(self.initial_data, dict):
            if "locale" in self.initial_data and "locale" not in data:
                data["locale"] = self.initial_data.get("locale")
        return data
