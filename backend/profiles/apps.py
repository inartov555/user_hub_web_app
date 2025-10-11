"""
App configuration
"""

from django.apps import AppConfig


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
        from . import signals  # pylint: disable=import-outside-toplevel, unused-import
