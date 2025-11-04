"""
DRF serializer used to update a user’s Profile together with a couple of fields
on the related User in one request.
"""

from rest_framework import serializers

from ..models.profile import Profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    DRF serializer used to update a user’s Profile together with a couple of fields
    on the related User in one request.
    """
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    locale = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        """
        Serializer configuration for the Profile update operation.
        """
        model = Profile
        fields = ["first_name", "last_name", "locale", "bio", "avatar"]

    def update(self, instance, validated_data):
        """
        Persist updates to the Profile and selected fields on the related User.

        Args:
            instance: The existing Profile instance to update.
            validated_data: Data already validated by DRF, potentially including a
                nested `user` dict produced by the `source="user.*"` mappings.

        Returns:
            The updated Profile instance.
        """
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)
