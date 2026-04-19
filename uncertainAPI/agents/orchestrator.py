"""Extractor orchestrator using AG2 multi-agent system."""

from __future__ import annotations

import json
from loguru import logger
from typing import Any, Optional, Type

from pydantic import BaseModel

from uncertainAPI.agents.base import BaseExtractorAgent
from uncertainAPI.agents.roles import (
    CoordinatorAgent,
    ExtractionAgent,
    NavigatorAgent,
    PaginationAgent,
    ValidationAgent,
)
from uncertainAPI.agents.tools import BrowserTools
from uncertainAPI.auth.base import AuthHandler
from uncertainAPI.browsers.base import BrowserBackend
from uncertainAPI.exceptions import ConfigurationError, ExtractionError

class ExtractorOrchestrator:
    """Orchestrates multi-agent web extraction using AG2.

    This is the core orchestration class that coordinates specialized agents
    to navigate, extract, and validate data from websites.

    Users can override agents, patterns, and tools for custom workflows.
    """

    def __init__(
        self,
        browser: BrowserBackend,
        ai_provider: Any,
        schema_class: Type[BaseModel],
        auth_handler: Optional[AuthHandler] = None,
        enable_pagination: bool = False,
        max_rounds: int = 20,
        custom_agents: Optional[list[BaseExtractorAgent]] = None,
        orchestration_pattern: str = "auto",
        **kwargs: Any,
    ) -> None:
        """Initialize extractor orchestrator.

        Args:
            browser: Browser backend instance.
            ai_provider: AI provider instance.
            schema_class: Pydantic schema class for extraction.
            auth_handler: Optional authentication handler.
            enable_pagination: Whether to enable pagination handling.
            max_rounds: Maximum conversation rounds for agents.
            custom_agents: Optional list of custom agents (overrides defaults).
            orchestration_pattern: Pattern type ('auto', 'sequential', 'round_robin').
            **kwargs: Additional orchestration options.
        """
        self.browser = browser
        self.ai_provider = ai_provider
        self.schema_class = schema_class
        self.auth_handler = auth_handler
        self.enable_pagination = enable_pagination
        self.max_rounds = max_rounds
        self.orchestration_pattern = orchestration_pattern
        self.config = kwargs

        # Initialize browser tools
        self.browser_tools = BrowserTools(browser)

        # Initialize agents
        if custom_agents:
            self.agents = custom_agents
        else:
            self.agents = self._create_default_agents()

        logger.info(
            "orchestrator.initialized",
            extra={
                "agent_count": len(self.agents),
                "pattern": orchestration_pattern,
                "pagination_enabled": enable_pagination,
            },
        )

    def _create_default_agents(self) -> list[BaseExtractorAgent]:
        """Create default agent lineup.

        Returns:
            List of agent instances.
        """
        agents: list[BaseExtractorAgent] = [
            CoordinatorAgent(),
            NavigatorAgent(browser_tools=self.browser_tools),
            ExtractionAgent(browser_tools=self.browser_tools),
            ValidationAgent(),
        ]

        if self.enable_pagination:
            agents.append(PaginationAgent(browser_tools=self.browser_tools))

        return agents

    def get_agents(self) -> list[BaseExtractorAgent]:
        """Get agents for orchestration.

        Override this method to customize agent lineup.

        Returns:
            List of agent instances.
        """
        return self.agents

    def get_orchestration_pattern(self) -> str:
        """Get orchestration pattern.

        Override this method to customize pattern selection.

        Returns:
            Pattern name.
        """
        return self.orchestration_pattern

    async def extract(self, url: str) -> list[BaseModel]:
        """Extract data from URL using multi-agent orchestration.

        Args:
            url: URL to extract.

        Returns:
            List of extracted data instances matching schema.

        Raises:
            ExtractionError: If extraction fails.
        """
        logger.info("orchestrator.extract.start", extra={"url": url})

        try:
            # Import AG2 components
            try:
                from autogen import ConversableAgent, LLMConfig, register_function
                from autogen.agentchat import run_group_chat
                from autogen.agentchat.group.patterns import AutoPattern
            except ImportError as exc:
                raise ConfigurationError(
                    "AG2 not installed. Install with: pip install ag2"
                ) from exc

            # Configure LLM for AG2
            llm_config = await self._build_llm_config_async()

            # Create AG2 agents from our agent definitions (async)
            ag2_agents = await self._create_ag2_agents_async(llm_config)

            # Create orchestration pattern
            coordinator = ag2_agents[0]  # First agent is coordinator
            pattern = AutoPattern(
                agents=ag2_agents,
                initial_agent=coordinator,
                group_manager_args={"name": "group_manager", "llm_config": llm_config},
            )

            # Prepare extraction task message
            task_message = await self._build_extraction_prompt_async(url)

            # Handle authentication if needed
            if self.auth_handler:
                logger.debug("orchestrator.auth.start")
                is_authenticated = await self.auth_handler.is_authenticated(self.browser)
                if not is_authenticated:
                    await self.auth_handler.authenticate(self.browser)
                logger.info("orchestrator.auth.complete")

            # Run multi-agent conversation (AG2's run_group_chat is sync, run in executor)
            logger.debug("orchestrator.agents.start", extra={"max_rounds": self.max_rounds})
            
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: run_group_chat(
                    pattern=pattern,
                    messages=task_message,
                    max_rounds=self.max_rounds,
                )
            )

            # Process results (sync operation, quick)
            response.process()
            final_output = response.summary

            logger.info("orchestrator.extract.complete", extra={"output_length": len(str(final_output))})

            # Parse extracted data (async)
            result = await self._parse_agent_output_async(final_output)

            return result

        except Exception as exc:
            logger.exception("orchestrator.extract.failed", extra={"url": url})
            raise ExtractionError(f"Extraction failed for {url}: {exc}") from exc
        finally:
            # Cleanup browser (async)
            await self.browser.close()

    async def _build_llm_config_async(self) -> Any:
        """Build LLM config for AG2 from our AI provider (async).

        Returns:
            LLM config dict compatible with AG2.
        """
        try:
            from autogen import LLMConfig
        except ImportError as exc:
            raise ConfigurationError("AG2 not installed") from exc

        # Get provider config (I/O operation should be async if needed)
        config_dict = {
            "model": getattr(self.ai_provider, "model", "gpt-4o"),
            "api_key": getattr(self.ai_provider, "api_key", None),
            "temperature": 0.7,
        }

        return LLMConfig.from_dict(config_dict)

    async def _create_ag2_agents_async(self, llm_config: Any) -> list[Any]:
        """Create AG2 agents from our agent definitions (async).

        Args:
            llm_config: LLM configuration.

        Returns:
            List of AG2 ConversableAgent instances.
        """
        from autogen import ConversableAgent, register_function

        ag2_agents = []
        
        for agent in self.get_agents():
            # Create AG2 agent (sync operation, fast)
            ag2_agent = ConversableAgent(
                name=agent.name,
                system_message=agent.get_system_message(),
                description=agent.get_description(),
                llm_config=llm_config,
                human_input_mode="NEVER",
            )

            # Register tools for this agent
            tools = agent.get_tools()
            for tool in tools:
                # Wrap async tools for AG2 compatibility
                wrapped_tool = self._wrap_async_tool(tool)
                register_function(
                    wrapped_tool,
                    caller=ag2_agent,
                    executor=ag2_agent,
                    description=tool.__doc__ or tool.__name__,
                )

            ag2_agents.append(ag2_agent)

        return ag2_agents

    def _wrap_async_tool(self, async_tool: Any) -> Any:
        """Wrap async tool for AG2 synchronous execution.

        AG2 expects sync functions, so we wrap async tools.

        Args:
            async_tool: Async tool function.

        Returns:
            Sync wrapper function.
        """
        import asyncio
        import inspect

        if not inspect.iscoroutinefunction(async_tool):
            # Already sync
            return async_tool

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Sync wrapper for async tool."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Already in async context, create task
                    import nest_asyncio
                    nest_asyncio.apply()
                return loop.run_until_complete(async_tool(*args, **kwargs))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(async_tool(*args, **kwargs))

        # Preserve metadata
        sync_wrapper.__name__ = async_tool.__name__
        sync_wrapper.__doc__ = async_tool.__doc__
        
        return sync_wrapper

    async def _build_extraction_prompt_async(self, url: str) -> str:
        """Build extraction prompt for agents (async).

        Args:
            url: URL to extract.

        Returns:
            Formatted prompt string.
        """
        # Get schema info (CPU-bound, sync is fine)
        schema_json = json.dumps(self.schema_class.get_json_schema())
        extraction_prompt = self.schema_class.get_extraction_prompt()

        task_message = f"""
Extract data from this URL: {url}

Schema to extract:
{extraction_prompt}

JSON Schema:
{schema_json}

Steps:
1. Navigator: Navigate to the URL and handle any auth/captcha
2. Extractor: Extract data matching the schema
3. Validator: Validate the extracted data
{'4. Pagination: Check for more pages and repeat if needed' if self.enable_pagination else ''}

Complete the extraction and return the final data.
"""
        
        return task_message

    async def _parse_agent_output_async(self, output: str) -> list[BaseModel]:
        """Parse agent output into schema instances (async).

        Args:
            output: Raw output from agents.

        Returns:
            List of validated schema instances.
        """
        # TODO: Implement robust parsing
        # For now, return placeholder
        logger.debug("orchestrator.parse.placeholder", extra={"output_length": len(str(output))})
        
        # This would normally involve:
        # 1. Extracting JSON from agent output
        # 2. Validating against schema
        # 3. Creating Pydantic instances
        
        # Placeholder implementation
        try:
            # Try to parse as JSON
            import json
            data = json.loads(str(output))
            if isinstance(data, list):
                return [self.schema_class.model_validate(item) for item in data]
            else:
                return [self.schema_class.model_validate(data)]
        except Exception as exc:
            logger.warning("orchestrator.parse.failed", extra={"error": str(exc)})
            return [self.schema_class.model_validate({})]

