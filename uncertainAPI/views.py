"""DRF views for uncertainAPI extractors."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional, Type

from django.core.cache import cache
from pydantic import BaseModel
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from uncertainAPI.agents.orchestrator import ExtractorOrchestrator
from uncertainAPI.auth.base import AuthHandler
from uncertainAPI.browsers.factory import get_browser_backend
from uncertainAPI.ai.factory import get_ai_provider
from uncertainAPI.exceptions import ExtractorError
from uncertainAPI.serializers import pydantic_to_drf_serializer

class ExtractorView(APIView):
    """Base view for AI-powered web extraction.

    Subclass this and configure class attributes to create a extractor endpoint.

    Example:
        class ProductScraperView(ExtractorView):
            url = "https://example.com/products"
            schema_class = ProductSchema
            enable_caching = True
            cache_ttl = 3600
    """

    # Core configuration
    url: Optional[str] = None
    schema_class: Optional[Type[BaseModel]] = None
    auth_handler_class: Optional[Type[AuthHandler]] = None

    # Caching
    enable_caching: bool = True
    cache_ttl: int = 3600

    # Background processing
    enable_background: bool = False

    # Pagination
    pagination: bool = False

    # Orchestration
    orchestrator_class: Type[ExtractorOrchestrator] = ExtractorOrchestrator
    max_rounds: int = 20

    def get_url(self, request: Request) -> str:
        """Get target URL for extraction.

        Override this for dynamic URLs.

        Args:
            request: DRF request object.

        Returns:
            URL string.

        Raises:
            ValueError: If URL is not configured.
        """
        if self.url:
            return self.url

        # Try to get from query params
        url_param = request.query_params.get("url")
        if url_param:
            return url_param

        raise ValueError("URL must be configured via class attribute or query parameter")

    def get_schema_class(self) -> Type[BaseModel]:
        """Get extraction schema class.

        Override this for dynamic schema selection.

        Returns:
            Pydantic schema class.

        Raises:
            ValueError: If schema is not configured.
        """
        if not self.schema_class:
            raise ValueError("schema_class must be configured")
        return self.schema_class

    def get_auth_handler(self, request: Request) -> Optional[AuthHandler]:
        """Get authentication handler instance.

        Override this for custom auth configuration.

        Args:
            request: DRF request object.

        Returns:
            AuthHandler instance or None.
        """
        if not self.auth_handler_class:
            return None

        # Get credentials from request (could be from POST body, headers, etc.)
        credentials = request.data.get("credentials", {})
        return self.auth_handler_class(credentials=credentials)

    def get_cache_key(self, url: str) -> str:
        """Get cache key for URL.

        Args:
            url: Target URL.

        Returns:
            Cache key string.
        """
        schema_name = self.get_schema_class().__name__
        return f"uncertainapi:extractor:{schema_name}:{url}"

    def get_serializer_class(self) -> Type[Any]:
        """Get DRF serializer class for schema.

        Returns:
            DRF serializer class.
        """
        schema_class = self.get_schema_class()
        return pydantic_to_drf_serializer(schema_class)

    def get_orchestrator(
        self,
        url: str,
        request: Request,
    ) -> ExtractorOrchestrator:
        """Get orchestrator instance.

        Override this to customize orchestration.

        Args:
            url: Target URL.
            request: DRF request object.

        Returns:
            ExtractorOrchestrator instance.
        """
        from django.conf import settings

        uncertainapi_settings = getattr(settings, "UNCERTAINAPI", {})

        # Get browser backend
        browser_config = uncertainapi_settings.get("BROWSER_BACKEND", {})
        browser = get_browser_backend(browser_config)

        # Get AI provider
        ai_config = uncertainapi_settings.get("AI_PROVIDER", {})
        ai_provider = get_ai_provider(ai_config)

        # Get auth handler
        auth_handler = self.get_auth_handler(request)

        # Create orchestrator
        return self.orchestrator_class(
            browser=browser,
            ai_provider=ai_provider,
            schema_class=self.get_schema_class(),
            auth_handler=auth_handler,
            enable_pagination=self.pagination,
            max_rounds=self.max_rounds,
        )

    async def extract_data(self, url: str, request: Request) -> list[BaseModel]:
        """Extract data from URL.

        Args:
            url: Target URL.
            request: DRF request object.

        Returns:
            List of extracted data instances.

        Raises:
            ExtractorError: If extraction fails.
        """
        orchestrator = self.get_orchestrator(url, request)
        return await orchestrator.extract(url)

    async def get(self, request: Request) -> Response:
        """Handle GET request (async).

        Args:
            request: DRF request object.

        Returns:
            DRF Response with extracted data.
        """
        logger.info("extractor.request.start", extra={"view": self.__class__.__name__})

        try:
            url = self.get_url(request)

            # Check cache if enabled (cache operations are sync but fast)
            if self.enable_caching:
                cache_key = self.get_cache_key(url)
                cached_data = cache.get(cache_key)
                if cached_data:
                    logger.info("extractor.cache.hit", extra={"url": url})
                    return Response(cached_data, status=status.HTTP_200_OK)

            # Background processing
            if self.enable_background:
                # TODO: Implement task scheduling
                logger.info("extractor.background.scheduled", extra={"url": url})
                return Response(
                    {"status": "scheduled", "message": "Extraction task scheduled"},
                    status=status.HTTP_202_ACCEPTED,
                )

            # Async extraction
            extracted_data = await self.extract_data(url, request)

            # Serialize data (CPU-bound, sync)
            serializer_class = self.get_serializer_class()
            serialized_data = [
                serializer_class(data=item.model_dump()).initial_data
                for item in extracted_data
            ]

            # Cache results (cache operations are sync but fast)
            if self.enable_caching:
                cache_key = self.get_cache_key(url)
                cache.set(cache_key, serialized_data, self.cache_ttl)
                logger.debug("extractor.cache.set", extra={"url": url, "ttl": self.cache_ttl})

            logger.info("extractor.request.success", extra={"url": url, "count": len(serialized_data)})
            return Response(serialized_data, status=status.HTTP_200_OK)

        except ValueError as exc:
            logger.warning("extractor.request.validation_error", extra={"error": str(exc)})
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ExtractorError as exc:
            logger.warning("extractor.request.extraction_error", extra={"error": str(exc)})
            return Response(
                {"error": f"Extraction failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            logger.exception("extractor.request.error")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

