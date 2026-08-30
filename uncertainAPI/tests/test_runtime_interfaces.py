"""Tests for the framework-independent runtime."""

from __future__ import annotations

from typing import Any, Sequence

import pytest

from uncertainAPI.core.plan import IntegrationPlan
from uncertainAPI.core.specs import (
    ContractSpec,
    IntegrationSpec,
    MappingSpec,
    SourceSpec,
)
from uncertainAPI.core.types import ExecutionContext, RawPayload
from uncertainAPI.runtime import IntegrationRuntime


class FakeAdapter:
    def supports(self, source: SourceSpec) -> bool:
        return source.type == "fake"

    async def fetch(self, source: SourceSpec, context: ExecutionContext) -> RawPayload:
        return RawPayload(data={"items": [{"sku": "ABC", "price": 42}]})


class FakeMapper:
    async def map(
        self,
        payload: RawPayload,
        mapping: MappingSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        item = payload.data["items"][0]
        return [{"product_id": item["sku"], "price": item["price"]}]


class FakeValidator:
    async def validate(
        self,
        records: Sequence[dict[str, Any]],
        contract: ContractSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        assert contract.name == "ProductOffer"
        return list(records)


@pytest.mark.asyncio
async def test_runtime_executes_through_interfaces() -> None:
    plan = IntegrationPlan(
        integration_id="integration-1",
        plan_version="1",
        integration=IntegrationSpec(
            source=SourceSpec(type="fake", endpoint="memory://products"),
            contract=ContractSpec(
                name="ProductOffer",
                version="1",
                schema={
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "price": {"type": "number"},
                    },
                    "required": ["product_id", "price"],
                },
            ),
            mapping=MappingSpec(fields={"product_id": "$.sku", "price": "$.price"}),
        ),
    )

    runtime = IntegrationRuntime(
        adapters=[FakeAdapter()],
        mapper=FakeMapper(),
        validator=FakeValidator(),
    )

    result = await runtime.execute(plan)

    assert result.records == [{"product_id": "ABC", "price": 42}]
