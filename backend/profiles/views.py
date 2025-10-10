from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import pandas as pd
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer, ProfileUpdateSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200

class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related("profile").all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]

class MeProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        return Profile.objects.select_related("user").get(user=self.request.user)

class ExcelUploadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided"}, status=400)
        df = pd.read_excel(file)
        created, updated = 0, 0
        for _, row in df.iterrows():
            email = str(row.get("email", "")).strip().lower()
            if not email:
                continue
            user, was_created = User.objects.get_or_create(email=email, defaults={
                "username": row.get("username") or email.split("@")[0],
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
            })
            if not was_created:
                for f in ["first_name", "last_name"]:
                    val = row.get(f)
                    if pd.notna(val):
                        setattr(user, f, val)
                if pd.notna(row.get("username")):
                    user.username = row.get("username")
                if pd.notna(row.get("is_active")):
                    user.is_active = bool(row.get("is_active"))
                user.save()
                updated += 1
            else:
                created += 1
            profile, _ = Profile.objects.get_or_create(user=user)
            if pd.notna(row.get("bio")):
                profile.bio = row.get("bio")
                profile.save()
        return Response({"created": created, "updated": updated})

class OnlineUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        return User.objects.filter(profile__last_activity__gte=cutoff).order_by("-profile__last_activity")
