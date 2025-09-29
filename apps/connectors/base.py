"""
Pluggable connector framework for third-party integrations.

This module provides a base framework for creating connectors that include:
- Tools: Reusable functions for interacting with external APIs
- Serializers: Data validation and transformation
- ViewSets: REST API endpoints for connector operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from rest_framework import serializers, viewsets
from rest_framework.response import Response


class BaseConnectorTool(ABC):
    """
    Base class for connector tools.
    """
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's input/output schema."""
        pass


class BaseConnectorSerializer(serializers.Serializer):
    """
    Base serializer for connector data.
    """
    pass


class BaseConnectorViewSet(viewsets.ViewSet):
    """
    Base viewset for connector endpoints.
    """
    
    def list(self, request):
        """List available connector operations."""
        return Response({
            "message": "Base connector - implement in subclass",
            "operations": []
        })


# Example connector implementations

class HTTPRequestTool(BaseConnectorTool):
    """
    Tool for making HTTP requests to external APIs.
    """
    
    def execute(self, url: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        import httpx
        
        try:
            with httpx.Client() as client:
                response = client.request(method, url, **kwargs)
                return {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content': response.text,
                    'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }
        except Exception as e:
            return {
                'error': str(e),
                'status_code': None
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            'input': {
                'url': {'type': 'string', 'required': True},
                'method': {'type': 'string', 'default': 'GET'},
                'headers': {'type': 'object', 'required': False},
                'params': {'type': 'object', 'required': False},
                'json': {'type': 'object', 'required': False}
            },
            'output': {
                'status_code': {'type': 'integer'},
                'headers': {'type': 'object'},
                'content': {'type': 'string'},
                'json': {'type': 'object', 'nullable': True}
            }
        }


class DataTransformTool(BaseConnectorTool):
    """
    Tool for transforming data between formats.
    """
    
    def execute(self, data: Any, transform_type: str = 'json_to_dict', **kwargs) -> Dict[str, Any]:
        try:
            if transform_type == 'json_to_dict':
                import json
                if isinstance(data, str):
                    return {'result': json.loads(data)}
                return {'result': data}
            elif transform_type == 'csv_to_list':
                import csv
                import io
                if isinstance(data, str):
                    reader = csv.DictReader(io.StringIO(data))
                    return {'result': list(reader)}
                return {'error': 'Invalid input for CSV transformation'}
            else:
                return {'error': f'Unknown transform type: {transform_type}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            'input': {
                'data': {'type': 'any', 'required': True},
                'transform_type': {'type': 'string', 'enum': ['json_to_dict', 'csv_to_list']}
            },
            'output': {
                'result': {'type': 'any'},
                'error': {'type': 'string', 'nullable': True}
            }
        }