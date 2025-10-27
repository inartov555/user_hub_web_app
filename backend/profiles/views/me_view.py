"""
User "me" endpoint views.

Exposes a single DRF view that lets an authenticated user retrieve and update
their own profile via the `/me/` endpoint (or whichever route you map it to).
"""

from rest_framework import generics, permissions
from ..serializers.me_serializer import MeSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """
    User "me" endpoint views.

    Exposes a single DRF view that lets an authenticated user retrieve and update
    their own profile via the `/me/` endpoint (or whichever route you map it to).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        """
        Return the object to be retrieved/updated by this view.

        DRF calls this to determine which instance to serialize. By returning
        `self.request.user`, the endpoint always targets the authenticated user
        making the request.

        Returns:
            django.contrib.auth.models.AbstractUser: The authenticated user instance.
        """
        return self.request.user
