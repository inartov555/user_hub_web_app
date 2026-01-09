"""
This defines a model named Profile - an extension of Django's built-in User data.
Each user has exactly one profile.
"""

import os
from uuid import uuid4

from django.conf import settings
from django.db import models


def avatar_upload_path(instance: "Profile", filename: str) -> str:
    """
    Where user avatars are stored:
      media/avatars/u_<user_id>/<uuid>.<ext>
    """
    _, ext = os.path.splitext(filename)
    ext = (ext or ".jpg").lower()
    return f"avatars/user_{instance.user.id}/{uuid4()}{ext}"


class Profile(models.Model):
    """
    This defines a model named Profile - an extension of Django's built-in User data.
    Each user has exactly one profile.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Profile({self.user.user_id})"
