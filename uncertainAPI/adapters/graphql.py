"""Deterministic GraphQL source adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from uncertainAPI.core.specs import SourceSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload

if TYPE_CHECKING:
    import httpx


class GraphQLResponseError(RuntimeError):
    """Raised when a GraphQL endpoint returns protocol-level errors."""


class GraphQLAdapter:
    """Fetch GraphQL data over HTTP without browser or AI infrastructure."""

    source_types = frozenset({"graphql"})

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = client
        self._timeout = timeout

    def supports(self, source: SourceSpec) -> bool:
        return source.type.lower() in self.source_types

    async def fetch(self, source: SourceSpec, context: ExecutionContext) -> RawPayload:
        try:
            import httpx
        except ImportError as exc:
            raise ImportError(
                "GraphQLAdapter requires the optional HTTP dependency. "
                "Install with: pip install 'uncertainapi[http]'"
            ) from exc

        query = source.options.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("GraphQL sources require options['query']")

        request_body: dict[str, Any] = {"query": query}

        variables = source.options.get("variables")
        if variables is not None:
            if not isinstance(variables, dict):
                raise ValueError("GraphQL options['variables'] must be an object")
            request_body["variables"] = variables

        operation_name = source.options.get("operation_name")
        if operation_name is not None:
            if not isinstance(operation_name, str):
                raise ValueError("GraphQL options['operation_name'] must be a string")
            request_body["operationName"] = operation_name

        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)

        try:
            response = await client.request(
                method="POST",
                url=source.endpoint,
                headers=source.headers,
                params=source.params,
                json=request_body,
            )
            response.raise_for_status()
            document = response.json()
            if not isinstance(document, dict):
                raise GraphQLResponseError("GraphQL response must be a JSON object")

            errors = document.get("errors")
            if errors:
                raise GraphQLResponseError(f"GraphQL response contains errors: {errors!r}")

            return RawPayload(
                data=document.get("data"),
                content_type=response.headers.get("content-type"),
                status_code=response.status_code,
                headers=dict(response.headers),
                metadata={
                    "source_type": source.type,
                    "transport": "graphql-http",
                },
            )
        finally:
            if owns_client:
                await client.aclose()
