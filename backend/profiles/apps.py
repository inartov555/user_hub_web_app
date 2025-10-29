"""
App configuration
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
        # Resolve user model lazily
        app_label, model_name = settings.AUTH_USER_MODEL.split(".")
        _user = apps.get_model(app_label, model_name)

        from . import signals   # pylint: disable=import-outside-toplevel

        post_save.connect(
            create_profile_on_user_create,
            sender=_user,
            dispatch_uid="profiles.create_profile_on_user_create",
        )

        # IMPORTANT: only run backfill after *this* app’s migrations
        post_migrate.connect(
            backfill_profiles,
            sender=self,  # <- scope to profiles app
            dispatch_uid="profiles.backfill_profiles",
        )
