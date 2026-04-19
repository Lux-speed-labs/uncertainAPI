"""Selenium browser backend implementation."""

from __future__ import annotations

import asyncio
from loguru import logger
from typing import Any, Optional

from uncertainAPI.exceptions import BrowserError

class SeleniumBackend:
    """Selenium WebDriver implementation of BrowserBackend.

    Provides compatibility with existing Selenium-based tools and workflows.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30,
        browser_type: str = "chrome",
        **kwargs: Any,
    ) -> None:
        """Initialize Selenium backend.

        Args:
            headless: Whether to run browser in headless mode.
            timeout: Default timeout in seconds.
            browser_type: Browser type ('chrome', 'firefox', 'edge', 'safari').
            **kwargs: Additional webdriver options.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.support.ui import WebDriverWait
        except ImportError as exc:
            raise BrowserError(
                "Selenium not installed. Install with: pip install uncertainapi[selenium]"
            ) from exc

        self.headless = headless
        self.timeout = timeout
        self.browser_type = browser_type
        self.options_kwargs = kwargs
        self._driver: Optional[Any] = None
        self._wait: Optional[Any] = None
        self._webdriver = webdriver
        self._WebDriverWait = WebDriverWait

    def _ensure_initialized(self) -> None:
        """Ensure browser is initialized."""
        if self._driver is not None:
            return

        logger.debug("browser.initialize.start", extra={"browser_type": self.browser_type})
        try:
            if self.browser_type == "chrome":
                from selenium.webdriver.chrome.options import Options

                options = Options()
                if self.headless:
                    options.add_argument("--headless=new")
                for key, value in self.options_kwargs.items():
                    options.add_argument(f"--{key}={value}")
                self._driver = self._webdriver.Chrome(options=options)
            elif self.browser_type == "firefox":
                from selenium.webdriver.firefox.options import Options

                options = Options()
                if self.headless:
                    options.add_argument("--headless")
                for key, value in self.options_kwargs.items():
                    options.set_preference(key, value)
                self._driver = self._webdriver.Firefox(options=options)
            elif self.browser_type == "edge":
                from selenium.webdriver.edge.options import Options

                options = Options()
                if self.headless:
                    options.add_argument("--headless=new")
                for key, value in self.options_kwargs.items():
                    options.add_argument(f"--{key}={value}")
                self._driver = self._webdriver.Edge(options=options)
            else:
                raise BrowserError(f"Unsupported browser type: {self.browser_type}")

            self._driver.set_page_load_timeout(self.timeout)
            self._wait = self._WebDriverWait(self._driver, self.timeout)
            logger.info("browser.initialized", extra={"browser_type": self.browser_type})
        except Exception as exc:
            logger.exception("browser.initialize.failed", extra={"browser_type": self.browser_type})
            raise BrowserError(f"Failed to initialize Selenium: {exc}") from exc

    async def navigate(self, url: str) -> None:
        """Navigate to the given URL."""
        self._ensure_initialized()
        logger.debug("browser.navigate.start", extra={"url": url})
        try:
            await asyncio.get_event_loop().run_in_executor(None, self._driver.get, url)
            logger.info("browser.navigate.success", extra={"url": url})
        except Exception as exc:
            logger.warning("browser.navigate.failed", extra={"url": url, "error": str(exc)})
            raise BrowserError(f"Failed to navigate to {url}: {exc}") from exc

    async def screenshot(self) -> bytes:
        """Take a screenshot of the current page."""
        self._ensure_initialized()
        logger.debug("browser.screenshot")
        try:
            screenshot_bytes = await asyncio.get_event_loop().run_in_executor(
                None, self._driver.get_screenshot_as_png
            )
            logger.debug("browser.screenshot.success", extra={"size_bytes": len(screenshot_bytes)})
            return screenshot_bytes
        except Exception as exc:
            logger.warning("browser.screenshot.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to take screenshot: {exc}") from exc

    async def get_html(self) -> str:
        """Get the HTML content of the current page."""
        self._ensure_initialized()
        logger.debug("browser.get_html")
        try:
            html = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._driver.page_source
            )
            logger.debug("browser.get_html.success", extra={"size_chars": len(html)})
            return html
        except Exception as exc:
            logger.warning("browser.get_html.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to get HTML: {exc}") from exc

    async def click(self, description: str) -> None:
        """Click an element based on natural language description."""
        self._ensure_initialized()
        logger.debug("browser.click", extra={"description": description})
        try:
            from selenium.webdriver.common.by import By

            element = await asyncio.get_event_loop().run_in_executor(
                None, self._driver.find_element, By.CSS_SELECTOR, description
            )
            await asyncio.get_event_loop().run_in_executor(None, element.click)
            logger.info("browser.click.success", extra={"description": description})
        except Exception as exc:
            logger.warning("browser.click.failed", extra={"description": description, "error": str(exc)})
            raise BrowserError(f"Failed to click {description}: {exc}") from exc

    async def fill(self, description: str, value: str) -> None:
        """Fill an input element based on natural language description."""
        self._ensure_initialized()
        logger.debug("browser.fill", extra={"description": description})
        try:
            from selenium.webdriver.common.by import By

            element = await asyncio.get_event_loop().run_in_executor(
                None, self._driver.find_element, By.CSS_SELECTOR, description
            )
            await asyncio.get_event_loop().run_in_executor(None, element.clear)
            await asyncio.get_event_loop().run_in_executor(None, element.send_keys, value)
            logger.info("browser.fill.success", extra={"description": description})
        except Exception as exc:
            logger.warning("browser.fill.failed", extra={"description": description, "error": str(exc)})
            raise BrowserError(f"Failed to fill {description}: {exc}") from exc

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        self._ensure_initialized()
        logger.debug("browser.execute_script")
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._driver.execute_script, script
            )
            logger.debug("browser.execute_script.success")
            return result
        except Exception as exc:
            logger.warning("browser.execute_script.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to execute script: {exc}") from exc

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for a selector to appear on the page."""
        self._ensure_initialized()
        logger.debug("browser.wait_for_selector", extra={"selector": selector})
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC

            wait_timeout = timeout if timeout is not None else self.timeout
            wait = self._WebDriverWait(self._driver, wait_timeout)
            await asyncio.get_event_loop().run_in_executor(
                None, wait.until, EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            logger.debug("browser.wait_for_selector.success", extra={"selector": selector})
        except Exception as exc:
            logger.warning("browser.wait_for_selector.failed", extra={"selector": selector, "error": str(exc)})
            raise BrowserError(f"Failed to wait for {selector}: {exc}") from exc

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        logger.debug("browser.close.start")
        try:
            if self._driver:
                await asyncio.get_event_loop().run_in_executor(None, self._driver.quit)
            logger.info("browser.close.success")
        except Exception as exc:
            logger.warning("browser.close.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to close browser: {exc}") from exc
        finally:
            self._driver = None
            self._wait = None

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies from the current context."""
        self._ensure_initialized()
        logger.debug("browser.get_cookies")
        try:
            cookies = await asyncio.get_event_loop().run_in_executor(
                None, self._driver.get_cookies
            )
            logger.debug("browser.get_cookies.success", extra={"count": len(cookies)})
            return cookies
        except Exception as exc:
            logger.warning("browser.get_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to get cookies: {exc}") from exc

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current context."""
        self._ensure_initialized()
        logger.debug("browser.set_cookies", extra={"count": len(cookies)})
        try:
            for cookie in cookies:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._driver.add_cookie, cookie
                )
            logger.debug("browser.set_cookies.success", extra={"count": len(cookies)})
        except Exception as exc:
            logger.warning("browser.set_cookies.failed", extra={"error": str(exc)})
            raise BrowserError(f"Failed to set cookies: {exc}") from exc



