"""
Temporarily set SimpleJWT Access/Refresh lifetimes, then restore previous values.
Mirrors the existing try/finally blocks used in serializers.
"""

from contextlib import contextmanager
from datetime import timedelta
from typing import Iterator

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

@contextmanager
def temporary_token_lifetimes(access_seconds: int, refresh_seconds: int) -> Iterator[None]:
    """
    Temporarily set SimpleJWT Access/Refresh lifetimes, then restore previous values.
    Mirrors the existing try/finally blocks used in serializers.
    """
    prev_access, prev_refresh = AccessToken.lifetime, RefreshToken.lifetime
    try:
        AccessToken.lifetime = timedelta(seconds=access_seconds)
        RefreshToken.lifetime = timedelta(seconds=refresh_seconds)
        yield
    finally:
        AccessToken.lifetime = prev_access
        RefreshToken.lifetime = prev_refresh
