"""
JWTs are stateless, so there is no server-side session to destroy.
"""

import time

from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


BLACKLIST_PREFIX = "jwt:bl:"


class LogoutView(APIView):
    """
    Invalidate the current session by blacklisting a refresh token.
    """
    # permission_classes = [IsAuthenticated]  # from rest_framework.permissions import IsAuthenticated
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Logging out
        """
        token = request.auth  # the validated JWT token object
        jti = token.get("jti")
        exp = token.get("exp")  # epoch seconds
        print("\n\n\n\n !!! LogoutView !!! \n\n\n\n")
        if jti and exp:
            ttl = max(0, int(exp) - int(time.time()))
            cache.set(f"{BLACKLIST_PREFIX}{jti}", 1, timeout=ttl)

        return Response(status=204)
