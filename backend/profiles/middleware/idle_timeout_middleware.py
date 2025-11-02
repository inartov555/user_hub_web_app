"""
Idle-timeout middleware for Django session authentication.

This enforces an inactivity window for authenticated users.
It uses the *effective* app settings (DB override or defaults).
"""

import time

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import translation
from django.contrib import auth
from django.shortcuts import redirect
from rest_framework import status

from ..models.app_settings import get_effective_auth_settings


class IdleTimeoutMiddleware(MiddlewareMixin):
    """
    If elapsed time since the last request exceeds idle timeout,
    logout the user and invalidate the session.
    """

    SESSION_KEY = "last_request_ts"

    def process_request(self, request):
        """
        Enforce inactivity timeout for the current request.
        """
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return None

        # NEW: pull the current effective value each request (cheap; or cache if you like)
        idle_timeout_seconds = get_effective_auth_settings().idle_timeout_seconds

        now = int(time.time())
        last = request.session.get(self.SESSION_KEY, now)
        request.session[self.SESSION_KEY] = now
        request.session.modified = True

        if now - last > idle_timeout_seconds:
            auth.logout(request)
            request.session.flush()
            if request.path.startswith("/api/"):
                return JsonResponse(
                {"detail": translation.gettext("Session expired due to inactivity.")},
                status=status.HTTP_401_UNAUTHORIZED)
            return redirect("/login")

        return None
