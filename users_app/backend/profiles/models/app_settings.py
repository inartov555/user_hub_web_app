"""
Dynamic App settings which can be set via web site UI
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from django.conf import settings
from django.db import models


JWT_RENEW_AT_SECONDS_KEY = "JWT_RENEW_AT_SECONDS"
IDLE_TIMEOUT_SECONDS_KEY = "IDLE_TIMEOUT_SECONDS"
ACCESS_TOKEN_LIFETIME_KEY = "ACCESS_TOKEN_LIFETIME"
ROTATE_REFRESH_TOKENS_KEY = "ROTATE_REFRESH_TOKENS"


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


@dataclass(frozen=True)
class EffectiveAuthSettings:
    """
    Effective app settings
    """
    jwt_renew_at_seconds: int
    idle_timeout_seconds: int
    access_token_lifetime_seconds: int
    rotate_refresh_tokens: bool

    def as_dict(self) -> Dict[str, Any]:
        """
        Get settings in the dictionary format
        """
        return {
            JWT_RENEW_AT_SECONDS_KEY: self.jwt_renew_at_seconds,
            IDLE_TIMEOUT_SECONDS_KEY: self.idle_timeout_seconds,
            ACCESS_TOKEN_LIFETIME_KEY: self.access_token_lifetime_seconds,
            ROTATE_REFRESH_TOKENS_KEY: self.rotate_refresh_tokens,
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

    def _bool_or(default: bool, maybe: str | None) -> bool:
        if maybe is None:
            return default
        s = str(maybe).strip().lower()
        if s in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "f", "no", "n", "off"}:
            return False
        # as a last resort, try int-like strings
        try:
            return bool(int(s))
        except ValueError:
            return default

    # fallbacks from core.settings
    default_renew = int(getattr(settings, JWT_RENEW_AT_SECONDS_KEY, 1200))
    default_idle = int(getattr(settings, IDLE_TIMEOUT_SECONDS_KEY, 900))
    # ACCESS_TOKEN_LIFETIME_KEY is a timedelta in core.settings
    default_access_td = getattr(settings, ACCESS_TOKEN_LIFETIME_KEY)
    default_access = int(default_access_td.total_seconds() if default_access_td else 1800)
    default_is_token_rotate = bool(getattr(settings, ROTATE_REFRESH_TOKENS_KEY))

    renew = _int_or(default_renew, AppSetting.get_value(JWT_RENEW_AT_SECONDS_KEY))
    idle  = _int_or(default_idle,  AppSetting.get_value(IDLE_TIMEOUT_SECONDS_KEY))
    access = _int_or(default_access, AppSetting.get_value(ACCESS_TOKEN_LIFETIME_KEY))
    rotate = _bool_or(default_is_token_rotate, AppSetting.get_value(ROTATE_REFRESH_TOKENS_KEY))

    return EffectiveAuthSettings(
        jwt_renew_at_seconds=max(0, renew),
        idle_timeout_seconds=max(1, idle),
        access_token_lifetime_seconds=max(1, access),
        rotate_refresh_tokens=rotate,
    )
