"""
Django REST Framework pagination class that controls how list endpoints return results.
"""

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import pandas as pd
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

from .models.profile import Profile
from .serializers.profile_serializer import ProfileSerializer
from .serializers.profile_update_serializer import ProfileUpdateSerializer
from .serializers.user_serializer import UserSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """
    Django REST Framework pagination class that controls how list endpoints return results.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200
