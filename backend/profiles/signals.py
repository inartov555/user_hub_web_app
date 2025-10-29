"""Profiles app signals and backfills.

- create_profile_on_user_create: creates a Profile when a new User is created
- backfill_profiles: bulk-creates missing profiles after migrations

Both functions are idempotent and safe to run multiple times.
"""

from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.db import transaction


def _get_user_and_profile_models():
    """
    Resolve the AUTH_USER_MODEL and profiles.Profile lazily.
    """
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    profile_model = apps.get_model("profiles", "Profile")
    return user_model, profile_model


def create_profile_on_user_create(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Post-save hook to create a profile for newly created users.
    """
    if not created:
        return

    # avoid creating profile within an open transaction; wait until commit
    def _create():
        _, profile_model = _get_user_and_profile_models()
        profile_model.objects.get_or_create(user=instance)

    transaction.on_commit(_create)


def backfill_profiles(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Post-migrate hook to ensure every user has a Profile.

    Runs once after migrations complete. Bulk-creates missing profiles.
    """
    user_model, profile_model = _get_user_and_profile_models()
    missing_users = user_model.objects.filter(profile__isnull=True).only("id")
    profile_model.objects.bulk_create(
        [profile_model(user=u) for u in missing_users],
        ignore_conflicts=True,
    )
