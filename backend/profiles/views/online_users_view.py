"""
Active user
"""

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import pandas as pd
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

from .models.profile import Profile
from .serializers.profile_serializer import ProfileSerializer
from .serializers.profile_update_serializer import ProfileUpdateSerializer
from .serializers.user_serializer import UserSerializer


class OnlineUsersView(generics.ListAPIView):
    """
    Active user
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Read-only DRF endpoint that returns the list of users who have been active in the last 5 minutes.
        """
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        return User.objects.filter(profile__last_activity__gte=cutoff).order_by("-profile__last_activity")
