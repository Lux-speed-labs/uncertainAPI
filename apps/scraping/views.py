from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from datetime import datetime, timedelta

from apps.jobs.models import Job
from apps.jobs.tasks import execute_job
from .serializers import ScrapeRequestSerializer, ScrapeResponseSerializer


class ScrapeView(APIView):
    """
    Web scraping endpoint with automatic sync→async handoff.
    
    This endpoint demonstrates the sync→async pattern:
    1. Validates request synchronously
    2. Creates background job immediately
    3. Returns job ID and WebSocket URL for progress tracking
    4. Client can monitor progress via WebSocket or polling
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Scrape Website",
        description="Start a web scraping job with Playwright. Returns immediately with job ID for progress tracking.",
        request=ScrapeRequestSerializer,
        responses={
            201: ScrapeResponseSerializer,
            400: {"description": "Invalid request data"}
        }
    )
    def post(self, request):
        serializer = ScrapeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create job with scraping-specific configuration
        job = Job.objects.create(
            job_type='scrape_website',
            input_data=serializer.validated_data,
            created_by=request.user,
            estimated_completion=datetime.now() + timedelta(seconds=60)  # 1 minute estimate
        )
        
        # Start background scraping task
        task = execute_job.delay(str(job.id))
        job.celery_task_id = task.id
        job.save()
        
        # Return job information for client tracking
        response_data = {
            'job_id': job.id,
            'status': job.status,
            'estimated_completion': job.estimated_completion,
            'websocket_url': f'/ws/jobs/{job.id}/progress/'
        }
        
        return Response(
            ScrapeResponseSerializer(response_data).data,
            status=status.HTTP_201_CREATED
        )