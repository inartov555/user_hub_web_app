from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, AvatarUploadView, UsersListView, ExcelImportView, OnlineUsersView

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),

    path('users/me/', MeView.as_view(), name='me'),
    path('users/me/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),

    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/import-excel/', ExcelImportView.as_view(), name='users-import-excel'),

    path('stats/online-users/', OnlineUsersView.as_view(), name='online-users'),
]
