from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet, MeProfileView, ExcelUploadView, OnlineUsersView

router = DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("me/profile/", MeProfileView.as_view(), name="me-profile"),
    path("users/import-excel/", ExcelUploadView.as_view(), name="users-import-excel"),
    path("stats/online-users/", OnlineUsersView.as_view(), name="online-users"),
]
