"""
DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
"""

from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from django.contrib.auth import get_user_model
import pandas as pd
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..models.profile import Profile


class ExcelUploadView(APIView):
    """
    DRF endpoint that lets an admin upload an Excel file to bulk create/update users (and their profiles).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_permissions(self):
        """
        Getting permissions needed for requests
        """
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Ingest an Excel file and create or update users (and their profiles).

        Returns:
            Response
        """
        user_model = get_user_model()

        # Pull users + profiles efficiently
        # If Profile is OneToOne, select_related is fine; if not, use prefetch.
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
                # If Profile may not exist yet, this won't crash thanks to try/except
                p: Profile = u.profile  # adjust if related_name is different
                bio = getattr(p, "bio", "")
            except Profile.DoesNotExist:
                bio = ""
            except AttributeError:
                bio = ""

            rows.append({
                "email": (u.email or "").strip().lower(),
                "username": u.username or "",
                "first_name": u.first_name or "",
                "last_name": u.last_name or "",
                "is_active": bool(u.is_active),
                "bio": bio or "",
            })

        # Create DataFrame and write to in-memory Excel
        df = pd.DataFrame(rows, columns=[
            "email", "username", "first_name", "last_name", "is_active", "bio"
        ])
        buf = BytesIO()
        # Use openpyxl (installed alongside pandas in many stacks). You can swap to xlsxwriter if you prefer.
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

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Ingest an Excel file and create or update users (and their profiles).

        Returns:
            Response
        """
        user_model = get_user_model()
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided"}, status=400)
        df = pd.read_excel(file)
        created, updated = 0, 0
        for _, row in df.iterrows():
            email = str(row.get("email", "")).strip().lower()
            if not email:
                continue
            user, was_created = user_model.objects.get_or_create(email=email, defaults={
                "username": row.get("username") or email.split('@', maxsplit=1)[0],
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
            })
            if not was_created:
                for f in ["first_name", "last_name"]:
                    val = row.get(f)
                    if pd.notna(val):
                        setattr(user, f, val)
                if pd.notna(row.get("username")):
                    user.username = row.get("username")
                if pd.notna(row.get("is_active")):
                    user.is_active = bool(row.get("is_active"))
                user.save()
                updated += 1
            else:
                created += 1
            profile, _ = Profile.objects.get_or_create(user=user)
            if pd.notna(row.get("bio")):
                profile.bio = row.get("bio")
                profile.save()
        return Response({"created": created, "updated": updated})
