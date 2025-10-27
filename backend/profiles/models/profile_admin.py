"""
This defines a model named ProfileAdmin - an extension of Django’s built-in User data.
Each user has exactly one profile.
"""

from django.contrib import admin
from django.utils.timezone import localtime

from ..models.profile import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    This defines a model named ProfileAdmin - an extension of Django’s built-in User data.
    Each user has exactly one profile.
    """
    # keep your existing list_display items, but ensure 'last_activity' is present
    list_display = (
        # ... your existing columns ...
        'last_activity',
    )

    # Add this method so 'last_activity' is valid for list_display
    def last_activity(self, obj):
        """
        Displays user's last_login as 'last activity'.
        Returns '-' if no value.
        """
        if getattr(obj, "user", None) and getattr(obj.user, "last_login", None):
            return localtime(obj.user.last_login)
        return "-"

    last_activity.short_description = "Last activity"
    last_activity.admin_order_field = "user__last_login"  # enables sorting by the related field
