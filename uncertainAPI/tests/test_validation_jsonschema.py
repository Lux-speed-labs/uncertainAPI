"""Tests for JSON Schema contract validation."""

import pytest

from uncertainAPI.core.specs import ContractSpec
from uncertainAPI.core.types import ExecutionContext
from uncertainAPI.validation import ContractValidationError, JSONSchemaContractValidator


@pytest.mark.asyncio
async def test_jsonschema_validator_accepts_valid_records() -> None:
    validator = JSONSchemaContractValidator()
    contract = ContractSpec(
        name="ProductOffer",
        version="1",
        schema={
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "price": {"type": "number"},
            },
            "required": ["product_id", "price"],
            "additionalProperties": False,
        },
    )
    records = [{"product_id": "A-1", "price": 42.5}]
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    assert await validator.validate(records, contract, context) == records


@pytest.mark.asyncio
async def test_jsonschema_validator_reports_record_and_path() -> None:
    validator = JSONSchemaContractValidator()
    contract = ContractSpec(
        name="ProductOffer",
        version="1",
        schema={
            "type": "object",
            "properties": {"price": {"type": "number"}},
            "required": ["price"],
        },
    )
    context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

    with pytest.raises(ContractValidationError) as exc_info:
        await validator.validate([{"price": "not-a-number"}], contract, context)

    assert exc_info.value.record_index == 0
    assert exc_info.value.path == "price"
