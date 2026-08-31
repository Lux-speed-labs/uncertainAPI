"""Tests for the GraphQL source adapter."""

import httpx
import pytest

from uncertainAPI.adapters import GraphQLAdapter, GraphQLResponseError
from uncertainAPI.core.specs import SourceSpec
from uncertainAPI.core.types import ExecutionContext


@pytest.mark.asyncio
async def test_graphql_adapter_returns_data_document() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(
            200,
            json={"data": {"products": [{"sku": "A-1"}]}},
            headers={"content-type": "application/json"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = GraphQLAdapter(client=client)
        source = SourceSpec(
            type="graphql",
            endpoint="https://supplier.example/graphql",
            options={"query": "query Products { products { sku } }"},
        )
        context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

        payload = await adapter.fetch(source, context)

    assert payload.data == {"products": [{"sku": "A-1"}]}
    assert payload.metadata["transport"] == "graphql-http"


@pytest.mark.asyncio
async def test_graphql_adapter_surfaces_protocol_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"errors": [{"message": "denied"}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = GraphQLAdapter(client=client)
        source = SourceSpec(
            type="graphql",
            endpoint="https://supplier.example/graphql",
            options={"query": "query { products { sku } }"},
        )
        context = ExecutionContext(execution_id="exec-1", integration_id="int-1")

        with pytest.raises(GraphQLResponseError):
            await adapter.fetch(source, context)
