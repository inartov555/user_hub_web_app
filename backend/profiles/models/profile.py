"""
This defines a model named Profile - an extension of Django’s built-in User data.
Each user has exactly one profile.
"""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    This defines a model named Profile - an extension of Django’s built-in User data.
    Each user has exactly one profile.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    last_activity = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Profile({self.user.username})"
