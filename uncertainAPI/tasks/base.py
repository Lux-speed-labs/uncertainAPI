"""Base task scheduler protocol."""

from __future__ import annotations

from loguru import logger
from typing import Any, Protocol

class TaskScheduler(Protocol):
    """Protocol for task scheduler implementations."""

    def schedule(
        self,
        task_func: str,
        interval: int,
        **kwargs: Any,
    ) -> str:
        """Schedule a recurring task.

        Args:
            task_func: Dotted path to task function.
            interval: Interval in seconds.
            **kwargs: Additional task parameters.

        Returns:
            Task ID.
        """
        ...

    def run_once(
        self,
        task_func: str,
        **kwargs: Any,
    ) -> str:
        """Run a task once.

        Args:
            task_func: Dotted path to task function.
            **kwargs: Task parameters.

        Returns:
            Task ID.
        """
        ...

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_id: Task ID to cancel.

        Returns:
            True if cancelled, False if not found.
        """
        ...



