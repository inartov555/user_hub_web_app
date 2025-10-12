"""
Custom user model and manager using email as the username.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Provides factory methods to create regular users and superusers while
    ensuring email normalization and secure password hashing.
    """
    def create_user(self, email, password=None, **extra):
        """
        Create and save a regular user with the given email and password.

        - Normalizes the email using Django's built-in normalization.
        - Hashes the provided password before saving.
        - Accepts additional keyword arguments for extra model fields.

        Args:
            email (str): The user's email address (required; used as username).
            password (str | None): The user's raw password. If None, the user
                will need to set a password later.
            **extra: Additional fields to set on the user instance.

        Raises:
            ValueError: If `email` is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra):
        """
        Create and save a superuser with the given email and password.

        Ensures the flags required for admin access are set:
        - is_staff = True (grants access to Django admin)
        - is_superuser = True (grants all permissions)

        Args:
            email (str): The superuser's email address.
            password (str | None): The raw password.
            **extra: Additional fields to set on the user instance.

        Returns:
            User: The created superuser instance.
        """
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Application's custom user model using email as the username field.

    Inherits:
        - AbstractBaseUser: Provides core authentication fields and password
          management (password hash, last_login, etc.).
        - PermissionsMixin: Adds Django's permission and group relationships
          plus the `is_superuser` flag.

    Fields:
        email (EmailField): Unique identifier for login.
        is_active (BooleanField): Soft-delete/activation flag. Inactive users
            cannot authenticate.
        is_staff (BooleanField): Grants access to the Django admin site.

    Attributes:
        USERNAME_FIELD (str): Field used as the unique identifier for auth;
            here it's "email".
        REQUIRED_FIELDS (list[str]): Extra fields required when creating a
            superuser via createsuperuser. Kept empty since email is enough.

    Manager:
        objects (UserManager): Custom manager handling user and superuser
        creation with proper email normalization and password hashing.
    """
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()
