"""
Boot epoch utilities.

Priority for the epoch source:
1) Django setting `BOOT_ID`
2) Fallback: per-process timestamp captured at import time
"""

from __future__ import annotations
from datetime import datetime, timezone

try:
    from django.conf import settings as DJANGO_SETTINGS
except Exception:  # pylint: disable=broad-exception-caught
    DJANGO_SETTINGS = None


# Capture a per-process fallback at import time.
# This ensures a changed value on every server restart when no shared value is provided.
_FALLBACK_BOOT_ID: int = datetime.now(timezone.utc).timestamp()


def get_boot_id() -> int:
    """
    Get the current boot id as an integer.

    Returns
        int, The boot id to embed in tokens and compare in middleware.
    """
    if DJANGO_SETTINGS is not None:
        # Prefer top-level BOOT_ID from core.settings
        boot_id = getattr(DJANGO_SETTINGS, "BOOT_ID", None)
        if boot_id is not None:
            try:
                return int(boot_id)
            except (TypeError, ValueError):
                pass
    return int(_FALLBACK_BOOT_ID)
