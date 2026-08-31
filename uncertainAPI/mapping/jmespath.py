"""JMESPath-backed deterministic mapping engine."""

from __future__ import annotations

import importlib
from typing import Any

from uncertainAPI.core.specs import MappingSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload


class MappingExecutionError(ValueError):
    """Raised when a mapping plan cannot be executed deterministically."""


class JMESPathMappingEngine:
    """Execute record selection and field mappings with JMESPath."""

    async def map(
        self,
        payload: RawPayload,
        mapping: MappingSpec,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        selected: object = payload.data
        if mapping.records_selector:
            selected = _search(mapping.records_selector, payload.data)

        source_records = _coerce_records(selected)
        mapped_records: list[dict[str, Any]] = []

        for record in source_records:
            if mapping.fields:
                mapped = {
                    target: _search(expression, record)
                    for target, expression in mapping.fields.items()
                }
            else:
                mapped = _copy_record(record)

            for field, transform in mapping.transforms.items():
                if field not in mapped:
                    raise MappingExecutionError(
                        f"Transform references unmapped field {field!r}"
                    )
                mapped[field] = _apply_transform(mapped[field], transform)

            mapped_records.append(mapped)

        return mapped_records


def _search(expression: str, data: object) -> object:
    try:
        module = importlib.import_module("jmespath")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "JMESPathMappingEngine requires the optional mapping dependency. "
            "Install with: pip install 'uncertainapi[mapping]'"
        ) from exc

    search = getattr(module, "search")
    result: object = search(expression, data)
    return result


def _coerce_records(value: object) -> list[object]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        return [value]
    raise MappingExecutionError(
        "Record selector must resolve to an object or a list of objects"
    )


def _copy_record(record: object) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise MappingExecutionError(
            "Pass-through mapping requires each selected record to be an object"
        )
    return {str(key): value for key, value in record.items()}


def _apply_transform(value: object, transform: object) -> object:
    if not isinstance(transform, str):
        raise MappingExecutionError("Phase 2 transforms must be named strings")

    name = transform.lower()
    if name in {"str", "string"}:
        return "" if value is None else str(value)
    if name in {"int", "integer"}:
        try:
            return int(str(value))
        except (TypeError, ValueError) as exc:
            raise MappingExecutionError(f"Cannot convert {value!r} to integer") from exc
    if name in {"float", "number"}:
        try:
            return float(str(value))
        except (TypeError, ValueError) as exc:
            raise MappingExecutionError(f"Cannot convert {value!r} to number") from exc
    if name in {"bool", "boolean"}:
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        raise MappingExecutionError(f"Cannot convert {value!r} to boolean")
    if name == "lower":
        return str(value).lower()
    if name == "upper":
        return str(value).upper()
    if name == "strip":
        return str(value).strip()

    raise MappingExecutionError(f"Unsupported transform {transform!r}")
