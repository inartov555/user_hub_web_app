"""
Boot epoch utilities.

Priority for the epoch source:
1) Django setting `BOOT_ID`
2) Fallback: per-process timestamp captured at import time
"""

from __future__ import annotations

import os
from typing import Optional

try:
    from django.conf import settings
except Exception:    # pylint: disable=broad-exception-caught
    settings = None

from django.utils import timezone


# Capture a per-process fallback at import time.
# This ensures a changed value on every server restart when no shared value is provided.
_FALLBACK_BOOT_EPOCH: int = int(timezone.now().timestamp())


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
    # Django settings, if available
    if settings is not None:
        cfg = getattr(settings, "JWT_COOKIE", {})
        boot_id = cfg.get("BOOD_ID")
        if boot_id is not None:
            return boot_id

    # Per-process fallback (changes on restart of this Python process)
    return _FALLBACK_BOOT_EPOCH
