"""
Helper to get effective settings
"""

from __future__ import annotations

from django.conf import settings
from django.utils.timezone import now
from typing import Dict, Any

from profiles.models import AppSetting, JWT_RENEW_AT_SECONDS_KEY, \
    IDLE_TIMEOUT_SECONDS_KEY, ACCESS_TOKEN_LIFETIME_KEY, ROTATE_REFRESH_TOKENS_KEY


_KEYS = (
    ACCESS_TOKEN_LIFETIME_KEY,
    JWT_RENEW_AT_SECONDS_KEY,
    IDLE_TIMEOUT_SECONDS_KEY,
    ROTATE_REFRESH_TOKENS_KEY,
)


def _get_db_map() -> Dict[str, str]:
    """
    Returns a {key: value} map for the keys we care about, from DB if available.
    Missing keys are simply absent.
    """
    if AppSetting is None:
        return {}
    rows = AppSetting.objects.filter(key__in=_KEYS).values_list("key", "value")
    return {k: v for (k, v) in rows if v is not None}


def _as_int(db: Dict[str, str], key: str, default: int) -> int:
    if key in db:
        try:
            return int(db[key])
        except Exception:
            return default
    # fall back to Django settings if present; otherwise given default
    if hasattr(settings, key):
        try:
            v = getattr(settings, key)
            return int(v)
        except Exception:
            pass
    # SIMPLE_JWT allows a timedelta for ACCESS_TOKEN_LIFETIME_KEY
    if key == ACCESS_TOKEN_LIFETIME_KEY and hasattr(settings, "SIMPLE_JWT"):
        sj = settings.SIMPLE_JWT
        v = sj.get(ACCESS_TOKEN_LIFETIME_KEY)
        if v is not None:
            try:
                # timedelta -> seconds
                return int(getattr(v, "total_seconds", lambda: int(v))())
            except Exception:
                pass
    return default


def _as_bool(db: Dict[str, str], key: str, default: bool) -> bool:
    if key in db:
        return str(db[key]).strip().lower() in ("1", "true", "yes", "on")
    if hasattr(settings, key):
        v = getattr(settings, key)
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("1", "true", "yes", "on")
    if hasattr(settings, "SIMPLE_JWT") and key == ROTATE_REFRESH_TOKENS_KEY:
        sj = settings.SIMPLE_JWT
        v = sj.get(ROTATE_REFRESH_TOKENS_KEY)
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("1", "true", "yes", "on")
    return default


def get_effective_runtime_auth() -> Dict[str, Any]:
    """
    DB values take precedence; fallback to settings / SIMPLE_JWT.
    Returns ints for *_SECONDS and bool for ROTATE_REFRESH_TOKENS_KEY.
    """
    db = _get_db_map()
    return {
        ACCESS_TOKEN_LIFETIME_KEY: _as_int(db, ACCESS_TOKEN_LIFETIME_KEY, 300),  # seconds
        JWT_RENEW_AT_SECONDS_KEY: _as_int(db, JWT_RENEW_AT_SECONDS_KEY, 0),
        IDLE_TIMEOUT_SECONDS_KEY: _as_int(db, IDLE_TIMEOUT_SECONDS_KEY, 0),
        ROTATE_REFRESH_TOKENS_KEY: _as_bool(db, ROTATE_REFRESH_TOKENS_KEY, True),
        "retrieved_at": now(),
    }
