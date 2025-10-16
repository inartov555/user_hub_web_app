"""
Active user
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, generics

from ..serializers.user_serializer import UserSerializer


class OnlineUsersView(generics.ListAPIView):
    """
    Active user
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    user = get_user_model()

    def get_queryset(self):
        """
        Read-only DRF endpoint that returns the list of users who have been active in the last 5 minutes.
        """
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        return self.User.objects.filter(profile__last_activity__gte=cutoff).order_by("-profile__last_activity")
