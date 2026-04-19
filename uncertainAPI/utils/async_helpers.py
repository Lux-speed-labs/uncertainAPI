"""Async helper utilities."""

from __future__ import annotations

import asyncio
import functools
from loguru import logger
from typing import Any, Callable, TypeVar

T = TypeVar("T")

def run_in_executor(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
    """Decorator to run sync functions in executor.

    Use this for CPU-bound or sync I/O operations that need to be called
    from async context without blocking the event loop.

    Args:
        func: Synchronous function to wrap.

    Returns:
        Async function that runs original in executor.

    Example:
        @run_in_executor
        def heavy_computation(n: int) -> int:
            return sum(i * i for i in range(n))

        result = await heavy_computation(1000000)
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    return wrapper

async def run_sync_in_executor(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a sync function in executor without decorator.

    Args:
        func: Synchronous function to run.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Function result.

    Example:
        result = await run_sync_in_executor(sync_function, arg1, arg2, key=value)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

async def gather_with_concurrency(n: int, *tasks: Any) -> list[Any]:
    """Run tasks with limited concurrency.

    Args:
        n: Maximum number of concurrent tasks.
        *tasks: Async tasks to run.

    Returns:
        List of results.

    Example:
        results = await gather_with_concurrency(
            5,
            fetch_url(url1),
            fetch_url(url2),
            # ... 100 more tasks
        )
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Any) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))



