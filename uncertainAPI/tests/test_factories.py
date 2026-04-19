"""Tests for factory functions."""

from __future__ import annotations

import pytest

from uncertainAPI.browsers.factory import get_browser_backend
from uncertainAPI.ai.factory import get_ai_provider
from uncertainAPI.exceptions import ConfigurationError

class TestBrowserFactory:
    """Test browser backend factory."""

    def test_get_playwright_backend(self) -> None:
        """Test getting Playwright backend."""
        settings = {
            "BACKEND": "uncertainAPI.browsers.playwright.PlaywrightBackend",
            "HEADLESS": True,
            "TIMEOUT": 30000,
        }

        backend = get_browser_backend(settings)
        assert backend is not None
        assert hasattr(backend, "navigate")
        assert hasattr(backend, "screenshot")

    def test_get_requests_backend(self) -> None:
        """Test getting Requests backend."""
        settings = {
            "BACKEND": "uncertainAPI.browsers.requests.RequestsBackend",
            "TIMEOUT": 30,
        }

        backend = get_browser_backend(settings)
        assert backend is not None
        assert hasattr(backend, "navigate")

    def test_invalid_backend(self) -> None:
        """Test invalid backend configuration."""
        settings = {
            "BACKEND": "uncertainAPI.browsers.NonExistentBackend",
        }

        with pytest.raises(ConfigurationError):
            get_browser_backend(settings)

class TestAIProviderFactory:
    """Test AI provider factory."""

    def test_get_openai_provider(self) -> None:
        """Test getting OpenAI provider."""
        settings = {
            "BACKEND": "uncertainAPI.ai.providers.openai.OpenAIProvider",
            "API_KEY": "test-key",
            "MODEL": "gpt-4o",
        }

        provider = get_ai_provider(settings)
        assert provider is not None
        assert hasattr(provider, "complete")
        assert hasattr(provider, "acomplete")

    def test_invalid_provider(self) -> None:
        """Test invalid provider configuration."""
        settings = {
            "BACKEND": "uncertainAPI.ai.providers.NonExistentProvider",
        }

        with pytest.raises(ConfigurationError):
            get_ai_provider(settings)



