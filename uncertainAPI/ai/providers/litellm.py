"""LiteLLM provider implementation."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import ProviderError

class LiteLLMProvider:
    """LiteLLM provider.

    Supports 100+ LLM providers including Ollama, local models, and more.
    Uses OpenAI-compatible API format.
    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize LiteLLM provider.

        Args:
            model: Model name (e.g., 'ollama/llama2', 'claude-3-opus').
            api_key: API key if required by the model provider.
            api_base: Base URL for API (e.g., for Ollama local server).
            **kwargs: Additional LiteLLM options.
        """
        try:
            import litellm
        except ImportError as exc:
            raise ProviderError(
                "LiteLLM not installed. Install with: pip install uncertainapi[litellm]"
            ) from exc

        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.kwargs = kwargs
        self._litellm = litellm

        # Configure LiteLLM
        if api_base:
            litellm.api_base = api_base
        if api_key:
            litellm.api_key = api_key

        logger.info("ai.provider.initialized", extra={"provider": "litellm", "model": model})

    def complete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a completion from messages."""
        logger.debug("ai.provider.complete.start", extra={"provider": "litellm", "message_count": len(messages)})
        try:
            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                **self.kwargs,
                **kwargs,
            }

            if response_format:
                completion_kwargs["response_format"] = response_format

            response = self._litellm.completion(**completion_kwargs)

            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, "usage") else 0,
                },
            }

            logger.info(
                "ai.provider.complete.success",
                extra={
                    "provider": "litellm",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.complete.failed", extra={"provider": "litellm"})
            raise ProviderError(f"LiteLLM completion failed: {exc}") from exc

    async def acomplete(
        self,
        messages: list[dict[str, Any]],
        response_format: Optional[dict[str, Any]] = None,
        vision: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Async version of complete."""
        logger.debug("ai.provider.acomplete.start", extra={"provider": "litellm", "message_count": len(messages)})
        try:
            completion_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                **self.kwargs,
                **kwargs,
            }

            if response_format:
                completion_kwargs["response_format"] = response_format

            response = await self._litellm.acompletion(**completion_kwargs)

            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, "usage") else 0,
                },
            }

            logger.info(
                "ai.provider.acomplete.success",
                extra={
                    "provider": "litellm",
                    "tokens": result["usage"]["total_tokens"],
                },
            )
            return result
        except Exception as exc:
            logger.exception("ai.provider.acomplete.failed", extra={"provider": "litellm"})
            raise ProviderError(f"LiteLLM completion failed: {exc}") from exc



