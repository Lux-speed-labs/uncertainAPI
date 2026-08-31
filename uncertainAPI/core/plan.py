"""Serializable integration execution plan."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from uncertainAPI.core.specs import IntegrationSpec


class IntegrationPlan(BaseModel):
    """Portable plan executed by the OSS runtime.

    The private CertainAPI compiler may generate these plans, while OSS users
    can author them manually. The runtime does not need to know how a plan was
    produced.
    """

    ir_version: int = 1
    integration_id: str
    plan_version: str
    integration: IntegrationSpec
    metadata: dict[str, Any] = Field(default_factory=dict)
