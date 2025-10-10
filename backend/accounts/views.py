from rest_framework import generics, permissions, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer, AvatarSerializer, ExcelImportResultSerializer
from .utils import handle_excel_user_import

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AvatarUploadView(generics.UpdateAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

class UsersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.all().order_by('id')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(username__icontains=search)
        sort = self.request.query_params.getlist('sort')
        if sort:
            qs = qs.order_by(*sort)
        return qs

class ExcelImportView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'detail':'No file uploaded'}, status=400)
        result = handle_excel_user_import(f)
        ser = ExcelImportResultSerializer(result)
        return Response(ser.data)

class OnlineUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        return User.objects.filter(last_seen__gte=cutoff)
