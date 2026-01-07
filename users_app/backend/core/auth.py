"""
Blacklisting tokens
"""

import time

from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


BLACKLIST_PREFIX = "jwt:bl:"


class JWTAuthenticationWithDenylist(JWTAuthentication):
    """
    Blacklisting tokens
    """
    def get_validated_token(self, raw_token):
        """
        Get valid token and raise error if it's blacklisted
        """
        token = super().get_validated_token(raw_token)

        jti = token.get("jti")
        if jti and cache.get(f"{BLACKLIST_PREFIX}{jti}"):
            raise AuthenticationFailed("Token is blacklisted", code="token_not_valid")

        return token
