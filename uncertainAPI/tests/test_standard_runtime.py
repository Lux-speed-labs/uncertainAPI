"""End-to-end deterministic runtime test using reusable engines."""

import pytest

from uncertainAPI.core.plan import IntegrationPlan
from uncertainAPI.core.specs import ContractSpec, IntegrationSpec, MappingSpec, SourceSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload
from uncertainAPI.mapping import JMESPathMappingEngine
from uncertainAPI.runtime import IntegrationRuntime
from uncertainAPI.validation import JSONSchemaContractValidator


class SupplierAdapter:
    def supports(self, source: SourceSpec) -> bool:
        return source.type == "supplier-fixture"

    async def fetch(self, source: SourceSpec, context: ExecutionContext) -> RawPayload:
        return RawPayload(
            data={
                "catalog": [
                    {"vendor_sku": "SKU-1", "selling_price": "19.99", "stock": "4"}
                ]
            },
            metadata={"provider": "fixture"},
        )


@pytest.mark.asyncio
async def test_runtime_normalizes_supplier_payload_to_stable_contract() -> None:
    plan = IntegrationPlan(
        integration_id="supplier-catalog",
        plan_version="2",
        integration=IntegrationSpec(
            source=SourceSpec(
                type="supplier-fixture",
                endpoint="fixture://supplier",
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
                records_selector="catalog",
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
        adapters=[SupplierAdapter()],
        mapper=JMESPathMappingEngine(),
        validator=JSONSchemaContractValidator(),
    )

    result = await runtime.execute(plan, metadata={"tenant_id": "tenant-1"})

    assert result.records == [{"product_id": "SKU-1", "price": 19.99, "quantity": 4}]
    assert result.metadata["provider"] == "fixture"
    assert result.metadata["plan_version"] == "2"
