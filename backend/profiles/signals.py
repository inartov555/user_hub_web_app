"""
This module wires up a Django signal.
"""

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.profile import Profile


User = get_user_model()


def _table_exists(name: str) -> bool:
    """
    Let's make sure that table exists before signal fires
    """
    with connection.cursor() as c:
        c.execute("SELECT to_regclass(%s);", [name])
        return c.fetchone()[0] is not None


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Every time a new User is created, a matching Profile row is created automatically.
    """
    if created:
        Profile.objects.create(user=instance)
