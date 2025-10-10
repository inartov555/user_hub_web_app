import io
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
import pandas as pd

from .serializers import (
    SignupSerializer,
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
    UserListSerializer,
    UserDetailSerializer,
)

User = get_user_model()

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    def get_object(self):
        return self.request.user
    parser_classes = (MultiPartParser, FormParser)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    def get_object(self):
        return self.request.user

class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["username", "email", "first_name", "last_name", "city"]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        now = timezone.now()
        window = timedelta(seconds=int(request.query_params.get("window", 300)))
        online_threshold = now - window
        total = User.objects.count()
        online = User.objects.filter(last_seen__gte=online_threshold).count()
        return Response({"total_users": total, "online_users": online, "window_seconds": int(window.total_seconds())})

@api_view(["POST"])
def import_profile_excel(request):
    '''
    Accepts an uploaded .xlsx file and updates the current user's fields from the first row.
    Expected columns: email, first_name, last_name, phone, city
    '''
    file = request.FILES.get("file")
    if not file:
        return Response({"detail": "No file uploaded under 'file'."}, status=400)
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return Response({"detail": f"Failed to read Excel: {e}"}, status=400)
    if df.empty:
        return Response({"detail": "Excel file has no rows."}, status=400)
    row = df.iloc[0].to_dict()
    allowed = {k: v for k, v in row.items() if k in {"email", "first_name", "last_name", "phone", "city"}}
    for k, v in allowed.items():
        setattr(request.user, k, str(v) if pd.notna(v) else "")
    request.user.save()
    return Response({"detail": "Profile updated from Excel.", "applied": allowed})
