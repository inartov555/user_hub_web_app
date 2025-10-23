"""
Idle-timeout middleware for Django session authentication.

This middleware enforces an inactivity window for authenticated users.
If the elapsed time since the last request exceeds ``IDLE_TIMEOUT_SECONDS``,
the user is logged out and the session is invalidated.
"""

import time

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth


IDLE_TIMEOUT_SECONDS = getattr(settings, "IDLE_TIMEOUT_SECONDS", 30 * 60)


class IdleTimeoutMiddleware(MiddlewareMixin):
    """
    Idle-timeout middleware for Django session authentication.

    This middleware enforces an inactivity window for authenticated users.
    If the elapsed time since the last request exceeds ``IDLE_TIMEOUT_SECONDS``,
    the user is logged out and the session is invalidated.
    """
    def process_request(self, request):
        """
        Enforce inactivity timeout for the current request.
        """
        if request.path.startswith("/api/"):
            return None
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer "):
            return None

        # if you truly need it for server-rendered pages using sessions, keep the rest:
        IDLE_TIMEOUT_SECONDS = getattr(settings, "IDLE_TIMEOUT_SECONDS", None)
        if not IDLE_TIMEOUT_SECONDS:
            return None

        last = request.session.get("last_activity_ts")
        now = int(time.time())
        request.session["last_activity_ts"] = now  # update on every request

        if last and now - last > IDLE_TIMEOUT_SECONDS:
            auth.logout(request)
            request.session.flush()
            # only apply to non-API pages (we already returned above for /api/)
            return None
        return None
