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
