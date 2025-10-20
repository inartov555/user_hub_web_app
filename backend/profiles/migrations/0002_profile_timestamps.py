"""
Profiles app migration: add timestamp fields to Profile.

This migration adds two timestamp columns to `profiles_profile`:

- `created_at`  — auto-populated when a row is first created.
- `updated_at`  — auto-updated on each save.

During migration, existing rows are backfilled with `timezone.now`
so the columns can be created without NULLs. After migration,
the fields behave as standard Django timestamp fields via
`auto_now_add` / `auto_now`.
"""

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    """
    Add `created_at` and `updated_at` fields to the Profile model.

    The migration uses a default only at migration time to backfill
    existing records, and does not preserve a database-level default.
    """

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        # Use a default *only during migration* so existing rows get a value.
        migrations.AddField(
            model_name="profile",
            name="created_at",
            field=models.DateTimeField(default=timezone.now, auto_now_add=True),
            preserve_default=False,  # default is not kept on the model
        ),
        migrations.AddField(
            model_name="profile",
            name="updated_at",
            field=models.DateTimeField(default=timezone.now, auto_now=True),
            preserve_default=False,
        ),
    ]
