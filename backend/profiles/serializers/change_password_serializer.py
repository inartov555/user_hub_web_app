"""
Django REST Framework (DRF) serializer that changes the password.
"""

from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """
    Django REST Framework (DRF) serializer that changes the password.
    """
    password = serializers.CharField(write_only=True, trim_whitespace=False, allow_blank=False)
