"""
DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
"""

from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils import translation
import pandas as pd
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..models.profile import Profile
from ..serializers.user_serializer import UserSerializer


class ExcelUploadView(APIView):
    """
    DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    serializer_class = UserSerializer
    user = get_user_model()

    def get_permissions(self):
        """
        Getting permissions needed for requests
        """
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
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
        # If your Profile is not reachable as user.profile, adjust accessor below.
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
            content_type="multipart/form-data",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Ingest an Excel file and create or update users (and their profiles).

        Returns:
            Response
        """
        user_model = get_user_model()
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": translation.gettext("No file provided")},
                            status=status.HTTP_400_BAD_REQUEST)
        df = pd.read_excel(file)
        created, updated, processed = 0, 0, 0
        for _, row in df.iterrows():
            # Some fields are located in the User model, and the rest of them in the Profile model
            user_updated = False
            profile_changed = False
            email = str(row.get("email", "")).strip().lower()
            if not email:
                continue
            user, was_created = user_model.objects.get_or_create(email=email, defaults={
                "username": row.get("username") or email.split('@', maxsplit=1)[0],
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
            })
            if not was_created:
                username_cell = row.get("username")
                first_name_cell = row.get("first_name")
                last_name_cell = row.get("last_name")
                is_active_cell = row.get("is_active")
                for f in ["first_name", "last_name"]:
                    val = row.get(f)
                    if pd.notna(val):
                        setattr(user, f, val)
                if pd.notna(username_cell) and user.username != username_cell:
                    user.username = username
                    user_updated = True
                    print(f"\n\n username_cell = '{username_cell}' \n\n")
                if pd.notna(first_name_cell) and user.first_name != first_name_cell:
                    user.first_name = first_name
                    user_updated = True
                    print(f"\n\n first_name_cell = '{first_name_cell}' \n\n")
                if pd.notna(last_name_cell) and user.last_name != last_name_cell:
                    user.last_name = last_name
                    user_updated = True
                    print(f"\n\n last_name_cell = '{last_name_cell}' \n\n")
                if pd.notna(is_active_cell) and user.is_active != is_active_cell:
                    user.is_active = bool(row.get("is_active"))
                    user_updated = True
                    print(f"\n\n is_active_cell = '{is_active_cell}' \n\n")
                user.save()
            else:
                created += 1
            profile, _ = Profile.objects.get_or_create(user=user)
            bio_cell = row.get("bio")
            if pd.notna(bio_cell):
                if profile.bio != bio_cell:
                    print(f"\n\n bio_cell = '{bio_cell}' \n profile.bio = '{profile.bio}' \n\n")
                    profile.bio = bio_cell
                    profile_changed = True
            if profile_changed:
                profile.save()
            if not was_created and (user_updated or profile_changed):
                updated += 1
        processed = created + updated
        return Response({"created": created, "updated": updated, "processed": processed})
