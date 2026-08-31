"""Default source-adapter resolution strategies."""

from __future__ import annotations

from collections.abc import Sequence

from uncertainAPI.core.interfaces import SourceAdapter, SourceAdapterResolver
from uncertainAPI.core.specs import SourceSpec
from uncertainAPI.core.types import ExecutionContext


class AdapterNotFoundError(RuntimeError):
    """Raised when no configured adapter can execute a source."""


class FirstMatchAdapterResolver(SourceAdapterResolver):
    """Simple OSS resolver that selects the first compatible adapter."""

    async def resolve(
        self,
        source: SourceSpec,
        adapters: Sequence[SourceAdapter],
        context: ExecutionContext,
    ) -> SourceAdapter:
        for adapter in adapters:
            if adapter.supports(source):
                return adapter
        raise AdapterNotFoundError(
            f"No source adapter registered for source type {source.type!r}"
        )
