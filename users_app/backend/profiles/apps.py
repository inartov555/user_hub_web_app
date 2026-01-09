"""
App configuration
"""
from django.apps import AppConfig, apps
from django.conf import settings
from django.db.models.signals import post_save, post_migrate


class ProfilesConfig(AppConfig):
    """
    App configuration
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"
    label = "profiles"  # keep label stable

    def ready(self) -> None:
        """
        Resolve the user model lazily/safely
        """
        app_label, model_name = settings.AUTH_USER_MODEL.split(".")
        user_model = apps.get_model(app_label, model_name)

        # Import the signals module so its functions exist
        from . import signals  # pylint: disable=import-outside-toplevel

        # Qualify the callables with the module
        post_save.connect(
            signals.create_profile_on_user_create,
            sender=user_model,
            dispatch_uid="profiles.create_profile_on_user_create",
        )

        # Scope post_migrate to this app only
        post_migrate.connect(
            signals.backfill_profiles,
            sender=self,
            dispatch_uid="profiles.backfill_profiles",
        )
