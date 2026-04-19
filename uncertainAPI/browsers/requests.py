"""Async HTTP + BeautifulSoup browser backend implementation."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import BrowserError

class RequestsBackend:
    """Async HTTP + BeautifulSoup implementation of BrowserBackend.

    Lightweight fallback for static HTML pages without JavaScript.
    Uses httpx for async HTTP requests.
    """

    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Requests backend.

        Args:
            timeout: Request timeout in seconds.
            headers: Default headers to send with requests.
            **kwargs: Additional httpx.AsyncClient options.
        """
        try:
            import httpx
            from bs4 import BeautifulSoup
        except ImportError as exc:
            raise BrowserError(
                "httpx/BeautifulSoup not installed. "
                "Install with: pip install uncertainapi[requests]"
            ) from exc

        self.timeout = timeout
        self.default_headers = headers or {}
        self.client_kwargs = kwargs
        self._client: Optional[Any] = None
        self._current_url: Optional[str] = None
        self._current_html: Optional[str] = None
        self._soup: Optional[Any] = None
        self._httpx = httpx
        self._BeautifulSoup = BeautifulSoup

    async def _ensure_initialized(self) -> None:
        """Ensure client is initialized."""
        if self._client is not None:
            return

        logger.debug("browser.initialize.start", extra={"backend": "httpx"})
        self._client = self._httpx.AsyncClient(
            headers=self.default_headers,
            timeout=self.timeout,
            **self.client_kwargs,
        )
        logger.info("browser.initialized", extra={"backend": "httpx"})

    async def navigate(self, url: str) -> None:
        """Navigate to the given URL."""
        await self._ensure_initialized()
        logger.debug("browser.navigate.start", extra={"url": url})
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            self._current_url = url
            self._current_html = response.text
            self._soup = self._BeautifulSoup(self._current_html, "lxml")
            logger.info("browser.navigate.success", extra={"url": url, "status": response.status_code})
        except Exception as exc:
            logger.warning("browser.navigate.failed", extra={"url": url, "error": str(exc)})
            raise BrowserError(f"Failed to navigate to {url}: {exc}") from exc

    async def screenshot(self) -> bytes:
        """Take a screenshot - not supported in requests backend."""
        logger.warning("browser.screenshot.not_supported", extra={"backend": "requests"})
        raise BrowserError("Screenshot not supported in Requests backend - use Playwright or Selenium")

    async def get_html(self) -> str:
        """Get the HTML content of the current page."""
        if self._current_html is None:
            raise BrowserError("No page loaded - call navigate() first")
        logger.debug("browser.get_html.success", extra={"size_chars": len(self._current_html)})
        return self._current_html

    async def click(self, description: str) -> None:
        """Click - not supported in requests backend."""
        logger.warning("browser.click.not_supported", extra={"backend": "requests", "description": description})
        raise BrowserError("Click not supported in Requests backend - use Playwright or Selenium")

    async def fill(self, description: str, value: str) -> None:
        """Fill - not supported in requests backend."""
        logger.warning("browser.fill.not_supported", extra={"backend": "requests", "description": description})
        raise BrowserError("Fill not supported in Requests backend - use Playwright or Selenium")

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript - not supported in requests backend."""
        logger.warning("browser.execute_script.not_supported", extra={"backend": "requests"})
        raise BrowserError("JavaScript not supported in Requests backend - use Playwright or Selenium")

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for selector - not supported in requests backend."""
        logger.warning("browser.wait_for_selector.not_supported", extra={"backend": "requests", "selector": selector})
        raise BrowserError("wait_for_selector not supported in Requests backend - use Playwright or Selenium")

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        logger.debug("browser.close.start")
        try:
            if self._client:
                await self._client.aclose()
            logger.info("browser.close.success")
        except Exception as exc:
            logger.warning("browser.close.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to close client: {exc}") from exc
        finally:
            self._client = None
            self._current_url = None
            self._current_html = None
            self._soup = None

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies from the current client."""
        await self._ensure_initialized()
        logger.debug("browser.get_cookies")
        try:
            cookies = [
                {
                    "name": name,
                    "value": value,
                    "domain": "",
                    "path": "/",
                    "secure": False,
                }
                for name, value in self._client.cookies.items()
            ]
            logger.debug("browser.get_cookies.success", extra={"count": len(cookies)})
            return cookies
        except Exception as exc:
            logger.warning("browser.get_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to get cookies: {exc}") from exc

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current client."""
        await self._ensure_initialized()
        logger.debug("browser.set_cookies", extra={"count": len(cookies)})
        try:
            for cookie in cookies:
                self._client.cookies.set(
                    name=cookie["name"],
                    value=cookie["value"],
                    domain=cookie.get("domain", ""),
                )
            logger.debug("browser.set_cookies.success", extra={"count": len(cookies)})
        except Exception as exc:
            logger.warning("browser.set_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to set cookies: {exc}") from exc

