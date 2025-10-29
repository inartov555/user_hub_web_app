"""
Migration module for App Settings
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration class
    """
    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppSetting",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, auto_created=True)),
                ("key", models.CharField(max_length=100, unique=True)),
                ("value", models.CharField(max_length=200)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "app_setting"},
        ),
    ]
