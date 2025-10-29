"""
App configuratio
"""

from django.apps import AppConfig, apps
from django.conf import settings
from django.db.models.signals import post_save, post_migrate


class ProfilesConfig(AppConfig):
    """
    Custom config for the profiles app
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        """
        Wire up signals in a registry-safe way.
        """
        # Resolve the user model lazily to avoid early app loading issues
        app_label, model_name = settings.AUTH_USER_MODEL.split(".")
        _user = apps.get_model(app_label, model_name)

        # Import here to avoid side effects at import time
        from .signals import (  # pylint: disable=import-outside-toplevel
            create_profile_on_user_create,
            backfill_profiles,
        )

        # Connect with stable dispatch_uids to prevent duplicate connections
        post_save.connect(
            create_profile_on_user_create,
            sender=_user,
            dispatch_uid="profiles.create_profile_on_user_create",
        )
        # Defer backfill until migrations are done (fires once per app migration)
        post_migrate.connect(
            backfill_profiles,
            dispatch_uid="profiles.backfill_profiles",
        )
