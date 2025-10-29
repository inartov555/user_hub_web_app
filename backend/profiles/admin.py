"""
This is a Django admin module that registers the Profile model with the admin site
and configures how it’s displayed.
"""

from django.contrib import admin

from .models.profile import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Controls how the Profile model in the admin looks and is filtered in the list view.
    """
    list_display = ("user", "last_activity")
