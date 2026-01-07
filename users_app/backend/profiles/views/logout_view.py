"""profiles/views/logout_view.py

JWTs are stateless, so there is no server-side "session" to destroy.

What we *can* invalidate is the client's ability to extend the session by
blacklisting the current **refresh token** (SimpleJWT blacklist app).

This endpoint is intentionally idempotent: calling it multiple times with the
same (or even invalid/expired) token returns 204.
"""

from django.conf import settings
from django.db import IntegrityError

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    """Invalidate the current session by blacklisting a refresh token.

    POST body:
      {"refresh": "<refresh-jwt>"}

    Returns:
      204 No Content (idempotent)
      400 if no refresh token is provided
    """

    # Allow logout even if the access token already expired; possession of the
    # refresh token is sufficient.
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh)

            # If the caller is authenticated, ensure they are only able to
            # blacklist their own refresh token.
            if request.user and request.user.is_authenticated:
                user_id_claim = settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id")
                token_user_id = token.get(user_id_claim)
                if str(token_user_id) != str(request.user.pk):
                    return Response(
                        {"detail": "Refresh token does not belong to the current user."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Blacklist the token (SimpleJWT blacklist app).
            try:
                token.blacklist()
            except AttributeError:
                # Blacklist app not installed; fall through to 204.
                pass
            except IntegrityError:
                # Already blacklisted (unique constraint) or race.
                pass

        except TokenError:
            # Invalid/expired token: keep logout idempotent.
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
