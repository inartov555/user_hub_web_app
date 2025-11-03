"""
Custom password reset email serializer with strict email validation.
"""

from django.core.validators import validate_email as dj_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from djoser.serializers import SendEmailResetSerializer
from rest_framework.exceptions import ValidationError


class CustomPasswordResetSerializer(SendEmailResetSerializer):
    """
    Custom password reset email serializer with strict email validation.
    """
    def validate_email(self, value: str) -> str:  # pylint: disable=duplicate-code
        """
        Email validation
        """
        # It's not a fully duplicate, there's difference
        if not value or not value.strip():
            raise ValidationError("This field may not be blank.")
        try:
            dj_validate_email(value)
        except DjangoValidationError as exc:
            raise ValidationError("Enter a valid email address.") from exc
        # Do NOT reveal whether the email exists (avoid user enumeration).
        return value.strip().lower()

    def create(self, validated_data):
        # Not used
        return validated_data

    def update(self, instance, validated_data):
        # Not used
        raise NotImplementedError("Update is not supported for this serializer.")
