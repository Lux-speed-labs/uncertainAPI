"""Tests for deterministic JMESPath mapping."""

import pytest

from uncertainAPI.core.specs import MappingSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload
from uncertainAPI.mapping import JMESPathMappingEngine, MappingExecutionError


@pytest.mark.asyncio
async def test_jmespath_mapping_selects_records_maps_fields_and_transforms() -> None:
    engine = JMESPathMappingEngine()
    payload = RawPayload(
        data={
            "items": [
                {"sku": " A-1 ", "selling": {"price": "42.50"}, "active": "yes"},
                {"sku": "B-2", "selling": {"price": "7"}, "active": "false"},
            ]
        }
    )
    mapping = MappingSpec(
        records_selector="items",
        fields={
            "product_id": "sku",
            "price": "selling.price",
            "available": "active",
        },
        transforms={
            "product_id": "strip",
            "price": "float",
            "available": "bool",
        },
    )
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    records = await engine.map(payload, mapping, context)

    assert records == [
        {"product_id": "A-1", "price": 42.5, "available": True},
        {"product_id": "B-2", "price": 7.0, "available": False},
    ]


@pytest.mark.asyncio
async def test_jmespath_mapping_rejects_scalar_record_selection() -> None:
    engine = JMESPathMappingEngine()
    payload = RawPayload(data={"count": 2})
    mapping = MappingSpec(records_selector="count")
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    with pytest.raises(MappingExecutionError):
        await engine.map(payload, mapping, context)
