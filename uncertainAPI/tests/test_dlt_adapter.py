"""Integration tests for the generic dlt connector adapter."""

from __future__ import annotations

import dlt
import pytest

from uncertainAPI.adapters import (
    DltSourceAdapter,
    DltSourceConfigurationError,
    StaticDltSourceRegistry,
)
from uncertainAPI.core.plan import IntegrationPlan
from uncertainAPI.core.specs import ContractSpec, IntegrationSpec, MappingSpec, SourceSpec
from uncertainAPI.core.types import ExecutionContext
from uncertainAPI.mapping import JMESPathMappingEngine
from uncertainAPI.runtime import IntegrationRuntime
from uncertainAPI.validation import JSONSchemaContractValidator


@dlt.resource(name="products")
def products_resource():
    yield [
        {"vendor_sku": "SKU-1", "selling_price": "19.99", "stock": "4"},
        {"vendor_sku": "SKU-2", "selling_price": "7.50", "stock": "0"},
    ]


@dlt.resource(name="orders")
def orders_resource():
    yield [{"order_id": "O-1"}]


@dlt.source
def supplier_source():
    return products_resource(), orders_resource()


@dlt.source
def single_resource_source():
    return products_resource()


def _adapter() -> DltSourceAdapter:
    return DltSourceAdapter(
        registry=StaticDltSourceRegistry(
            {
                "supplier": supplier_source,
                "single": single_resource_source,
            }
        )
    )


@pytest.mark.asyncio
async def test_dlt_adapter_discovers_resources_without_source_specific_code() -> None:
    adapter = _adapter()
    source = SourceSpec(
        type="dlt",
        endpoint="dlt://supplier",
        options={"factory": "supplier"},
    )

    assert await adapter.resources(source) == ("products", "orders")


@pytest.mark.asyncio
async def test_dlt_adapter_requires_resource_for_multi_resource_source() -> None:
    adapter = _adapter()
    source = SourceSpec(
        type="dlt",
        endpoint="dlt://supplier",
        options={"factory": "supplier"},
    )
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    with pytest.raises(DltSourceConfigurationError):
        await adapter.fetch(source, context)


@pytest.mark.asyncio
async def test_dlt_adapter_materializes_selected_resource_and_limit() -> None:
    adapter = _adapter()
    source = SourceSpec(
        type="dlt",
        endpoint="dlt://supplier",
        options={
            "factory": "supplier",
            "resource": "products",
            "max_items": 1,
        },
    )
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    payload = await adapter.fetch(source, context)

    assert payload.data == [
        {"vendor_sku": "SKU-1", "selling_price": "19.99", "stock": "4"}
    ]
    assert payload.metadata["connector"] == "dlt"
    assert payload.metadata["resource"] == "products"
    assert payload.metadata["record_count"] == 1


@pytest.mark.asyncio
async def test_dlt_source_runs_through_standard_mapping_and_validation() -> None:
    adapter = _adapter()
    plan = IntegrationPlan(
        integration_id="supplier-products",
        plan_version="3",
        integration=IntegrationSpec(
            source=SourceSpec(
                type="dlt",
                endpoint="dlt://supplier",
                options={
                    "factory": "supplier",
                    "resource": "products",
                },
            ),
            contract=ContractSpec(
                name="ProductOffer",
                version="1",
                schema={
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "price": {"type": "number"},
                        "quantity": {"type": "integer"},
                    },
                    "required": ["product_id", "price", "quantity"],
                    "additionalProperties": False,
                },
            ),
            mapping=MappingSpec(
                fields={
                    "product_id": "vendor_sku",
                    "price": "selling_price",
                    "quantity": "stock",
                },
                transforms={
                    "price": "float",
                    "quantity": "int",
                },
            ),
        ),
    )
    runtime = IntegrationRuntime(
        adapters=[adapter],
        mapper=JMESPathMappingEngine(),
        validator=JSONSchemaContractValidator(),
    )

    result = await runtime.execute(plan)

    assert result.records == [
        {"product_id": "SKU-1", "price": 19.99, "quantity": 4},
        {"product_id": "SKU-2", "price": 7.5, "quantity": 0},
    ]
    assert result.metadata["connector"] == "dlt"
