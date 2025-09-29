from django.db import models
from django.contrib.auth.models import User
import uuid


class Job(models.Model):
    """
    Model for tracking background jobs with ETA and progress.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('retry', 'Retry'),
        ('failure', 'Failure'),
        ('success', 'Success'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    celery_task_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Job metadata
    job_type = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Progress tracking
    progress = models.PositiveIntegerField(default=0)  # 0-100
    current_step = models.CharField(max_length=255, blank=True)
    total_steps = models.PositiveIntegerField(default=1)
    
    # Timing information
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Input/Output data
    input_data = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['job_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Job {self.id} ({self.job_type}) - {self.status}"
    
    @property
    def is_completed(self):
        return self.status in ['success', 'failure', 'revoked']
    
    @property
    def is_running(self):
        return self.status in ['pending', 'started', 'retry']