"""
Migration module
"""
from django.db import migrations, models
from django.conf import settings

import profiles.models.profile  # ensures `avatar_upload_path` import path is resolvable (if used)

class Migration(migrations.Migration):
    """
    Migration class
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bio", models.TextField(blank=True)),
                ("avatar", models.ImageField(blank=True, null=True, upload_to=profiles.models.profile.avatar_upload_path)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_activity", models.DateTimeField(blank=True, null=True)),
                ("user", models.OneToOneField(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
    ]
