"""Retry utilities with exponential backoff."""

from __future__ import annotations

import asyncio
import functools
from loguru import logger
from typing import Any, Callable, Type, TypeVar

T = TypeVar("T")

def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for async functions with exponential backoff retry.

    Args:
        max_attempts: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential_base: Base for exponential backoff.
        exceptions: Tuple of exception types to retry on.

    Returns:
        Decorated function.

    Example:
        @async_retry(max_attempts=5, base_delay=2.0)
        async def fetch_data(url: str) -> dict:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exception = None

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    last_exception = exc

                    if attempt >= max_attempts:
                        logger.error(
                            "retry.exhausted",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "error": str(exc),
                            },
                        )
                        raise

                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    logger.warning(
                        "retry.attempt",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "delay": delay,
                            "error": str(exc),
                        },
                    )

                    await asyncio.sleep(delay)

            # Should never reach here, but for type checker
            raise last_exception if last_exception else RuntimeError("Retry failed")

        return wrapper

    return decorator

class AsyncRetryContext:
    """Context manager for async retry with exponential backoff.

    Example:
        async with AsyncRetryContext(max_attempts=3) as retry:
            while retry.should_retry():
                try:
                    result = await some_operation()
                    break
                except Exception as exc:
                    await retry.handle_exception(exc)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        exceptions: tuple[Type[Exception], ...] = (Exception,),
    ) -> None:
        """Initialize retry context.

        Args:
            max_attempts: Maximum number of retry attempts.
            base_delay: Initial delay in seconds.
            max_delay: Maximum delay in seconds.
            exponential_base: Base for exponential backoff.
            exceptions: Tuple of exception types to retry on.
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.exceptions = exceptions
        self.attempt = 0
        self.last_exception: Exception | None = None

    async def __aenter__(self) -> AsyncRetryContext:
        """Enter context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit context."""
        return False

    def should_retry(self) -> bool:
        """Check if should retry.

        Returns:
            True if should retry, False otherwise.
        """
        return self.attempt < self.max_attempts

    async def handle_exception(self, exc: Exception) -> None:
        """Handle exception and apply backoff.

        Args:
            exc: Exception that occurred.

        Raises:
            Exception: If max attempts reached or exception not in retry list.
        """
        self.attempt += 1
        self.last_exception = exc

        if not isinstance(exc, self.exceptions):
            raise exc

        if self.attempt >= self.max_attempts:
            logger.error(
                "retry.context.exhausted",
                extra={"attempts": self.attempt, "error": str(exc)},
            )
            raise exc

        delay = min(
            self.base_delay * (self.exponential_base ** (self.attempt - 1)),
            self.max_delay,
        )

        logger.warning(
            "retry.context.attempt",
            extra={
                "attempt": self.attempt,
                "max_attempts": self.max_attempts,
                "delay": delay,
                "error": str(exc),
            },
        )

        await asyncio.sleep(delay)



