from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring system status.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Health Check",
        description="Check if the API is running and healthy",
        responses={200: {"description": "API is healthy"}}
    )
    def get(self, request):
        return Response({
            "status": "healthy",
            "message": "UncertainAPI is running"
        }, status=status.HTTP_200_OK)


class APIRootView(APIView):
    """
    Root API endpoint showing available endpoints.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="API Root",
        description="Root endpoint showing available API endpoints",
        responses={200: {"description": "Available endpoints"}}
    )
    def get(self, request):
        return Response({
            "message": "Welcome to UncertainAPI",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/v1/health/",
                "scrape": "/api/v1/scrape/",
                "jobs": "/api/v1/jobs/",
                "docs": "/api/docs/",
                "schema": "/api/schema/"
            }
        }, status=status.HTTP_200_OK)