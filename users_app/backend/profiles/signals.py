"""
Profiles app signals and backfills.

- create_profile_on_user_create: creates a Profile when a new User is created
- backfill_profiles: bulk-creates missing profiles after migrations

Both functions are idempotent and safe to run multiple times.
"""

from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.db import connection, router, transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def _get_user_and_profile_models() -> tuple[type["User"], type["Profile"]]:
    """
    Resolve the AUTH_USER_MODEL and profiles.Profile lazily.
    """
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    profile_model = apps.get_model("profiles", "Profile")
    return user_model, profile_model


def create_profile_on_user_create(sender, instance, created, **kwargs) -> None:  # pylint: disable=unused-argument
    """
    Post-save hook to create a profile for newly created users.
    """
    if not created:
        return

    # avoid creating profile within an open transaction; wait until commit
    def _create() -> None:
        _, profile_model = _get_user_and_profile_models()
        profile_model.objects.get_or_create(user=instance)

    transaction.on_commit(_create)


def _table_exists(table_name: str) -> bool:
    with connection.cursor() as cursor:
        return table_name in connection.introspection.table_names(cursor)


@receiver(post_migrate)
def backfill_profiles(sender, app_config=None, using=None, **kwargs) -> None:
    """
    Only run after the 'profiles' app itself has been migrated
    """
    app_label = (sender.label if sender else (app_config.label if app_config else None))
    if app_label != "profiles":
        return

    _profile = apps.get_model("profiles", "Profile")
    user_model = apps.get_model("auth", "User")

    # Ensure the table exists before querying it
    if not _table_exists(_profile._meta.db_table):
        return

    db_alias = using or router.db_for_read(_profile)

    # Find users without a profile and backfill in bulk
    existing_user_ids = _profile.objects.using(db_alias).values_list("user_id", flat=True)
    missing_users = user_model.objects.using(db_alias).exclude(id__in=existing_user_ids)

    to_create = [_profile(user=u) for u in missing_users]
    if to_create:
        with transaction.atomic(using=db_alias):
            _profile.objects.using(db_alias).bulk_create(to_create, ignore_conflicts=True)
