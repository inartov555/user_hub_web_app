"""
Django REST Framework (DRF) serializer that changes the password.
"""

from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """
    Django REST Framework (DRF) serializer that changes the password.
    """
    password = serializers.CharField(write_only=True, trim_whitespace=False, allow_blank=False)

    def create(self, validated_data):
        """
        Not used for write-once actions, but required to satisfy abstract methods.
        """
        return validated_data

    def update(self, instance, validated_data):
        """
        Not used in this serializer; password change is handled in the view.
        """
        return instance
