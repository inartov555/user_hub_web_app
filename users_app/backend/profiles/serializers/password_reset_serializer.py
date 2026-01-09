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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"] = serializers.EmailField(min_length=5, max_length=40, required=True)

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
