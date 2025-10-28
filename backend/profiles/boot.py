"""
Boot epoch utilities.

Priority for the epoch source:
1) Django setting `BOOT_ID`
2) Fallback: per-process timestamp captured at import time
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

try:
    from django.conf import settings as DJANGO_SETTINGS
except Exception:  # pylint: disable=broad-exception-caught
    DJANGO_SETTINGS = None


# Capture a per-process fallback at import time.
# This ensures a changed value on every server restart when no shared value is provided.
_FALLBACK_BOOT_ID: int = datetime.now(timezone.utc).timestamp()


def _coerce_epoch(value: Optional[object]) -> Optional[int]:
    """
    Try to coerce a value to an int epoch; return None if not possible.
    Accepts strings like "1730112345" or ints.
    """
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_boot_epoch() -> int:
    """
    Get the current boot epoch as an integer.

    Returns
        int, The boot epoch to embed in tokens and compare in middleware.
    """
    if DJANGO_SETTINGS is not None:
        # Prefer top-level BOOT_ID from core.settings
        boot_id = getattr(DJANGO_SETTINGS, "BOOT_ID", None)
        if boot_id is None:
            # Back-compat: allow SIMPLE_JWT["BOOT_ID"]
            boot_id = (getattr(DJANGO_SETTINGS, "SIMPLE_JWT", {}) or {}).get("BOOT_ID")
        if boot_id is not None:
            try:
                return int(boot_id)
            except (TypeError, ValueError):
                pass
    return _FALLBACK_BOOT_ID
