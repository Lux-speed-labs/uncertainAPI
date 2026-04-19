"""Initial migration for uncertainAPI models."""

from __future__ import annotations

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):
    """Initial migration."""

    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="ExtractionTask",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("url", models.URLField(max_length=2048)),
                ("schema_name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("result", models.JSONField(blank=True, null=True)),
                ("error", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user_id", models.CharField(blank=True, max_length=255, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "uncertainapi_extraction_tasks",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["status", "-created_at"],
                        name="uncertainap_status_idx",
                    ),
                    models.Index(fields=["url"], name="uncertainap_url_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ExtractionSession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "url_pattern",
                    models.CharField(
                        help_text="URL pattern for this session", max_length=1024
                    ),
                ),
                ("session_data", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("user_id", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "db_table": "uncertainapi_extraction_sessions",
                "ordering": ["-updated_at"],
            },
        ),
    ]

