"""Mixins for ExtractorView customization."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional, Type, cast

from django.db import models
from pydantic import BaseModel
from rest_framework.request import Request

class PersistenceMixin:
    """Mixin to persist extracted data to Django models.

    Add this mixin to ExtractorView to automatically save results to database.

    Example:
        class ProductScraperView(PersistenceMixin, ExtractorView):
            schema_class = ProductSchema
            model_class = Product
    """

    model_class: Optional[Type[models.Model]] = None

    def get_model_class(self) -> Type[models.Model]:
        """Get Django model class for persistence.

        Returns:
            Django model class.

        Raises:
            ValueError: If model_class not configured.
        """
        if not self.model_class:
            raise ValueError("model_class must be configured when using PersistenceMixin")
        return self.model_class

    def save_to_model(self, data: BaseModel) -> models.Model:
        """Save extracted data to Django model.

        Args:
            data: Extracted data instance.

        Returns:
            Saved model instance.
        """
        model_class = self.get_model_class()
        data_dict = data.model_dump()

        # Create or update (django-stubs: .objects on abstract Model type)
        instance, created = model_class.objects.update_or_create(  # type: ignore[attr-defined]
            defaults=data_dict,
            **self.get_unique_fields(data_dict),
        )

        action = "created" if created else "updated"
        logger.info(
            f"persistence.{action}",
            extra={"model": model_class.__name__, "pk": instance.pk},
        )

        return cast(models.Model, instance)

    def get_unique_fields(self, data_dict: dict[str, Any]) -> dict[str, Any]:
        """Get fields to use for unique lookup.

        Override this to customize unique field selection.

        Args:
            data_dict: Data dictionary.

        Returns:
            Dict of fields for unique lookup.
        """
        # Default: use first field as unique identifier
        if data_dict:
            first_key = next(iter(data_dict.keys()))
            return {first_key: data_dict[first_key]}
        return {}

    async def extract_data(self, url: str, request: Request) -> list[BaseModel]:
        """Extract and persist data.

        Args:
            url: Target URL.
            request: DRF request object.

        Returns:
            List of extracted data instances.
        """
        # Extract data using parent class
        extracted_data = cast(
            list[BaseModel],
            await super().extract_data(url, request),  # type: ignore[misc]
        )

        # Persist each item (database operations should use async ORM)
        # For now, we'll run sync saves in executor to avoid blocking
        import asyncio

        loop = asyncio.get_event_loop()
        for item in extracted_data:
            await loop.run_in_executor(None, self.save_to_model, item)

        logger.info("persistence.batch_saved", extra={"count": len(extracted_data)})

        return extracted_data

class RateLimitMixin:
    """Mixin to add rate limiting to extractor views.

    Example:
        class ProductScraperView(RateLimitMixin, ExtractorView):
            rate_limit = "10/hour"  # Django-ratelimit format
    """

    rate_limit: str = "60/hour"

    def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limit.

        Args:
            request: DRF request object.

        Returns:
            True if within limit, False if exceeded.
        """
        # TODO: Implement rate limiting
        # Could use django-ratelimit or custom implementation
        logger.debug("rate_limit.check", extra={"limit": self.rate_limit})
        return True

