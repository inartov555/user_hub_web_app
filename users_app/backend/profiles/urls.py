"""
This is the URL routing module for the profiles app (DRF + Django).
It exposes the app’s API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.excel_upload_view import ExcelUploadView
from .views.me_profile_view import MeProfileView
from .views.online_users_view import OnlineUsersView
from .views.users_view_set import UsersViewSet
from .views.logout_view import LogoutView
from .views.settings_view import SettingsView
from .views.runtime_auth_view import runtime_auth_config
from .views.runtime_aware_token_refresh_view import RuntimeAwareTokenRefreshView


router = DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("me/profile/", MeProfileView.as_view(), name="me-profile"),
    path("import-excel/", ExcelUploadView.as_view(), name="users-import-excel"),
    path("stats/online-users/", OnlineUsersView.as_view(), name="online-users"),
    path("system/settings/", SettingsView.as_view(), name="system-settings"),
    path("system/runtime-auth/", runtime_auth_config, name="runtime-auth-config"),
    path("auth/jwt/refresh/", RuntimeAwareTokenRefreshView.as_view(), name="token_refresh"),
    # path("auth/jwt/logout/", LogoutView.as_view(), name="jwt-logout"),
]
