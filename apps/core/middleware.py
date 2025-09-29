"""
Idempotency middleware for ensuring API endpoints can be safely retried.
"""
import hashlib
import json
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.utils.decorators import sync_and_async_middleware


@sync_and_async_middleware
def IdempotencyMiddleware(get_response: Callable) -> Callable:
    """
    Middleware to handle idempotent API requests using idempotency keys.
    
    For POST, PUT, PATCH requests with an Idempotency-Key header,
    this middleware will:
    1. Check if we've seen this key before
    2. If yes, return the cached response
    3. If no, process the request and cache the response
    """
    
    def middleware(request: HttpRequest) -> HttpResponse:
        # Only process certain HTTP methods
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return get_response(request)
        
        # Check for idempotency key
        idempotency_key = request.headers.get(settings.IDEMPOTENCY_KEY_HEADER)
        if not idempotency_key:
            return get_response(request)
        
        # Create cache key
        cache_key = f"idempotency:{idempotency_key}:{request.path}"
        
        # Check if we've processed this request before
        cached_response = cache.get(cache_key)
        if cached_response:
            response = HttpResponse(
                content=cached_response['content'],
                status=cached_response['status'],
                content_type=cached_response['content_type']
            )
            for header, value in cached_response['headers'].items():
                response[header] = value
            return response
        
        # Process the request
        response = get_response(request)
        
        # Cache the response for successful requests
        if 200 <= response.status_code < 300:
            cached_data = {
                'content': response.content,
                'status': response.status_code,
                'content_type': response.get('Content-Type', 'application/json'),
                'headers': dict(response.items())
            }
            cache.set(cache_key, cached_data, timeout=settings.IDEMPOTENCY_CACHE_TIMEOUT)
        
        return response
    
    return middleware