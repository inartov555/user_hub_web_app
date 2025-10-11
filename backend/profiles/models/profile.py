"""
This defines a model named Profile - an extension of Django’s built-in User data.
Each user has exactly one profile.
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    This defines a model named Profile - an extension of Django’s built-in User data.
    Each user has exactly one profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
