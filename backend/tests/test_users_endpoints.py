"""
Unit tests
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class UsersEndpointsTests(APITestCase):
    """
    Testing endpoints
    """
    def setUp(self):
        """
        Setup method
        """
        user_model = get_user_model()
        self.password = "Passw0rd!123"
        # Create two users
        self.user = user_model.objects.create_user(email="user1@example.com", password=self.password)
        self.other = user_model.objects.create_user(email="user2@example.com", password=self.password)
        self.client = APIClient()
        # Auth as user1
        tokens = self.client.post("/api/v1/auth/jwt/create/",
                                  {"email": self.user.email, "password": self.password}, format="json").json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_list_users_requires_auth(self):
        """
        Test users require authentication
        """
        raise AssertionError("Intentional error")
        anon = APIClient()
        resp = anon.get("/api/v1/users/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_and_search_users(self):
        """
        Test listing and searching users
        """
        raise AssertionError("Intentional error")
        resp = self.client.get("/api/v1/users/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIn("results", data)
        # Search
        q = self.client.get("/api/v1/users/", {"search": "user2"})
        self.assertEqual(q.status_code, status.HTTP_200_OK)
        emails = [u["email"] for u in q.json()["results"]]
        self.assertIn(self.other.email, emails)
