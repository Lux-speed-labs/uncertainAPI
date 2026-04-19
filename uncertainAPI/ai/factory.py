"""Factory for creating AI providers."""

from __future__ import annotations

from loguru import logger
from typing import Any, Type

from uncertainAPI.ai.base import AIProvider
from uncertainAPI.exceptions import ConfigurationError

def get_ai_provider(settings: dict[str, Any]) -> AIProvider:
    """Get an AI provider instance based on settings.

    Args:
        settings: AI provider configuration from Django settings.

    Returns:
        Configured AI provider instance.

    Raises:
        ConfigurationError: If provider configuration is invalid.

    Example:
        settings = {
            'BACKEND': 'uncertainapi.ai.providers.OpenAIProvider',
            'API_KEY': 'sk-...',
            'MODEL': 'gpt-4o',
        }
        provider = get_ai_provider(settings)
    """
    backend_path = settings.get("BACKEND", "uncertainAPI.ai.providers.openai.OpenAIProvider")
    logger.debug("ai.factory.create", extra={"backend": backend_path})

    try:
        module_path, class_name = backend_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        provider_class: Type[AIProvider] = getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as exc:
        logger.error("ai.factory.import_failed", extra={"backend": backend_path, "error": str(exc)})
        raise ConfigurationError(f"Failed to import AI provider {backend_path}: {exc}") from exc

    # Extract provider-specific config (everything except BACKEND key)
    config = {k.lower(): v for k, v in settings.items() if k != "BACKEND"}

    try:
        provider_instance = provider_class(**config)
        logger.info("ai.factory.created", extra={"backend": backend_path})
        return provider_instance
    except Exception as exc:
        logger.exception("ai.factory.instantiation_failed", extra={"backend": backend_path})
        raise ConfigurationError(f"Failed to instantiate AI provider {backend_path}: {exc}") from exc



