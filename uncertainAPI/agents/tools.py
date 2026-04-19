"""Tools for AG2 agents - bridges browser backends to AG2 format.

All tools are async but wrapped for AG2 synchronous compatibility.
"""

from __future__ import annotations

import base64
import json
from loguru import logger
from typing import Annotated, Any, Optional

from uncertainAPI.agents.async_tools import async_tool
from uncertainAPI.browsers.base import BrowserBackend
from uncertainAPI.exceptions import BrowserError

class BrowserTools:
    """Wrapper that provides browser tools for AG2 agents."""

    def __init__(self, browser: BrowserBackend) -> None:
        """Initialize browser tools.

        Args:
            browser: Browser backend instance.
        """
        self.browser = browser

    async def navigate_to_url(
        self,
        url: Annotated[str, "The URL to navigate to"],
    ) -> str:
        """Navigate to a URL.

        Args:
            url: The URL to navigate to.

        Returns:
            Status message.
        """
        logger.debug("tool.navigate", extra={"url": url})
        try:
            await self.browser.navigate(url)
            return f"Successfully navigated to {url}"
        except BrowserError as exc:
            logger.warning("tool.navigate.failed", extra={"url": url, "error": str(exc)})
            return f"Failed to navigate to {url}: {exc}"

    async def take_screenshot(self) -> str:
        """Take a screenshot of the current page.

        Returns:
            Base64-encoded screenshot image.
        """
        logger.debug("tool.screenshot")
        try:
            screenshot_bytes = await self.browser.screenshot()
            encoded = base64.b64encode(screenshot_bytes).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
        except BrowserError as exc:
            logger.warning("tool.screenshot.failed", extra={"error": str(exc)})
            return f"Failed to take screenshot: {exc}"

    async def get_page_html(self) -> str:
        """Get the HTML content of the current page.

        Returns:
            HTML content as string.
        """
        logger.debug("tool.get_html")
        try:
            html = await self.browser.get_html()
            # Truncate if too large for context
            if len(html) > 50000:
                logger.debug("tool.get_html.truncated", extra={"original_size": len(html)})
                return html[:50000] + "\n... (truncated)"
            return html
        except BrowserError as exc:
            logger.warning("tool.get_html.failed", extra={"error": str(exc)})
            return f"Failed to get HTML: {exc}"

    async def click_element(
        self,
        description: Annotated[str, "CSS selector or description of element to click"],
    ) -> str:
        """Click an element on the page.

        Args:
            description: CSS selector or natural language description.

        Returns:
            Status message.
        """
        logger.debug("tool.click", extra={"description": description})
        try:
            await self.browser.click(description)
            return f"Successfully clicked: {description}"
        except BrowserError as exc:
            logger.warning("tool.click.failed", extra={"description": description, "error": str(exc)})
            return f"Failed to click {description}: {exc}"

    async def fill_input(
        self,
        selector: Annotated[str, "CSS selector or description of input element"],
        value: Annotated[str, "Value to fill in the input"],
    ) -> str:
        """Fill an input element with a value.

        Args:
            selector: CSS selector or natural language description.
            value: Value to fill.

        Returns:
            Status message.
        """
        logger.debug("tool.fill", extra={"selector": selector})
        try:
            await self.browser.fill(selector, value)
            return f"Successfully filled {selector} with value"
        except BrowserError as exc:
            logger.warning("tool.fill.failed", extra={"selector": selector, "error": str(exc)})
            return f"Failed to fill {selector}: {exc}"

    async def extract_structured_data(
        self,
        schema_json: Annotated[str, "JSON schema defining the data structure to extract"],
    ) -> str:
        """Extract structured data matching the schema.

        Args:
            schema_json: JSON schema as string.

        Returns:
            Extracted data as JSON string or error message.
        """
        logger.debug("tool.extract_data")
        try:
            # This is a placeholder - actual implementation would use AI
            # to intelligently extract data matching the schema
            html = await self.browser.get_html()
            schema = json.loads(schema_json)

            # TODO: Implement AI-powered extraction
            # For now, return placeholder
            result = {
                "status": "extraction_started",
                "message": "Data extraction in progress",
                "html_length": len(html),
                "schema_fields": list(schema.get("properties", {}).keys()),
            }

            return json.dumps(result)
        except Exception as exc:
            logger.warning("tool.extract_data.failed", extra={"error": str(exc)})
            return f"Failed to extract data: {exc}"

    async def detect_captcha(self) -> str:
        """Detect if a captcha is present on the page.

        Returns:
            Detection result message.
        """
        logger.debug("tool.detect_captcha")
        try:
            html = await self.browser.get_html()
            # Simple heuristic - in production, use AI vision
            captcha_indicators = [
                "recaptcha",
                "g-recaptcha",
                "hcaptcha",
                "h-captcha",
                "captcha",
            ]

            for indicator in captcha_indicators:
                if indicator.lower() in html.lower():
                    logger.info("tool.detect_captcha.found", extra={"indicator": indicator})
                    return f"Captcha detected: {indicator}"

            return "No captcha detected"
        except Exception as exc:
            logger.warning("tool.detect_captcha.failed", extra={"error": str(exc)})
            return f"Failed to detect captcha: {exc}"

    async def detect_pagination(self) -> str:
        """Detect if pagination is present on the page.

        Returns:
            Pagination detection result.
        """
        logger.debug("tool.detect_pagination")
        try:
            html = await self.browser.get_html()
            # Simple heuristic - in production, use AI
            pagination_indicators = [
                'class="next"',
                'class="pagination"',
                'aria-label="Next"',
                'rel="next"',
                ">Next<",
                ">>",
            ]

            for indicator in pagination_indicators:
                if indicator in html:
                    logger.info("tool.detect_pagination.found", extra={"indicator": indicator})
                    return f"Pagination detected: {indicator}"

            return "No pagination detected"
        except Exception as exc:
            logger.warning("tool.detect_pagination.failed", extra={"error": str(exc)})
            return f"Failed to detect pagination: {exc}"

    def get_all_tools(self) -> list[Any]:
        """Get all available tool functions.

        Returns:
            List of tool methods (async, will be wrapped for AG2).
        """
        # Return async methods - they'll be wrapped by orchestrator
        return [
            self.navigate_to_url,
            self.take_screenshot,
            self.get_page_html,
            self.click_element,
            self.fill_input,
            self.extract_structured_data,
            self.detect_captcha,
            self.detect_pagination,
        ]

    def get_sync_tools_for_ag2(self) -> list[Any]:
        """Get sync-wrapped tools for AG2 compatibility.

        Returns:
            List of synchronous wrapper functions.
        """
        from uncertainAPI.agents.async_tools import make_sync_wrapper

        return [make_sync_wrapper(tool) for tool in self.get_all_tools()]

