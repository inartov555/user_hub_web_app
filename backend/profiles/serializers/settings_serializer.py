"""
Settings serializer
"""

from rest_framework import serializers
from ..models.app_settings import (
    AppSetting,
    get_effective_auth_settings,
    JWT_RENEW_AT_SECONDS_KEY,
    IDLE_TIMEOUT_SECONDS_KEY,
    ACCESS_TOKEN_LIFETIME_KEY,
)


class SettingsSerializer(serializers.Serializer):
    """
    Settings serializer
    """
    JWT_RENEW_AT_SECONDS = serializers.IntegerField(min_value=0)
    IDLE_TIMEOUT_SECONDS = serializers.IntegerField(min_value=1)
    ACCESS_TOKEN_LIFETIME = serializers.IntegerField(min_value=1)

    def to_representation(self, instance):
        eff = get_effective_auth_settings()
        return eff.as_dict()

    def update(self, instance, validated_data):
        """
        Upsert overrides (store ONLY what admin set explicitly)
        """
        for key, db_key in [
            ("JWT_RENEW_AT_SECONDS", JWT_RENEW_AT_SECONDS_KEY),
            ("IDLE_TIMEOUT_SECONDS", IDLE_TIMEOUT_SECONDS_KEY),
            ("ACCESS_TOKEN_LIFETIME", ACCESS_TOKEN_LIFETIME_KEY),
        ]:
            AppSetting.objects.update_or_create(
                key=db_key, defaults={"value": str(validated_data[key])}
            )
        return validated_data

    def create(self, validated_data):
        return self.update(None, validated_data)
