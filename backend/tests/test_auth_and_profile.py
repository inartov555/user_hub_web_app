"""
Unit tests
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class AuthAndProfileTests(APITestCase):
    """
    Authentication and profile related tests
    """
    def setUp(self):
        """
        Setup method
        """
        self.user_model = get_user_model()
        self.password = "Passw0rd!123"
        self.user = self.user_model.objects.create_user(username="user",
                                                        email="user@example.com",
                                                        password=self.password)
        self.client = APIClient()

    def test_jwt_create_and_refresh(self):
        """
        Login and refresh token it -> success
        """
        # Obtain access/refresh via Djoser
        resp = self.client.post("/api/v1/auth/jwt/create/",
                                {"username": self.user.username, "password": self.password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.content)
        tokens = resp.json()
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

        # Use access on a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        me = self.client.get("/api/v1/me/profile/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)

        # Refresh should work (endpoint is overridden in app urls)
        refresh = self.client.post("/api/v1/auth/jwt/refresh/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh.json())

    def test_me_profile_update(self):
        """
        Test my profile update
        """
        # Authenticate
        resp = self.client.post("/api/v1/auth/jwt/create/",
                                {"username": self.user.username, "password": self.password}, format="json")
        access = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Read current profile
        me = self.client.get("/api/v1/me/profile/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        # current = me.json()
        # Update some editable fields
        payload = {"first_name": "Ada", "last_name": "Lovelace", "locale": "en_US"}
        upd = self.client.patch("/api/v1/me/profile/", payload, format="json")
        self.assertEqual(upd.status_code, status.HTTP_200_OK, upd.content)
        out = upd.json()
        for k, v in payload.items():
            self.assertEqual(out[k], v)
