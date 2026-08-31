"""JSON Schema contract validation using the jsonschema package."""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from typing import Any

from uncertainAPI.core.specs import ContractSpec
from uncertainAPI.core.types import ExecutionContext


class ContractValidationError(ValueError):
    """Raised when a canonical record violates its contract."""

    def __init__(self, *, record_index: int, path: str, message: str) -> None:
        location = path or "<record>"
        super().__init__(
            f"Record {record_index} failed contract validation at {location}: {message}"
        )
        self.record_index = record_index
        self.path = path
        self.validation_message = message


class JSONSchemaContractValidator:
    """Validate canonical records against a Draft 2020-12 JSON Schema."""

    async def validate(
        self,
        records: Sequence[dict[str, Any]],
        contract: ContractSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        try:
            module = importlib.import_module("jsonschema")
        except ModuleNotFoundError as exc:
            raise ImportError(
                "JSONSchemaContractValidator requires the optional validation dependency. "
                "Install with: pip install 'uncertainapi[validation]'"
            ) from exc

        validator_type = module.Draft202012Validator
        validator_type.check_schema(contract.json_schema)
        validator = validator_type(contract.json_schema)

        for index, record in enumerate(records):
            errors = list(validator.iter_errors(record))
            if not errors:
                continue
            error = min(
                errors,
                key=lambda item: tuple(str(part) for part in item.absolute_path),
            )
            path = ".".join(str(part) for part in error.absolute_path)
            raise ContractValidationError(
                record_index=index,
                path=path,
                message=str(error.message),
            )

        return list(records)
