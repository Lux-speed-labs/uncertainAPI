"""Playwright browser backend implementation."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import BrowserError

class PlaywrightBackend:
    """Playwright implementation of BrowserBackend.

    This is the recommended browser backend with full JavaScript support,
    modern async API, and excellent AI-assisted interaction capabilities.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        """Initialize Playwright backend.

        Args:
            headless: Whether to run browser in headless mode.
            timeout: Default timeout in milliseconds.
            browser_type: Browser type ('chromium', 'firefox', 'webkit').
            **kwargs: Additional browser launch options.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise BrowserError(
                "Playwright not installed. Install with: pip install uncertainapi[playwright]"
            ) from exc

        self.headless = headless
        self.timeout = timeout
        self.browser_type = browser_type
        self.launch_options = kwargs
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._async_playwright = async_playwright

    async def _ensure_initialized(self) -> None:
        """Ensure browser is initialized."""
        if self._page is not None:
            return

        logger.debug("browser.initialize.start", extra={"browser_type": self.browser_type})
        try:
            self._playwright = await self._async_playwright().start()
            browser_launcher = getattr(self._playwright, self.browser_type)
            self._browser = await browser_launcher.launch(
                headless=self.headless, **self.launch_options
            )
            self._context = await self._browser.new_context()
            self._page = await self._context.new_page()
            self._page.set_default_timeout(self.timeout)
            logger.info("browser.initialized", extra={"browser_type": self.browser_type})
        except Exception as exc:
            logger.exception("browser.initialize.failed", extra={"browser_type": self.browser_type})
            raise BrowserError(f"Failed to initialize Playwright: {exc}") from exc

    async def navigate(self, url: str) -> None:
        """Navigate to the given URL."""
        await self._ensure_initialized()
        logger.debug("browser.navigate.start", extra={"url": url})
        try:
            assert self._page is not None
            await self._page.goto(url, wait_until="networkidle")
            logger.info("browser.navigate.success", extra={"url": url})
        except Exception as exc:
            logger.warning("browser.navigate.failed", extra={"url": url, "error": str(exc)})
            raise BrowserError(f"Failed to navigate to {url}: {exc}") from exc

    async def screenshot(self) -> bytes:
        """Take a screenshot of the current page."""
        await self._ensure_initialized()
        logger.debug("browser.screenshot")
        try:
            assert self._page is not None
            screenshot_bytes = await self._page.screenshot(full_page=True)
            logger.debug("browser.screenshot.success", extra={"size_bytes": len(screenshot_bytes)})
            return screenshot_bytes
        except Exception as exc:
            logger.warning("browser.screenshot.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to take screenshot: {exc}") from exc

    async def get_html(self) -> str:
        """Get the HTML content of the current page."""
        await self._ensure_initialized()
        logger.debug("browser.get_html")
        try:
            assert self._page is not None
            html = await self._page.content()
            logger.debug("browser.get_html.success", extra={"size_chars": len(html)})
            return html
        except Exception as exc:
            logger.warning("browser.get_html.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to get HTML: {exc}") from exc

    async def click(self, description: str) -> None:
        """Click an element based on natural language description.

        Note: This is a simplified implementation. In production, you'd use
        AI to interpret the description and find the element.
        """
        await self._ensure_initialized()
        logger.debug("browser.click", extra={"description": description})
        try:
            assert self._page is not None
            # For now, treat description as a selector
            # TODO: Implement AI-powered element detection
            await self._page.click(description)
            logger.info("browser.click.success", extra={"description": description})
        except Exception as exc:
            logger.warning("browser.click.failed", extra={"description": description, "error": str(exc)})
            raise BrowserError(f"Failed to click {description}: {exc}") from exc

    async def fill(self, description: str, value: str) -> None:
        """Fill an input element based on natural language description."""
        await self._ensure_initialized()
        logger.debug("browser.fill", extra={"description": description})
        try:
            assert self._page is not None
            # For now, treat description as a selector
            # TODO: Implement AI-powered element detection
            await self._page.fill(description, value)
            logger.info("browser.fill.success", extra={"description": description})
        except Exception as exc:
            logger.warning("browser.fill.failed", extra={"description": description, "error": str(exc)})
            raise BrowserError(f"Failed to fill {description}: {exc}") from exc

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        await self._ensure_initialized()
        logger.debug("browser.execute_script")
        try:
            assert self._page is not None
            result = await self._page.evaluate(script)
            logger.debug("browser.execute_script.success")
            return result
        except Exception as exc:
            logger.warning("browser.execute_script.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to execute script: {exc}") from exc

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for a selector to appear on the page."""
        await self._ensure_initialized()
        logger.debug("browser.wait_for_selector", extra={"selector": selector})
        try:
            assert self._page is not None
            await self._page.wait_for_selector(selector, timeout=timeout or self.timeout)
            logger.debug("browser.wait_for_selector.success", extra={"selector": selector})
        except Exception as exc:
            logger.warning("browser.wait_for_selector.failed", extra={"selector": selector, "error": str(exc)})
            raise BrowserError(f"Failed to wait for {selector}: {exc}") from exc

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        logger.debug("browser.close.start")
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("browser.close.success")
        except Exception as exc:
            logger.warning("browser.close.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to close browser: {exc}") from exc
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies from the current context."""
        await self._ensure_initialized()
        logger.debug("browser.get_cookies")
        try:
            assert self._context is not None
            cookies = await self._context.cookies()
            logger.debug("browser.get_cookies.success", extra={"count": len(cookies)})
            return cookies
        except Exception as exc:
            logger.warning("browser.get_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to get cookies: {exc}") from exc

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current context."""
        await self._ensure_initialized()
        logger.debug("browser.set_cookies", extra={"count": len(cookies)})
        try:
            assert self._context is not None
            await self._context.add_cookies(cookies)
            logger.debug("browser.set_cookies.success", extra={"count": len(cookies)})
        except Exception as exc:
            logger.warning("browser.set_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to set cookies: {exc}") from exc



