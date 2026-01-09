"""
Settings serializer
"""

from typing import Any

from rest_framework import serializers
from ..models.app_settings import (
    AppSetting,
    get_effective_auth_settings,
    JWT_RENEW_AT_SECONDS_KEY,
    IDLE_TIMEOUT_SECONDS_KEY,
    ACCESS_TOKEN_LIFETIME_KEY,
    ROTATE_REFRESH_TOKENS_KEY,
)


class SettingsSerializer(serializers.Serializer):
    """
    Settings serializer
    """
    JWT_RENEW_AT_SECONDS = serializers.IntegerField(min_value=0, max_value=9999)
    IDLE_TIMEOUT_SECONDS = serializers.IntegerField(min_value=60, max_value=9999)
    ACCESS_TOKEN_LIFETIME = serializers.IntegerField(min_value=60, max_value=9999)
    ROTATE_REFRESH_TOKENS = serializers.BooleanField()

    def to_representation(self, instance) -> dict[str, Any]:
        eff = get_effective_auth_settings()
        return eff.as_dict()

    def update(self, instance, validated_data) -> dict[str, Any]:
        """
        Upsert overrides (store ONLY what admin set explicitly)
        """
        for key, db_key in [
            (JWT_RENEW_AT_SECONDS_KEY, JWT_RENEW_AT_SECONDS_KEY),
            (IDLE_TIMEOUT_SECONDS_KEY, IDLE_TIMEOUT_SECONDS_KEY),
            (ACCESS_TOKEN_LIFETIME_KEY, ACCESS_TOKEN_LIFETIME_KEY),
            (ROTATE_REFRESH_TOKENS_KEY, ROTATE_REFRESH_TOKENS_KEY),
        ]:
            AppSetting.objects.update_or_create(
                key=db_key, defaults={"value": str(validated_data[key])}
            )
        return validated_data

    def create(self, validated_data) -> dict[str, Any]:
        return self.update(None, validated_data)
