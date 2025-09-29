from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for Job model with comprehensive progress tracking.
    """
    
    class Meta:
        model = Job
        fields = [
            'id', 'status', 'job_type', 'created_at', 'updated_at',
            'progress', 'current_step', 'total_steps',
            'started_at', 'completed_at', 'estimated_completion',
            'input_data', 'result_data', 'error_message',
            'is_completed', 'is_running'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'started_at', 'completed_at',
            'is_completed', 'is_running'
        ]


class JobCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new jobs.
    """
    job_type = serializers.CharField(max_length=100)
    input_data = serializers.JSONField(default=dict)
    estimated_duration = serializers.IntegerField(required=False, help_text="Estimated duration in seconds")
    
    def validate_job_type(self, value):
        """
        Validate that the job type is supported.
        """
        supported_types = ['scrape_website', 'process_data', 'generate_report']
        if value not in supported_types:
            raise serializers.ValidationError(
                f"Unsupported job type. Supported types: {', '.join(supported_types)}"
            )
        return value