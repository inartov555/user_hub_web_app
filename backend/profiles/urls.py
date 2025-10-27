"""
This is the URL routing module for the profiles app (DRF + Django).
It exposes the app’s API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.excel_upload_view import ExcelUploadView
from .views.me_profile_view import MeProfileView
from .views.me_view import MeView
from .views.online_users_view import OnlineUsersView
from .views.users_view_set import UsersViewSet


router = DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MeView.as_view(), name="me"),
    path("me/profile/", MeProfileView.as_view(), name="me-profile"),
    path("import-excel/", ExcelUploadView.as_view(), name="users-import-excel"),
    path("stats/online-users/", OnlineUsersView.as_view(), name="online-users"),
]
