"""Base classes for extractor agents."""

from __future__ import annotations

from loguru import logger
from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseExtractorAgent(ABC):
    """Abstract base class for extractor agents.

    All specialized agents (Coordinator, Navigator, Extractor, etc.)
    should inherit from this and implement their specific logic.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize agent.

        Args:
            name: Agent name.
            **kwargs: Additional configuration.
        """
        self.name = name
        self.config = kwargs

    @abstractmethod
    def get_system_message(self) -> str:
        """Get the system message for this agent.

        Returns:
            System message string.
        """
        ...

    @abstractmethod
    def get_description(self) -> str:
        """Get the agent description for group chat selection.

        Returns:
            Description string.
        """
        ...

    def get_tools(self) -> list[Any]:
        """Get tools this agent can use.

        Returns:
            List of tool functions.
        """
        return []

class BaseCoordinatorAgent(BaseExtractorAgent):
    """Base class for coordinator agents."""

    def get_system_message(self) -> str:
        """Get coordinator system message."""
        return (
            "You coordinate the web extraction workflow. "
            "Delegate tasks to specialized agents (Navigator, Extractor, Validator). "
            "Ensure all required data is extracted and validated before completion. "
            "Make high-level decisions about workflow execution and error handling."
        )

    def get_description(self) -> str:
        """Get coordinator description."""
        return "Coordinates the overall extraction workflow and delegates to specialists."

class BaseNavigatorAgent(BaseExtractorAgent):
    """Base class for navigator agents."""

    def get_system_message(self) -> str:
        """Get navigator system message."""
        return (
            "You navigate websites using browser tools. "
            "Handle authentication, solve captchas, and perform page interactions. "
            "Use the provided browser tools (navigate, click, fill, screenshot) to complete tasks. "
            "Report any navigation issues or obstacles encountered."
        )

    def get_description(self) -> str:
        """Get navigator description."""
        return "Handles web navigation, authentication, captchas, and browser interactions."

class BaseExtractionAgent(BaseExtractorAgent):
    """Base class for extraction agents."""

    def get_system_message(self) -> str:
        """Get extraction system message."""
        return (
            "You extract structured data from web pages matching the provided schema. "
            "Analyze HTML content and extract all required fields accurately. "
            "Ensure data types match the schema. "
            "Report if required fields cannot be found or extracted."
        )

    def get_description(self) -> str:
        """Get extraction description."""
        return "Extracts structured data from pages according to defined schemas."

class BaseValidationAgent(BaseExtractorAgent):
    """Base class for validation agents."""

    def get_system_message(self) -> str:
        """Get validation system message."""
        return (
            "You validate extracted data for quality, completeness, and schema compliance. "
            "Check that all required fields are present and correctly typed. "
            "Identify missing data, format errors, or quality issues. "
            "Request re-extraction if data quality is insufficient."
        )

    def get_description(self) -> str:
        """Get validation description."""
        return "Validates extracted data for completeness, quality, and schema compliance."

class BasePaginationAgent(BaseExtractorAgent):
    """Base class for pagination agents."""

    def get_system_message(self) -> str:
        """Get pagination system message."""
        return (
            "You detect and handle paginated content. "
            "Identify 'next' buttons, page links, or infinite scroll patterns. "
            "Coordinate navigation through all pages until no more content is available. "
            "Track pagination state to avoid infinite loops."
        )

    def get_description(self) -> str:
        """Get pagination description."""
        return "Detects pagination patterns and coordinates multi-page data extraction."

