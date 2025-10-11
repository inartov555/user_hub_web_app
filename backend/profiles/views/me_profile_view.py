"""
DRF endpoint for the current logged-in user to view and update their own profile.
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


class MeProfileView(generics.RetrieveUpdateAPIView):
    """
    DRF endpoint for the current logged-in user to view and update their own profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        return Profile.objects.select_related("user").get(user=self.request.user)
