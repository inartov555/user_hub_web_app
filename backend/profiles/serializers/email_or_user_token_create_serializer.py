"""
Django REST Framework ModelSerializer for Django’s built-in User model.
It defines which user fields are exposed through your API and which of them are writable.
"""

from djoser.serializers import TokenCreateSerializer as BaseTokenCreateSerializer


class EmailOrUsernameTokenCreateSerializer(BaseTokenCreateSerializer):
    """
    Django REST Framework ModelSerializer for Django’s built-in User model.
    It defines which user fields are exposed through your API and which of them are writable.
    """
    def validate(self, attrs):
        """
        Taking email as username
        """
        data = dict(getattr(self, "initial_data", {}) or {})
        login = (data.get("email") or data.get("username") or "").strip()
        if login:
            # Inject into the field Djoser expects (self.username_field)
            attrs["username"] = login
            if "password" in data:
                attrs["password"] = data["password"]
        return super().validate(attrs)
