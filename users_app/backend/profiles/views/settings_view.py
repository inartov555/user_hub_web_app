"""
Admin-only settings endpoint.
GET: effective values (DB override if present, else core.settings default)
PUT/PATCH: store overrides in DB (only affects NEW logins)
"""

from rest_framework import permissions, generics
from ..serializers.settings_serializer import SettingsSerializer


class SettingsView(generics.RetrieveUpdateAPIView):
    """
    Admin-only settings endpoint.
    GET: effective values (DB override if present, else core.settings default)
    PUT/PATCH: store overrides in DB (only affects NEW logins)
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SettingsSerializer

    def get_object(self):
        return {}
