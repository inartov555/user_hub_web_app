from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView, MeView, ChangePasswordView, UsersViewSet, import_profile_excel

router = DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")

urlpatterns = [
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("me/import-excel/", import_profile_excel, name="import_profile_excel"),
    path("", include(router.urls)),
]
