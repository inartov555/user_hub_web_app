# profiles/boot.py
"""
Boot epoch utilities.

`get_boot_epoch()` returns an integer that identifies the current "boot" of the
application. Embed this value into JWTs at issue-time and compare it in
middleware to invalidate tokens after a restart/deploy.

Priority for the epoch source:
1) Django setting `BOOT_EPOCH`
2) Environment variable `BOOT_EPOCH`
3) Fallback: per-process timestamp captured at import time

Notes
-----
- For multi-worker deployments (uWSGI, gunicorn with multiple workers, ASGI
  workers, etc.), you should set BOOT_EPOCH via settings or environment so all
  processes share the same value. The fallback is per-process and will differ
  between workers.
- To force logouts on each deploy, bump BOOT_EPOCH (e.g., export a new value in
  your CI/CD or write the build timestamp).
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
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def get_boot_epoch() -> int:
    """
    Return the current boot epoch as an integer.

    Resolution is seconds since Unix epoch. Prefer configuring this via
    `settings.BOOT_EPOCH` or the environment variable `BOOT_EPOCH` so all
    workers share the same value. Falls back to a per-process timestamp that
    changes on interpreter restart.

    Examples
    --------
    In settings.py (recommended for consistent multi-worker behavior):

        import time
        BOOT_EPOCH = int(time.time())  # bump on each deploy, or set in CI

    Or set an environment variable before starting the app:

        export BOOT_EPOCH=$(date +%s)

    Returns
    -------
    int
        The boot epoch to embed in tokens and compare in middleware.
    """
    # 1) Django settings, if available
    if settings is not None:
        cfg = getattr(settings, "JWT_COOKIE", {})
        boot_id = cfg.get("BOOD_ID")
        epoch = _coerce_epoch(getattr(settings, "BOOT_EPOCH", None))
        if epoch is not None:
            return epoch

    # 2) Environment variable
    env_epoch = _coerce_epoch(os.getenv("BOOT_EPOCH"))
    if env_epoch is not None:
        return env_epoch

    # 3) Per-process fallback (changes on restart of this Python process)
    return _FALLBACK_BOOT_EPOCH
