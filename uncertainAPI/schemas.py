"""Extraction schemas for uncertainAPI."""

from __future__ import annotations

from loguru import logger
from typing import Any

from pydantic import BaseModel

class ExtractionSchema(BaseModel):
    """Base class for data extraction schemas.

    Users subclass this to define the structure of data they want to extract.

    Example:
        class ProductSchema(ExtractionSchema):
            name: str
            price: float
            description: str
            in_stock: bool
            rating: Optional[float] = None
    """

    @classmethod
    def get_json_schema(cls) -> dict[str, Any]:
        """Get JSON schema for AI structured output.

        Returns:
            JSON schema dictionary suitable for OpenAI structured output.
        """
        return cls.model_json_schema()

    @classmethod
    def get_extraction_prompt(cls) -> str:
        """Generate a prompt describing the data to extract.

        Returns:
            Prompt string for AI agents.
        """
        schema = cls.get_json_schema()
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        prompt_parts = ["Extract the following fields from the page:"]

        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "string")
            field_desc = field_info.get("description", "")
            is_required = field_name in required

            req_marker = "[REQUIRED]" if is_required else "[OPTIONAL]"
            desc_str = f" - {field_desc}" if field_desc else ""
            prompt_parts.append(f"- {field_name} ({field_type}) {req_marker}{desc_str}")

        return "\n".join(prompt_parts)

    class Config:
        """Pydantic config."""

        # Allow extra fields during extraction
        extra = "ignore"



