"""Default agent role implementations."""

from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING, Any

from uncertainAPI.agents.base import (
    BaseCoordinatorAgent,
    BaseExtractionAgent,
    BaseNavigatorAgent,
    BasePaginationAgent,
    BaseValidationAgent,
)

if TYPE_CHECKING:
    from uncertainAPI.agents.tools import BrowserTools

class CoordinatorAgent(BaseCoordinatorAgent):
    """Default coordinator agent implementation."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize coordinator agent."""
        super().__init__(name="coordinator_agent", **kwargs)

class NavigatorAgent(BaseNavigatorAgent):
    """Default navigator agent implementation."""

    def __init__(self, browser_tools: BrowserTools, **kwargs: Any) -> None:
        """Initialize navigator agent.

        Args:
            browser_tools: Browser tools instance.
            **kwargs: Additional configuration.
        """
        super().__init__(name="navigator_agent", **kwargs)
        self.browser_tools = browser_tools

    def get_tools(self) -> list[Any]:
        """Get browser navigation tools."""
        return [
            self.browser_tools.navigate_to_url,
            self.browser_tools.click_element,
            self.browser_tools.fill_input,
            self.browser_tools.take_screenshot,
            self.browser_tools.detect_captcha,
        ]

class ExtractionAgent(BaseExtractionAgent):
    """Default extraction agent implementation."""

    def __init__(self, browser_tools: BrowserTools, **kwargs: Any) -> None:
        """Initialize extraction agent.

        Args:
            browser_tools: Browser tools instance.
            **kwargs: Additional configuration.
        """
        super().__init__(name="extraction_agent", **kwargs)
        self.browser_tools = browser_tools

    def get_tools(self) -> list[Any]:
        """Get data extraction tools."""
        return [
            self.browser_tools.get_page_html,
            self.browser_tools.extract_structured_data,
        ]

class ValidationAgent(BaseValidationAgent):
    """Default validation agent implementation."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize validation agent."""
        super().__init__(name="validation_agent", **kwargs)

class PaginationAgent(BasePaginationAgent):
    """Default pagination agent implementation."""

    def __init__(self, browser_tools: BrowserTools, **kwargs: Any) -> None:
        """Initialize pagination agent.

        Args:
            browser_tools: Browser tools instance.
            **kwargs: Additional configuration.
        """
        super().__init__(name="pagination_agent", **kwargs)
        self.browser_tools = browser_tools

    def get_tools(self) -> list[Any]:
        """Get pagination detection tools."""
        return [
            self.browser_tools.detect_pagination,
            self.browser_tools.click_element,
        ]



