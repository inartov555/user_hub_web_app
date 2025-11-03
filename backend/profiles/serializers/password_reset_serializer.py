"""
Custom password reset email serializer with strict email validation.
"""

from django.core.validators import validate_email as dj_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from djoser.serializers import SendEmailResetSerializer

from profiles.validators import validate_and_normalize_email


class CustomPasswordResetSerializer(SendEmailResetSerializer):
    """
    Custom password reset email serializer with strict email validation.
    """
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
