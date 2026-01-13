"""
DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
"""

from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils import translation
import pandas as pd
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from ..models.profile import Profile
from ..serializers.user_serializer import UserSerializer
from ..validators import validate_and_normalize_email


class ExcelUploadView(APIView):
    """
    DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
    """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser]
    serializer_class = UserSerializer
    user = get_user_model()

    def get_permissions(self) -> list[permissions.BasePermission]:
        """
        Getting permissions needed for requests
        """
        # if self.request.method == "GET":
        #    return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]

    def get(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=unused-argument
        """
        Ingest an Excel file and create or update users (and their profiles).

        Returns:
            Response
        """
        user_model = get_user_model()
        qs = (
            user_model.objects.all()
            .select_related()  # will bring one-to-one (like profile) if declared on User
            .order_by("id")
        )

        # Build rows with safe profile access
        rows = []
        # If Profile is not reachable as user.profile, adjust accessor below.
        # e.g. if Profile has FK user=OneToOne(User), Django default accessor is user.profile
        for u in qs:
            try:
                p: Profile = u.profile  # adjust if related_name is different
                bio = getattr(p, "bio", "")
            except Profile.DoesNotExist:
                bio = ""
            except AttributeError:
                bio = ""

            # Also, "is_active": bool(u.is_active),
            rows.append({
                "email": (u.email or "").strip().lower(),
                "username": u.username or "",
                "first_name": u.first_name or "",
                "last_name": u.last_name or "",
                "bio": bio or "",
            })

        # Create DataFrame and write to in-memory Excel
        df = pd.DataFrame(rows, columns=[
            "email", "username", "first_name", "last_name", "bio"
        ])
        buf = BytesIO()
        # Use openpyxl (installed alongside pandas in many stacks)
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="users")

        buf.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        filename = f"users_{ts}.xlsx"

        resp = HttpResponse(
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    def post(self, request, *args, **kwargs) -> Response:  # pylint: disable=unused-argument,too-many-locals,too-many-branches
        """
        Ingest an Excel file and create or update users (and their profiles).

        Returns:
            Response
        """
        user_model = get_user_model()
        file = request.FILES.get("file")
        if not file:
            raise ValidationError(
                {"file_input": translation.gettext("No file provided")}
            )
        df = pd.read_excel(file)
        created, updated, processed = 0, 0, 0
        for _, row in df.iterrows():
            # Some fields are located in the User model, and the rest of them in the Profile model
            user_updated = False
            profile_changed = False
            username_cell = row.get("username")
            email_cell = str(row.get("email", "")).strip().lower()
            first_name_cell = row.get("first_name")
            last_name_cell = row.get("last_name")
            is_active_cell = row.get("is_active")
            if not email_cell or not username_cell:
                continue
            validate_and_normalize_email(email_cell, exists=False)
            user, was_created = user_model.objects.get_or_create(email=email_cell, defaults={
                "username": row.get("username") or email_cell.split('@', maxsplit=1)[0],
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
                "is_active": row.get("is_active", True),
            })
            if not was_created:
                if pd.notna(username_cell) and user.username != username_cell:
                    user.username = username_cell
                    user_updated = True
                if pd.notna(first_name_cell) and user.first_name != first_name_cell:
                    user.first_name = first_name_cell
                    user_updated = True
                if pd.notna(last_name_cell) and user.last_name != last_name_cell:
                    user.last_name = last_name_cell
                    user_updated = True
                if pd.notna(is_active_cell) and user.is_active != is_active_cell:
                    user.is_active = bool(is_active_cell)
                    user_updated = True
                user.save()
            else:
                created += 1
            profile, _ = Profile.objects.get_or_create(user=user)
            bio_cell = row.get("bio")
            if pd.notna(bio_cell):
                if profile.bio != bio_cell:
                    profile.bio = bio_cell
                    profile_changed = True
            if profile_changed:
                profile.save()
            if not was_created and (user_updated or profile_changed):
                updated += 1
        processed = created + updated
        return Response({"created": created, "updated": updated, "processed": processed})
