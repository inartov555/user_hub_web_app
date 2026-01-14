from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthenticatedReadOnlyOrAdminWrite(BasePermission):
    """
    GET/HEAD/OPTIONS: any authenticated user
    PUT/PATCH/DELETE: admin (is_staff) only
    """
    def has_permission(self, request, view):
        """
        Check permissions
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated)
        return bool(user and user.is_authenticated and user.is_staff)
