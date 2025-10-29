"""
Dynamic App settings which can be set via web site UI
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from django.conf import settings
from django.db import models


class AppSetting(models.Model):
    """
    Simple key/value settings store.
    Keys are unique; values are stored as strings to keep it generic.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_setting"

    def __str__(self) -> str:
        return f"{self.key}={self.value}"

    @staticmethod
    def get_value(key: str) -> str | None:
        """
        Getting value
        """
        try:
            return AppSetting.objects.only("value").get(key=key).value
        except AppSetting.DoesNotExist:
            return None


# Keys we care about for this task
JWT_RENEW_AT_SECONDS_KEY = "JWT_RENEW_AT_SECONDS"
IDLE_TIMEOUT_SECONDS_KEY = "IDLE_TIMEOUT_SECONDS"
ACCESS_TOKEN_LIFETIME_KEY = "ACCESS_TOKEN_LIFETIME"  # seconds


@dataclass(frozen=True)
class EffectiveAuthSettings:
    """
    Effective app settings
    """
    jwt_renew_at_seconds: int
    idle_timeout_seconds: int
    access_token_lifetime_seconds: int

    def as_dict(self) -> Dict[str, Any]:
        """
        Get settings in the dictionary format
        """
        return {
            "JWT_RENEW_AT_SECONDS": self.jwt_renew_at_seconds,
            "IDLE_TIMEOUT_SECONDS": self.idle_timeout_seconds,
            "ACCESS_TOKEN_LIFETIME": self.access_token_lifetime_seconds,
        }


def get_effective_auth_settings() -> EffectiveAuthSettings:
    """
    Returns effective values:
      - DB override if present
      - otherwise fall back to core.settings.py defaults / env
    """
    def _int_or(default: int, maybe: str | None) -> int:
        try:
            return int(maybe) if maybe is not None else default
        except ValueError:
            return default

    # fallbacks from core.settings
    default_renew = int(getattr(settings, "JWT_RENEW_AT_SECONDS", 1200))
    default_idle = int(getattr(settings, "IDLE_TIMEOUT_SECONDS", 900))
    # ACCESS_TOKEN_LIFETIME is a timedelta in core.settings
    default_access_td = getattr(settings, "ACCESS_TOKEN_LIFETIME")
    default_access = int(default_access_td.total_seconds() if default_access_td else 1800)

    renew = _int_or(default_renew, AppSetting.get_value(JWT_RENEW_AT_SECONDS_KEY))
    idle  = _int_or(default_idle,  AppSetting.get_value(IDLE_TIMEOUT_SECONDS_KEY))
    access = _int_or(default_access, AppSetting.get_value(ACCESS_TOKEN_LIFETIME_KEY))

    return EffectiveAuthSettings(
        jwt_renew_at_seconds=max(0, renew),
        idle_timeout_seconds=max(1, idle),
        access_token_lifetime_seconds=max(1, access),
    )
