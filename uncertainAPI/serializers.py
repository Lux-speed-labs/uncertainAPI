"""DRF serializer integration for Pydantic schemas."""

from __future__ import annotations

from loguru import logger
from typing import Any, Type

from pydantic import BaseModel

def pydantic_to_drf_serializer(schema_class: Type[BaseModel]) -> Type[Any]:
    """Convert a Pydantic schema to a DRF serializer.

    Args:
        schema_class: Pydantic model class.

    Returns:
        DRF serializer class.

    Raises:
        ImportError: If DRF is not installed.
    """
    try:
        from rest_framework import serializers
    except ImportError as exc:
        raise ImportError("DRF not installed") from exc

    # Get Pydantic schema
    json_schema = schema_class.model_json_schema()
    properties = json_schema.get("properties", {})
    required = set(json_schema.get("required", []))

    # Map Pydantic types to DRF fields
    type_mapping = {
        "string": serializers.CharField,
        "integer": serializers.IntegerField,
        "number": serializers.FloatField,
        "boolean": serializers.BooleanField,
        "array": serializers.ListField,
        "object": serializers.DictField,
    }

    # Build serializer fields
    serializer_fields: dict[str, Any] = {}

    for field_name, field_info in properties.items():
        field_type = field_info.get("type", "string")
        is_required = field_name in required
        description = field_info.get("description", "")

        drf_field_class = type_mapping.get(field_type, serializers.CharField)
        field_kwargs = {
            "required": is_required,
            "help_text": description,
        }

        if not is_required:
            field_kwargs["allow_null"] = True
            field_kwargs["default"] = None

        serializer_fields[field_name] = drf_field_class(**field_kwargs)

    # Create serializer class dynamically
    serializer_class = type(
        f"{schema_class.__name__}Serializer",
        (serializers.Serializer,),
        serializer_fields,
    )

    logger.debug(
        "serializer.created",
        extra={"schema": schema_class.__name__, "fields": len(serializer_fields)},
    )

    return serializer_class



