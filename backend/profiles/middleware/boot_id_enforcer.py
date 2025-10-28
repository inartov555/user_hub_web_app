"""
This module integrates with Django REST Framework + SimpleJWT. On each request,
it compares the `boot_id` value embedded in the validated JWT (added at
issue time) with the server's current boot epoch (from `profiles.boot.get_boot_id`).
If they differ—e.g., after a deploy or restart—the middleware returns a 401
so the client can refresh credentials.

Expected behavior:
- Anonymous users are ignored (normal response continues).
- If no validated JWT is present on the request (e.g., session auth or unauthenticated),
  the request proceeds unmodified.
- When a JWT is present and its `boot_id` differs from the server's current
  epoch, a 401 JSON response is returned with a short explanation.
"""

from django.http import JsonResponse
from ..boot import get_boot_id


def boot_header(get_response):
    """
    Attach the current boot id to every HTTP response so the frontend
    can detect deploys/restarts without making a separate call.
    Header: X-Boot-Id: <int>
    """
    def middleware(request):
        response = get_response(request)
        try:
            response["X-Boot-Id"] = str(int(get_boot_id()))
        except (TypeError, ValueError):
            # Never break responses if boot reading fails
            pass
        return response
    return middleware


class BootIdEnforcerMiddleware:
    """
    Middleware to enforce logout of JWT-authenticated users after a server "boot epoch"
    change.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre-response check: only enforce if a validated SimpleJWT token is present.
        user = getattr(request, "user", None)
        token = getattr(request, "auth", None)  # SimpleJWT validated token (if any)

        if user is not None and getattr(user, "is_authenticated", False) and token is not None:
            try:
                current_boot = int(get_boot_id())
            except (TypeError, ValueError):
                # If boot id can't be read, do NOT hard-fail the request.
                current_boot = None

            if current_boot is not None:
                # Token may be an instance of AccessToken/RefreshToken or a dict-like object
                payload = getattr(token, "payload", None) or getattr(token, "payload", {}) or {}
                try:
                    token_boot = int(payload.get("boot_id"))
                except (TypeError, ValueError):
                    token_boot = None

                if token_boot is not None and token_boot != current_boot:
                    return JsonResponse(
                        {"detail": "Session expired due to server restart."},
                        status=401,
                    )

        # Call downstream view/middleware
        response = self.get_response(request)

        # Best-effort header with current boot id
        try:
            response["X-Boot-Id"] = str(int(get_boot_id()))
        except (TypeError, ValueError):
            # Never break responses if boot reading fails
            pass

        return response
