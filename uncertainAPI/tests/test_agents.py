"""Tests for agent system."""

from __future__ import annotations

from uncertainAPI.agents.base import (
    BaseCoordinatorAgent,
    BaseNavigatorAgent,
    BaseExtractionAgent,
)

class TestAgentBase:
    """Test base agent classes."""

    def test_coordinator_agent(self) -> None:
        """Test coordinator agent."""
        agent = BaseCoordinatorAgent(name="test_coordinator")

        assert agent.name == "test_coordinator"
        assert "coordinate" in agent.get_system_message().lower()
        assert "workflow" in agent.get_description().lower()

    def test_navigator_agent(self) -> None:
        """Test navigator agent."""
        agent = BaseNavigatorAgent(name="test_navigator")

        assert agent.name == "test_navigator"
        assert "navigate" in agent.get_system_message().lower()
        assert "browser" in agent.get_description().lower()

    def test_extraction_agent(self) -> None:
        """Test extraction agent."""
        agent = BaseExtractionAgent(name="test_extractor")

        assert agent.name == "test_extractor"
        assert "extract" in agent.get_system_message().lower()
        assert "data" in agent.get_description().lower()



