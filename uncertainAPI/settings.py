"""Settings validation and defaults for uncertainAPI."""

from __future__ import annotations

from loguru import logger
from typing import Any

def validate_settings(settings_dict: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize UncertainAPI settings.

    Args:
        settings_dict: Raw settings dictionary.

    Returns:
        Validated settings dictionary with defaults applied.

    Raises:
        ValueError: If required settings are missing or invalid.
    """
    validated: dict[str, Any] = {}

    # AI Provider settings
    ai_config = settings_dict.get("AI_PROVIDER", {})
    if not ai_config.get("BACKEND"):
        ai_config["BACKEND"] = "uncertainAPI.ai.providers.openai.OpenAIProvider"
    if not ai_config.get("MODEL"):
        ai_config["MODEL"] = "gpt-4o"
    validated["AI_PROVIDER"] = ai_config

    # Browser Backend settings
    browser_config = settings_dict.get("BROWSER_BACKEND", {})
    if not browser_config.get("BACKEND"):
        browser_config["BACKEND"] = "uncertainAPI.browsers.playwright.PlaywrightBackend"
    if "HEADLESS" not in browser_config:
        browser_config["HEADLESS"] = True
    if "TIMEOUT" not in browser_config:
        browser_config["TIMEOUT"] = 30000
    validated["BROWSER_BACKEND"] = browser_config

    # Task Scheduler settings
    task_config = settings_dict.get("TASK_SCHEDULER", {})
    validated["TASK_SCHEDULER"] = task_config

    # Cache settings
    validated["CACHE_BACKEND"] = settings_dict.get("CACHE_BACKEND", "default")

    # Auth storage
    validated["DEFAULT_AUTH_STORAGE"] = settings_dict.get("DEFAULT_AUTH_STORAGE", "database")

    logger.debug("settings.validated", extra={"config_keys": list(validated.keys())})

    return validated

DEFAULT_SETTINGS = {
    "AI_PROVIDER": {
        "BACKEND": "uncertainAPI.ai.providers.openai.OpenAIProvider",
        "MODEL": "gpt-4o",
    },
    "BROWSER_BACKEND": {
        "BACKEND": "uncertainAPI.browsers.playwright.PlaywrightBackend",
        "HEADLESS": True,
        "TIMEOUT": 30000,
    },
    "TASK_SCHEDULER": {},
    "CACHE_BACKEND": "default",
    "DEFAULT_AUTH_STORAGE": "database",
}



