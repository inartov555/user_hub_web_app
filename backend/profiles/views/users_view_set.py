"""
Read-only DRF viewset that lets admins list and view Django users with pagination,
filtering, sorting, and search.
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


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only DRF viewset that lets admins list and view Django users with pagination,
    filtering, sorting, and search.
    """
    queryset = User.objects.select_related("profile").all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
