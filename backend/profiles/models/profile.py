"""
This defines a model named Profile - an extension of Django’s built-in User data.
Each user has exactly one profile.
"""

import os

from django.conf import settings
from django.db import models


def avatar_upload_path(instance: "Profile", filename: str) -> str:
    """
    Where user avatars are stored:
      media/avatars/u_<user_id>/<uuid>.<ext>
    """
    _, ext = os.path.splitext(filename)
    ext = (ext or ".jpg").lower()
    # Use user_id if available; fall back to 'anonymous'
    user_part = f"u_{instance.user_id}" if getattr(instance, "user_id", None) else "anonymous"
    return f"avatars/{user_part}/{uuid4().hex}{ext}"


class Profile(models.Model):
    """
    This defines a model named Profile - an extension of Django’s built-in User data.
    Each user has exactly one profile.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(blank=True)
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.user_id})"
