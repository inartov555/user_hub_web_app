"""
This module wires up a Django signal.
"""

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from .models.profile import Profile


user_mod = get_user_model()


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
    # Create after commit so we never run during migrations/flush/fixtures
    def _make():
        profile_model = apps.get_model("profiles", "Profile")
        profile_model.objects.get_or_create(user=instance)
    transaction.on_commit(_make)


def backfill_profiles(sender, app_config, **kwargs):  # pylint: disable=unused-argument
    """
    After migrations, ensure every user has a Profile.
    Only run when *this* app (profiles) finishes migrating.
    """
    if app_config.label not in {"auth", "profiles"}:
        return

    # Make sure the necessary tables exist before querying
    from django.db import connection  # pylint: disable=import-outside-toplevel
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
    if not {"auth_user", "profiles_profile"}.issubset(tables):
        return

    # Resolve models lazily
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    profile_model = apps.get_model("profiles", "Profile")

    # Create profiles only for users missing one
    missing_users = user_model.objects.filter(profile__isnull=True).only("id")
    # idempotent; safe to run multiple times
    profile_model.objects.bulk_create(
        [profile_model(user=u) for u in missing_users],
        ignore_conflicts=True,
    )
