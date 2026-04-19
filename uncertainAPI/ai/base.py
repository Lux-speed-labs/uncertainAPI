"""Base AI provider protocol."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional, Protocol

class AIProvider(Protocol):
    """Protocol for AI provider implementations.

    All providers should expose an OpenAI-style API for consistency.
    """

    def complete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a completion from messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            response_format: Optional response format (e.g., JSON schema).
            vision: Whether to use vision-capable model for images.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Response dictionary with 'content' and optional 'usage' keys.

        Raises:
            ProviderError: If completion fails.
        """
        ...

    async def acomplete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Async version of complete.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            response_format: Optional response format (e.g., JSON schema).
            vision: Whether to use vision-capable model for images.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Response dictionary with 'content' and optional 'usage' keys.

        Raises:
            ProviderError: If completion fails.
        """
        ...



