"""
On each request, it compares the `boot_id` value embedded in the validated JWT (added at
issue time) with the server's current boot ID.
If they differ—e.g., after a deploy or restart—the middleware returns a 401
so the client can refresh credentials.
"""

from django.http import JsonResponse
from django.utils import translation
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

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
    Middleware to enforce logout of JWT-authenticated users after a server "boot ID"
    change.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        # Pull raw Bearer token (if any)
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.lower().startswith("bearer "):
            raw = auth_header.split(None, 1)[1]

            # Validate token and compare boot ids
            try:
                token = self.jwt_auth.get_validated_token(raw)
                curr = get_boot_id()
                if token.payload.get("boot_id") != curr:
                    return JsonResponse(
                        {"detail": translation.gettext("Session expired due to server restart.")},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                request.auth = token
            except (InvalidToken, AuthenticationFailed):
                # Let the normal auth/permission handling reject it.
                pass

        # Anonymous or no/bad token - proceed (views/DRF will handle)
        return self.get_response(request)
