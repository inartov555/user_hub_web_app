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


class OnlineUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        return User.objects.filter(profile__last_activity__gte=cutoff).order_by("-profile__last_activity")
