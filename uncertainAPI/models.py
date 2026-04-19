"""Django models for uncertainAPI."""

from __future__ import annotations

from loguru import logger
import uuid

from django.db import models
from django.utils import timezone

class ExtractionTask(models.Model):
    """Model for tracking extractor task execution.

    Used for background task scheduling and status tracking.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2048)
    schema_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Results
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    user_id = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        """Meta options."""

        db_table = "uncertainapi_extraction_tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["url"]),
        ]

    def __str__(self) -> str:
        """String representation."""
        return f"ExtractionTask({self.id}, {self.status}, {self.url})"

    def mark_running(self) -> None:
        """Mark task as running."""
        self.status = "running"
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])
        logger.info("task.marked_running", extra={"task_id": str(self.id)})

    def mark_completed(self, result: dict) -> None:
        """Mark task as completed.

        Args:
            result: Extraction result data.
        """
        self.status = "completed"
        self.result = result
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "result", "completed_at"])
        logger.info("task.marked_completed", extra={"task_id": str(self.id)})

    def mark_failed(self, error: str) -> None:
        """Mark task as failed.

        Args:
            error: Error message.
        """
        self.status = "failed"
        self.error = error
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "error", "completed_at"])
        logger.warning("task.marked_failed", extra={"task_id": str(self.id), "error": error})

class ExtractionSession(models.Model):
    """Model for storing extractor authentication sessions.

    Stores cookies, tokens, and other session data for reuse.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    url_pattern = models.CharField(max_length=1024, help_text="URL pattern for this session")

    # Session data (encrypted)
    session_data = models.JSONField(default=dict)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    user_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        """Meta options."""

        db_table = "uncertainapi_extraction_sessions"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        """String representation."""
        return f"ExtractionSession({self.name}, {self.url_pattern})"

    def is_expired(self) -> bool:
        """Check if session is expired.

        Returns:
            True if expired, False otherwise.
        """
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

