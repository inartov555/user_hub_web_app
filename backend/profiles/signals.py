"""
This module wires up a Django signal.
"""

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.profile import Profile


user_mod = get_user_model()


@receiver(post_save, sender=user_mod)
def create_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Every time a new User is created, a matching Profile row is created automatically.
    """
    if created:
        Profile.objects.create(user=instance)


def create_profile_on_user_create(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    When a new user is created, ensure a matching Profile exists.
    """
    if not created:
        return
    _profile = apps.get_model("profiles", "Profile")
    _profile.objects.get_or_create(user=instance)


def backfill_profiles(sender, app_config, **kwargs):  # pylint: disable=unused-argument
    """
    After migrations, ensure every user has a Profile.
    Only run when *this* app (profiles) finishes migrating.
    """
    if app_config.label != "profiles":
        return

    # Resolve models lazily
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    _user = apps.get_model(app_label, model_name)
    _profile = apps.get_model("profiles", "Profile")

    # Create profiles only for users missing one
    missing = _user.objects.filter(profile__isnull=True).only("id")
    _profile.objects.bulk_create([_profile(user=u) for u in missing])
