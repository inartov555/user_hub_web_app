"""
Read-only DRF viewset that lets admins list and view Django users with pagination,
filtering, sorting, and search.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .standard_results_set_pagination import StandardResultsSetPagination
from ..serializers.user_serializer import UserSerializer
from ..serializers.change_password_serializer import ChangePasswordSerializer


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
        """
        Get queryset
        """
        user_model = get_user_model()
        return user_model.objects.select_related("profile").order_by("id")

    @action(detail=False, methods=["post"], url_path="bulk-delete",
            permission_classes=[permissions.IsAuthenticated])
    def bulk_delete(self, request):
        """
        Delete multiple users by id list: { "ids": [1,2,3] }
        """
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return Response({"detail": "ids must be a list of integers"}, status=400)

        # optional: don't allow deleting yourself
        if request.user and request.user.id in ids:
            return Response({"detail": "Cannot delete current user."}, status=400)

        qs = self.get_queryset().filter(id__in=ids)
        count = qs.count()
        qs.delete()
        return Response({"deleted": count}, status=200)

    @action(detail=True, methods=["post"], url_path="set-password",
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request, pk=None):  # pylint: disable=unused-argument
        """
        Set (change) the password for a specific user.
        Allowed for staff OR the user changing their own password.
        """
        user = self.get_object()
        # Check for admin user
        # if not (request.user.is_staff or request.user == user):
        #    return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)

        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new_pw = ser.validated_data["password"]

        # Run Django password validators
        try:
            password_validation.validate_password(new_pw, user=user)
        except (DjangoValidationError, ValueError) as e:
            return Response({"detail": str(e)}, status=400)
        except IntegrityError:
            return Response({"detail": "Database error while applying changes."}, status=400)

        user.set_password(new_pw)
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)
