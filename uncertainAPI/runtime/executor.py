"""Framework-independent IntegrationPlan executor."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from uncertainAPI.core.interfaces import (
    ContractValidator,
    MappingEngine,
    RuntimeObserver,
    SourceAdapter,
)
from uncertainAPI.core.plan import IntegrationPlan
from uncertainAPI.core.types import ExecutionContext, ExecutionResult


class AdapterNotFoundError(RuntimeError):
    """Raised when no registered source adapter supports a source."""


class NullRuntimeObserver:
    """No-op observer used when observability is not configured."""

    async def started(self, context: ExecutionContext) -> None:
        pass

    async def succeeded(
        self, context: ExecutionContext, result: ExecutionResult
    ) -> None:
        pass

    async def retrying(self, context: ExecutionContext, error: Exception) -> None:
        pass

    async def failed(self, context: ExecutionContext, error: Exception) -> None:
        pass


class IntegrationRuntime:
    """Execute plans using injected extension interfaces.

    No Django, DRF, browser vendor, scheduler, telemetry provider, or AI
    framework is required by this class.
    """

    def __init__(
        self,
        *,
        adapters: Sequence[SourceAdapter],
        mapper: MappingEngine,
        validator: ContractValidator,
        observer: RuntimeObserver | None = None,
    ) -> None:
        self._adapters = tuple(adapters)
        self._mapper = mapper
        self._validator = validator
        self._observer = observer or NullRuntimeObserver()

    def _adapter_for(self, plan: IntegrationPlan) -> SourceAdapter:
        source = plan.integration.source
        for adapter in self._adapters:
            if adapter.supports(source):
                return adapter
        raise AdapterNotFoundError(
            f"No source adapter registered for source type {source.type!r}"
        )

    async def execute(
        self,
        plan: IntegrationPlan,
        *,
        execution_id: str | None = None,
        metadata: dict | None = None,
    ) -> ExecutionResult:
        context = ExecutionContext(
            execution_id=execution_id or str(uuid.uuid4()),
            integration_id=plan.integration_id,
            metadata=dict(metadata or {}),
        )
        await self._observer.started(context)

        try:
            adapter = self._adapter_for(plan)
            payload = await adapter.fetch(plan.integration.source, context)
            records = await self._mapper.map(
                payload,
                plan.integration.mapping,
                context,
            )
            validated = await self._validator.validate(
                records,
                plan.integration.contract,
                context,
            )
            result = ExecutionResult(
                records=validated,
                metadata={
                    "plan_version": plan.plan_version,
                    "ir_version": plan.ir_version,
                    **payload.metadata,
                },
            )
            await self._observer.succeeded(context, result)
            return result
        except Exception as exc:
            await self._observer.failed(context, exc)
            raise
