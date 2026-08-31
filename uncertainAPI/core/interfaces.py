"""Extension protocols for uncertainAPI.

The core runtime depends on these interfaces rather than concrete vendors or
frameworks. Third parties can implement them without modifying uncertainAPI.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from uncertainAPI.core.specs import ContractSpec, MappingSpec, SourceSpec
from uncertainAPI.core.types import ExecutionContext, ExecutionResult, RawPayload


@runtime_checkable
class SourceAdapter(Protocol):
    """Acquire raw data from one family of sources."""

    def supports(self, source: SourceSpec) -> bool:
        """Return whether this adapter can execute the source specification."""
        ...

    async def fetch(self, source: SourceSpec, context: ExecutionContext) -> RawPayload:
        """Acquire and return a raw source payload."""
        ...


@runtime_checkable
class SourceAdapterResolver(Protocol):
    """Select the adapter/provider that should execute a source."""

    async def resolve(
        self,
        source: SourceSpec,
        adapters: Sequence[SourceAdapter],
        context: ExecutionContext,
    ) -> SourceAdapter:
        ...


@runtime_checkable
class MappingEngine(Protocol):
    """Transform raw source payloads into canonical record candidates."""

    async def map(
        self,
        payload: RawPayload,
        mapping: MappingSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class ContractValidator(Protocol):
    """Validate canonical records against a stable contract."""

    async def validate(
        self,
        records: Sequence[dict[str, Any]],
        contract: ContractSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class RuntimeObserver(Protocol):
    """Observe execution without coupling the runtime to a telemetry vendor."""

    async def started(self, context: ExecutionContext) -> None:
        ...

    async def succeeded(
        self,
        context: ExecutionContext,
        result: ExecutionResult,
    ) -> None:
        ...

    async def retrying(self, context: ExecutionContext, error: Exception) -> None:
        ...

    async def failed(self, context: ExecutionContext, error: Exception) -> None:
        ...


@runtime_checkable
class ArtifactStore(Protocol):
    """Persist and retrieve large or immutable runtime artifacts."""

    async def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Persist bytes and return an opaque artifact reference."""
        ...

    async def get(self, reference: str) -> bytes:
        """Retrieve bytes by opaque artifact reference."""
        ...


@runtime_checkable
class PlanRegistry(Protocol):
    """Persistence boundary for compiled integration plans."""

    async def get(self, integration_id: str, version: str | None = None) -> Any:
        ...

    async def put(self, plan: Any) -> None:
        ...


@runtime_checkable
class CheckpointStore(Protocol):
    """Persist incremental execution state without coupling to a backend."""

    async def get(self, integration_id: str, key: str) -> Any | None:
        ...

    async def set(self, integration_id: str, key: str, value: Any) -> None:
        ...


@runtime_checkable
class SecretResolver(Protocol):
    """Resolve an opaque secret reference at execution time."""

    async def resolve(self, reference: str) -> Any:
        ...


@runtime_checkable
class DestinationAdapter(Protocol):
    """Deliver validated canonical records to an external destination."""

    def supports(self, destination: dict[str, Any]) -> bool:
        ...

    async def deliver(
        self,
        records: Sequence[dict[str, Any]],
        destination: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        ...


@runtime_checkable
class RateLimiter(Protocol):
    """Wait until a named execution scope is permitted to continue."""

    async def acquire(self, key: str, *, cost: float = 1.0) -> None:
        ...


@runtime_checkable
class JobDispatcher(Protocol):
    """Dispatch an integration execution without coupling to a queue vendor."""

    async def dispatch(
        self,
        integration_id: str,
        *,
        plan_version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        ...
