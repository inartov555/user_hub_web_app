"""
Read-only DRF viewset that lets admins list and view Django users with pagination,
filtering, sorting, and search.
"""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from .standard_results_set_pagination import StandardResultsSetPagination
from ..serializers.user_serializer import UserSerializer


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only DRF viewset that lets admins list and view Django users with pagination,
    filtering, sorting, and search.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]

    def get_queryset(self):
        user_model = get_user_model()
        return user_model.objects.select_related("profile").order_by("id")
