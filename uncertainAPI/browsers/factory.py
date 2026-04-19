"""Factory for creating browser backends."""

from __future__ import annotations

from loguru import logger
from typing import Any, Type

from uncertainAPI.browsers.base import BrowserBackend
from uncertainAPI.exceptions import ConfigurationError

def get_browser_backend(settings: dict[str, Any]) -> BrowserBackend:
    """Get a browser backend instance based on settings.

    Args:
        settings: Browser backend configuration from Django settings.

    Returns:
        Configured browser backend instance.

    Raises:
        ConfigurationError: If backend configuration is invalid.

    Example:
        settings = {
            'BACKEND': 'uncertainapi.browsers.PlaywrightBackend',
            'HEADLESS': True,
            'TIMEOUT': 30000,
        }
        backend = get_browser_backend(settings)
    """
    backend_path = settings.get("BACKEND", "uncertainAPI.browsers.playwright.PlaywrightBackend")
    logger.debug("browser.factory.create", extra={"backend": backend_path})

    try:
        module_path, class_name = backend_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        backend_class: Type[BrowserBackend] = getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as exc:
        logger.error("browser.factory.import_failed", extra={"backend": backend_path, "error": str(exc)})
        raise ConfigurationError(f"Failed to import browser backend {backend_path}: {exc}") from exc

    # Extract backend-specific config (everything except BACKEND key)
    config = {k: v for k, v in settings.items() if k != "BACKEND"}

    try:
        backend_instance = backend_class(**config)
        logger.info("browser.factory.created", extra={"backend": backend_path})
        return backend_instance
    except Exception as exc:
        logger.exception("browser.factory.instantiation_failed", extra={"backend": backend_path})
        raise ConfigurationError(f"Failed to instantiate browser backend {backend_path}: {exc}") from exc



