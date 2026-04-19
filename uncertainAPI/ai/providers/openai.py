"""OpenAI provider implementation."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import ProviderError

class OpenAIProvider:
    """OpenAI API provider.

    Native implementation using OpenAI's official client.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key.
            model: Model name to use.
            base_url: Optional custom base URL (for OpenAI-compatible APIs).
            **kwargs: Additional OpenAI client options.
        """
        try:
            from openai import AsyncOpenAI, OpenAI
        except ImportError as exc:
            raise ProviderError(
                "OpenAI not installed. Install with: pip install uncertainapi[openai]"
            ) from exc

        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url, **kwargs)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url, **kwargs)
        logger.info("ai.provider.initialized", extra={"provider": "openai", "model": model})

    def complete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a completion from messages."""
        logger.debug("ai.provider.complete.start", extra={"provider": "openai", "message_count": len(messages)})
        try:
            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                **kwargs,
            }

            if response_format:
                completion_kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**completion_kwargs)

            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

            logger.info(
                "ai.provider.complete.success",
                extra={
                    "provider": "openai",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.complete.failed", extra={"provider": "openai"})
            raise ProviderError(f"OpenAI completion failed: {exc}") from exc

    async def acomplete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Async version of complete."""
        logger.debug("ai.provider.acomplete.start", extra={"provider": "openai", "message_count": len(messages)})
        try:
            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                **kwargs,
            }

            if response_format:
                completion_kwargs["response_format"] = response_format

            response = await self.async_client.chat.completions.create(**completion_kwargs)

            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

            logger.info(
                "ai.provider.acomplete.success",
                extra={
                    "provider": "openai",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.acomplete.failed", extra={"provider": "openai"})
            raise ProviderError(f"OpenAI completion failed: {exc}") from exc



