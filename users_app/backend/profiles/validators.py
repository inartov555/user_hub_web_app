"""
Validators
"""

from django.contrib.auth import get_user_model
from django.core.validators import validate_email as dj_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError


def validate_and_normalize_email(value: str, exists: bool = False) -> str:
    """
    Email validation

    Args:
        value (str): email to validate and normilize
        exists (bool): in some cases, we should not validate the email presence in database
                       to avoid giving any hint what emails are registered (security reasons)
    """
    if not value or not value.strip():
        raise ValidationError("This field may not be blank.")
    try:
        dj_validate_email(value)
    except DjangoValidationError as exc:
        raise ValidationError("Enter a valid email address.") from exc
    normalized = value.strip().lower()
    if exists:
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=normalized).exists():
            raise ValidationError("A user with this email already exists.")
    return normalized
