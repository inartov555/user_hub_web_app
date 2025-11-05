"""
Custom password reset email serializer with strict email validation.
"""

from djoser.serializers import SendEmailResetSerializer
from rest_framework import serializers

from profiles.validators import validate_and_normalize_email


class CustomPasswordResetSerializer(SendEmailResetSerializer):
    """
    Custom password reset email serializer with strict email validation.
    """
    password = serializers.CharField(
        min_length=8, max_length=40, write_only=True, required=True, trim_whitespace=False,
        allow_blank=False
    )

    def validate_email(self, value: str) -> str:
        """
        Email validation
        """
        return validate_and_normalize_email(value=value, exists=False)

    def create(self, validated_data):
        # Not used
        return validated_data

    def update(self, instance, validated_data):
        # Not used
        raise NotImplementedError("Update is not supported for this serializer.")
