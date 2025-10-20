"""
Django REST Framework (DRF) serializer that converts your Profile model instances
to/from JSON for the API.
"""

from rest_framework import serializers

from ..models.profile import Profile
from ..serializers.user_serializer import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """
    Django REST Framework (DRF) serializer that converts your Profile model instances
    to/from JSON for the API.
    """
    user = UserSerializer(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        """
        If you want to prevent clients from writing last_activity, mark it read-only.
        """
        model = Profile
        fields = ["user", "bio", "avatar", "avatar_url", "updated_at", "last_activity"]

    def get_avatar_url(self, obj) -> str:
        """
        Gettting avatar URL
        """
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            url = obj.avatar.url
            # return absolute URL so the SPA can load it cross-origin if needed
            return request.build_absolute_uri(url) if request else url
        return None
