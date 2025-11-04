"""
Unit tests
"""

from django.test import SimpleTestCase
from django.urls import resolve

from profiles.views.runtime_aware_token_refresh_view import RuntimeAwareTokenRefreshView


class RefreshRouteTest(SimpleTestCase):
    """
    Test refresh route
    """
    def test_refresh_resolves_to_runtime_view(self):
        """
        Test if refresh resolves to runtime view
        """
        match = resolve("/api/v1/auth/jwt/refresh/")
        self.assertEqual(match.func.view_class, RuntimeAwareTokenRefreshView)
