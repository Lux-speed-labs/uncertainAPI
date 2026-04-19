"""Django app configuration for uncertainAPI."""

from __future__ import annotations

from django.apps import AppConfig


class UncertainAPIConfig(AppConfig):
    """App configuration for uncertainAPI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "uncertainAPI"
    verbose_name = "UncertainAPI"

    def ready(self) -> None:
        """Initialize app when Django starts."""
        from uncertainAPI.logging_config import configure_loguru_for_django, logger
        from django.conf import settings

        # Configure loguru based on Django settings
        try:
            configure_loguru_for_django(settings)
            logger.info("uncertainapi.ready", app="uncertainAPI")
        except Exception as exc:
            # Fallback to basic configuration
            from uncertainAPI.logging_config import configure_loguru
            configure_loguru()
            logger.warning("uncertainapi.logging.fallback", error=str(exc))

