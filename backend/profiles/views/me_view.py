from rest_framework import generics, permissions
from ..serializers.me_serializer import MeSerializer

class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
