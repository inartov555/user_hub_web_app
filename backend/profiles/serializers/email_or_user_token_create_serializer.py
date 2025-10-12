from djoser.serializers import TokenCreateSerializer as BaseTokenCreateSerializer

class EmailOrUsernameTokenCreateSerializer(BaseTokenCreateSerializer):
    """
    Accepts either {"email","password"} or {"username","password"}.
    """
    def validate(self, attrs):
        data = dict(getattr(self, "initial_data", {}) or {})
        login = (data.get("email") or data.get("username") or "").strip()
        if login:
            # Inject into the field Djoser expects (self.username_field)
            attrs[self.username_field] = login
            if "password" in data:
                attrs["password"] = data["password"]
        return super().validate(attrs)
