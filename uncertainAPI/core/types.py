"""Runtime-neutral value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class ExecutionContext:
    """Per-run context propagated through runtime extension points."""

    execution_id: str
    integration_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RawPayload:
    """Uninterpreted payload returned by a source adapter."""

    data: Any
    content_type: str | None = None
    status_code: int | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionResult:
    """Validated canonical output from an integration execution."""

    records: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
