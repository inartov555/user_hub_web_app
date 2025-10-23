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
        # Skip for anonymous users or for endpoints you want to ignore
        if not request.user.is_authenticated:
            return None

        now = int(time.time())
        last = request.session.get("last_activity_ts", now)
        request.session["last_activity_ts"] = now  # always update

        if now - last > IDLE_TIMEOUT_SECONDS:
            # Invalidate the session and logout the user
            auth.logout(request)
            request.session.flush()

            # For API requests, return 401 JSON; for normal pages, redirect if you prefer
            if request.path.startswith("/api/"):
                return JsonResponse(
                    {"detail": "Session expired due to inactivity."},
                    status=401
                )
            # For non-API, redirect:
            # from django.shortcuts import redirect  # pylint: disable=import-outside-toplevel
            # return redirect("login")

        return None
