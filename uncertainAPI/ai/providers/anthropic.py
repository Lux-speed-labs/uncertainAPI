"""Anthropic provider implementation."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import ProviderError

class AnthropicProvider:
    """Anthropic API provider.

    Adapts Anthropic's API to OpenAI-style interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs: Any,
    ) -> None:
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key.
            model: Model name to use.
            **kwargs: Additional Anthropic client options.
        """
        try:
            from anthropic import Anthropic, AsyncAnthropic
        except ImportError as exc:
            raise ProviderError(
                "Anthropic not installed. Install with: pip install uncertainapi[anthropic]"
            ) from exc

        self.model = model
        self.client = Anthropic(api_key=api_key, **kwargs)
        self.async_client = AsyncAnthropic(api_key=api_key, **kwargs)
        logger.info("ai.provider.initialized", extra={"provider": "anthropic", "model": model})

    def _convert_messages(self, messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
        """Convert OpenAI-style messages to Anthropic format.

        Returns:
            Tuple of (system_message, anthropic_messages)
        """
        system_message = ""
        anthropic_messages = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                system_message = content if isinstance(content, str) else str(content)
            else:
                # Anthropic uses 'user' and 'assistant' roles
                anthropic_role = "assistant" if role == "assistant" else "user"
                anthropic_messages.append({"role": anthropic_role, "content": content})

        return system_message, anthropic_messages

    def complete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a completion from messages."""
        logger.debug("ai.provider.complete.start", extra={"provider": "anthropic", "message_count": len(messages)})
        try:
            system_message, anthropic_messages = self._convert_messages(messages)

            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": kwargs.pop("max_tokens", 4096),
                **kwargs,
            }

            if system_message:
                completion_kwargs["system"] = system_message

            response = self.client.messages.create(**completion_kwargs)

            # Extract text content
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }

            logger.info(
                "ai.provider.complete.success",
                extra={
                    "provider": "anthropic",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.complete.failed", extra={"provider": "anthropic"})
            raise ProviderError(f"Anthropic completion failed: {exc}") from exc

    async def acomplete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Async version of complete."""
        logger.debug("ai.provider.acomplete.start", extra={"provider": "anthropic", "message_count": len(messages)})
        try:
            system_message, anthropic_messages = self._convert_messages(messages)

            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": kwargs.pop("max_tokens", 4096),
                **kwargs,
            }

            if system_message:
                completion_kwargs["system"] = system_message

            response = await self.async_client.messages.create(**completion_kwargs)

            # Extract text content
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }

            logger.info(
                "ai.provider.acomplete.success",
                extra={
                    "provider": "anthropic",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.acomplete.failed", extra={"provider": "anthropic"})
            raise ProviderError(f"Anthropic completion failed: {exc}") from exc



