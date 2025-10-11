"""
This module wires up a Django signal.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.profile import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Every time a new User is created, a matching Profile row is created automatically.
    """
    if created:
        Profile.objects.create(user=instance)
