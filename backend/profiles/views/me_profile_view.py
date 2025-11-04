"""
DRF endpoint for the current logged-in user to view and update their own profile.
"""

from rest_framework import permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser

from ..models.profile import Profile
from ..serializers.profile_serializer import ProfileSerializer
from ..serializers.profile_update_serializer import ProfileUpdateSerializer


class MeProfileView(generics.RetrieveUpdateAPIView):
    """
    DRF endpoint for the current logged-in user to view and update their own profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        """
        Return the serializer appropriate for the current HTTP method.
        """
        if self.request.method in ["PUT", "PATCH"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        """
        Return the Profile for the authenticated user.
        Ensure it exists to avoid 500s when a user has no profile yet.
        """
        profile, _ = Profile.objects.select_related("user").get_or_create(user=self.request.user)
        # return Profile.objects.select_related("user").get(user=self.request.user)
        return profile
