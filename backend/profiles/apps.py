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
        Importing signals registers signal receivers. It's imported here (not at module top)
        to avoid import-order issues and ensure models are loaded before connecting signals.
        """
        # Get models safely after apps are loaded
        app_label, model_name = settings.AUTH_USER_MODEL.split(".")
        _user = apps.get_model(app_label, model_name)
        from .signals import *  # pylint: disable=import-outside-toplevel, unused-import
        # Connect with stable dispatch_uids to prevent duplicate connections
        post_save.connect(
            create_profile_on_user_create,
            sender=_user,
            dispatch_uid="profiles.create_profile_on_user_create",
        )
        post_migrate.connect(
            backfill_profiles,
            dispatch_uid="profiles.backfill_profiles",
        )
