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

def validate_and_normalize_username(
        value: str,
        exists: bool = False,
        exclude_user_id: int | None = None,
) -> str:
    """
    Username validation

    Args:
        value (str): username to validate/normalize.
        exists (bool): when True, ensure the username is not already taken.
        exclude_user_id (int): when checking uniqueness, ignore this user id.
    """
    if value is None or not str(value).strip():
        raise ValidationError("This field may not be blank.")

    normalized = str(value).strip()

    if exists:
        user_model = get_user_model()
        qs = user_model.objects.filter(username__iexact=normalized)
        if exclude_user_id is not None:
            qs = qs.exclude(id=exclude_user_id)
        if qs.exists():
            raise ValidationError("A user with this username already exists.")

    return normalized
