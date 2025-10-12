"""
This module wires up a Django signal.
"""

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from .models.profile import Profile


User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Every time a new User is created, a matching Profile row is created automatically.
    """
    if created:
        Profile.objects.create(user=instance)


def create_profile_on_user_create(sender, instance, created, **kwargs):
    """
    When a new user is created, ensure a matching Profile exists.
    """
    if not created:
        return
    Profile = apps.get_model("profiles", "Profile")
    Profile.objects.get_or_create(user=instance)


def backfill_profiles(sender, app_config, **kwargs):
    """
    After migrations, ensure every user has a Profile.
    Only run when *this* app (profiles) finishes migrating.
    """
    if app_config.label != "profiles":
        return

    # Resolve models lazily
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    Profile = apps.get_model("profiles", "Profile")

    # Create profiles only for users missing one
    missing = User.objects.filter(profile__isnull=True).only("id")
    Profile.objects.bulk_create([Profile(user=u) for u in missing])
