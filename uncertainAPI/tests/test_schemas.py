"""Tests for extraction schemas."""

from __future__ import annotations

from typing import Optional

import pytest
from pydantic import ValidationError

from uncertainAPI.schemas import ExtractionSchema

class TestProductSchema(ExtractionSchema):
    """Test schema for product data."""

    name: str
    price: float
    description: str
    in_stock: bool
    rating: Optional[float] = None

class TestExtractionSchema:
    """Test extraction schema functionality."""

    def test_schema_creation(self) -> None:
        """Test creating schema instance."""
        product = TestProductSchema(
            name="Test Product",
            price=29.99,
            description="A test product",
            in_stock=True,
        )

        assert product.name == "Test Product"
        assert product.price == 29.99
        assert product.description == "A test product"
        assert product.in_stock is True
        assert product.rating is None

    def test_schema_validation(self) -> None:
        """Test schema validation."""
        with pytest.raises(ValidationError):
            TestProductSchema(
                name="Test",
                price="invalid",  # Should be float
                description="Test",
                in_stock=True,
            )

    def test_get_json_schema(self) -> None:
        """Test JSON schema generation."""
        schema = TestProductSchema.get_json_schema()

        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "price" in schema["properties"]
        assert schema["properties"]["price"]["type"] == "number"

    def test_get_extraction_prompt(self) -> None:
        """Test extraction prompt generation."""
        prompt = TestProductSchema.get_extraction_prompt()

        assert "name" in prompt
        assert "price" in prompt
        assert "description" in prompt
        assert "[REQUIRED]" in prompt
        assert "[OPTIONAL]" in prompt

    def test_schema_serialization(self) -> None:
        """Test schema serialization."""
        product = TestProductSchema(
            name="Test Product",
            price=29.99,
            description="A test product",
            in_stock=True,
            rating=4.5,
        )

        data = product.model_dump()
        assert data["name"] == "Test Product"
        assert data["price"] == 29.99
        assert data["rating"] == 4.5

        # Test JSON serialization
        json_str = product.model_dump_json()
        assert "Test Product" in json_str



