from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from celery import current_app

from .models import Job
from .serializers import JobSerializer, JobCreateSerializer
from .tasks import execute_job


class JobListCreateView(generics.ListCreateAPIView):
    """
    List all jobs or create a new job with automatic sync→async handoff.
    """
    queryset = Job.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCreateSerializer
        return JobSerializer
    
    @extend_schema(
        summary="List Jobs",
        description="Get a list of all jobs with their current status and progress",
        parameters=[
            OpenApiParameter(
                name='status',
                description='Filter jobs by status',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='job_type',
                description='Filter jobs by type',
                required=False,
                type=str
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by job type if provided
        job_type_filter = request.query_params.get('job_type')
        if job_type_filter:
            queryset = queryset.filter(job_type=job_type_filter)
        
        # Filter by current user
        if not request.user.is_staff:
            queryset = queryset.filter(created_by=request.user)
        
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create Job",
        description="Create a new background job with ETA calculation and auto sync→async handoff",
        request=JobCreateSerializer,
        responses={201: JobSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = JobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create job instance
        job = Job.objects.create(
            job_type=serializer.validated_data['job_type'],
            input_data=serializer.validated_data['input_data'],
            created_by=request.user,
            estimated_completion=datetime.now() + timedelta(
                seconds=serializer.validated_data.get('estimated_duration', 300)
            )
        )
        
        # Start background task
        task = execute_job.delay(str(job.id))
        job.celery_task_id = task.id
        job.save()
        
        return Response(
            JobSerializer(job).data,
            status=status.HTTP_201_CREATED
        )


class JobDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific job.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get Job Details",
        description="Get detailed information about a specific job including progress and ETA"
    )
    def get(self, request, *args, **kwargs):
        job = self.get_object()
        
        # Check permissions
        if not request.user.is_staff and job.created_by != request.user:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().get(request, *args, **kwargs)


class JobCancelView(APIView):
    """
    Cancel a running job.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Cancel Job",
        description="Cancel a running job if it's still in progress",
        responses={200: {"description": "Job cancelled successfully"}}
    )
    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        
        # Check permissions
        if not request.user.is_staff and job.created_by != request.user:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if job can be cancelled
        if job.is_completed:
            return Response(
                {"error": "Job is already completed and cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel Celery task
        if job.celery_task_id:
            current_app.control.revoke(job.celery_task_id, terminate=True)
        
        # Update job status
        job.status = 'revoked'
        job.completed_at = datetime.now()
        job.save()
        
        return Response(
            {"message": "Job cancelled successfully"},
            status=status.HTTP_200_OK
        )