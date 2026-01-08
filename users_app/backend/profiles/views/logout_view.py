from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class LogoutView(APIView):
    """
    Invalidate the current access token by blacklisting its JTI.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Read the raw access token from Authorization header
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.lower().startswith("bearer "):
            raise ValidationError({"details": "No token found"})

        raw_access = auth.split(" ", 1)[1].strip()
        if not raw_access:
            raise ValidationError({"details": "No token found"})

        token = AccessToken(raw_access)  # validates signature + exp
        jti = token.get("jti")
        exp = token.get("exp")
        user_id = token.get("user_id") or token.get("sub")

        if not (jti and exp and user_id):
            raise ValidationError({"details": "Invalid token"})

        User = get_user_model()
        user = User.objects.get(pk=user_id)

        expires_at = timezone.datetime.fromtimestamp(int(exp), tz=timezone.utc)

        outstanding, _ = OutstandingToken.objects.get_or_create(
            jti=jti,
            defaults={
                "user": user,
                "token": raw_access,
                "expires_at": expires_at,
            },
        )
        BlacklistedToken.objects.get_or_create(token=outstanding)

        return Response(status=204)
