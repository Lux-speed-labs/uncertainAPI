"""Base browser backend protocol."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional, Protocol

class BrowserBackend(Protocol):
    """Protocol for browser backend implementations."""

    async def navigate(self, url: str) -> None:
        """Navigate to the given URL.

        Args:
            url: The URL to navigate to.

        Raises:
            BrowserError: If navigation fails.
        """
        ...

    async def screenshot(self) -> bytes:
        """Take a screenshot of the current page.

        Returns:
            Screenshot as bytes.

        Raises:
            BrowserError: If screenshot fails.
        """
        ...

    async def get_html(self) -> str:
        """Get the HTML content of the current page.

        Returns:
            HTML content as string.

        Raises:
            BrowserError: If getting HTML fails.
        """
        ...

    async def click(self, description: str) -> None:
        """Click an element based on natural language description.

        Args:
            description: Natural language description of the element to click.

        Raises:
            BrowserError: If click fails.
        """
        ...

    async def fill(self, description: str, value: str) -> None:
        """Fill an input element based on natural language description.

        Args:
            description: Natural language description of the element to fill.
            value: The value to fill.

        Raises:
            BrowserError: If fill fails.
        """
        ...

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page.

        Args:
            script: JavaScript code to execute.

        Returns:
            Result of the script execution.

        Raises:
            BrowserError: If script execution fails.
        """
        ...

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for a selector to appear on the page.

        Args:
            selector: CSS selector to wait for.
            timeout: Timeout in milliseconds.

        Raises:
            BrowserError: If selector doesn't appear within timeout.
        """
        ...

    async def close(self) -> None:
        """Close the browser and cleanup resources.

        Raises:
            BrowserError: If close fails.
        """
        ...

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies from the current context.

        Returns:
            List of cookie dictionaries.

        Raises:
            BrowserError: If getting cookies fails.
        """
        ...

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current context.

        Args:
            cookies: List of cookie dictionaries.

        Raises:
            BrowserError: If setting cookies fails.
        """
        ...



