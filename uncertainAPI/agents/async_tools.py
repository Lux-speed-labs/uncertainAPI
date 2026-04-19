"""Async-to-sync tool wrappers for AG2 compatibility."""

from __future__ import annotations

import asyncio
import functools
import inspect
from loguru import logger
from typing import Any, Callable

def make_sync_wrapper(async_func: Callable[..., Any]) -> Callable[..., Any]:
    """Create a synchronous wrapper for an async function.

    AG2 expects synchronous tool functions, but our tools are async.
    This wrapper allows AG2 to call async tools seamlessly.

    Args:
        async_func: Async function to wrap.

    Returns:
        Synchronous wrapper function.

    Example:
        @make_sync_wrapper
        async def async_tool(arg: str) -> str:
            return await do_something_async(arg)

        # Can now be called synchronously by AG2
        result = async_tool("test")
    """
    if not inspect.iscoroutinefunction(async_func):
        # Already sync, return as-is
        return async_func

    @functools.wraps(async_func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        """Synchronous wrapper that runs async function."""
        logger.debug(
            "async_tool.sync_wrapper",
            extra={"tool": async_func.__name__, "args_count": len(args)},
        )

        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            
            if loop.is_running():
                # We're already in an async context
                # Use nest_asyncio to allow nested event loops
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(async_func(*args, **kwargs))
                except ImportError:
                    logger.warning(
                        "async_tool.nest_asyncio_missing",
                        extra={"tool": async_func.__name__},
                    )
                    # Fallback: create new loop (may cause issues)
                    return asyncio.run(async_func(*args, **kwargs))
            else:
                # No loop running, safe to use run_until_complete
                return loop.run_until_complete(async_func(*args, **kwargs))
                
        except RuntimeError as exc:
            # No event loop exists, create one
            logger.debug(
                "async_tool.create_loop",
                extra={"tool": async_func.__name__, "error": str(exc)},
            )
            return asyncio.run(async_func(*args, **kwargs))
        except Exception as exc:
            logger.exception(
                "async_tool.failed",
                extra={"tool": async_func.__name__},
            )
            raise

    return sync_wrapper

class AsyncToolRegistry:
    """Registry for async tools with automatic sync wrapping.

    This class helps manage async tools that need to be exposed
    to AG2's synchronous tool system.

    Example:
        registry = AsyncToolRegistry()
        
        @registry.register
        async def my_tool(arg: str) -> str:
            return await do_async_work(arg)
        
        # Get sync-wrapped version for AG2
        sync_tools = registry.get_sync_tools()
    """

    def __init__(self) -> None:
        """Initialize tool registry."""
        self._async_tools: dict[str, Callable[..., Any]] = {}
        self._sync_wrappers: dict[str, Callable[..., Any]] = {}

    def register(self, async_func: Callable[..., Any]) -> Callable[..., Any]:
        """Register an async tool.

        Args:
            async_func: Async function to register.

        Returns:
            The original async function (for use as decorator).
        """
        name = async_func.__name__
        self._async_tools[name] = async_func
        self._sync_wrappers[name] = make_sync_wrapper(async_func)
        
        logger.debug("async_tool.registered", extra={"tool": name})
        
        return async_func

    def get_sync_wrapper(self, name: str) -> Callable[..., Any]:
        """Get synchronous wrapper for a tool.

        Args:
            name: Tool name.

        Returns:
            Sync wrapper function.

        Raises:
            KeyError: If tool not registered.
        """
        return self._sync_wrappers[name]

    def get_sync_tools(self) -> list[Callable[..., Any]]:
        """Get all sync-wrapped tools.

        Returns:
            List of synchronous wrapper functions.
        """
        return list(self._sync_wrappers.values())

    def get_async_tool(self, name: str) -> Callable[..., Any]:
        """Get original async tool.

        Args:
            name: Tool name.

        Returns:
            Original async function.

        Raises:
            KeyError: If tool not registered.
        """
        return self._async_tools[name]

# Global registry instance
default_registry = AsyncToolRegistry()

def async_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to register an async tool with automatic sync wrapping.

    Args:
        func: Async function to register.

    Returns:
        Sync-wrapped function suitable for AG2.

    Example:
        @async_tool
        async def fetch_data(url: str) -> str:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text
        
        # Can now be called by AG2 synchronously
        data = fetch_data("https://example.com")
    """
    default_registry.register(func)
    return make_sync_wrapper(func)



