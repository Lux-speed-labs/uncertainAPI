"""Deterministic HTTP/JSON source adapter."""

from __future__ import annotations

from typing import Any

import httpx

from uncertainAPI.core.specs import SourceSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload


class HTTPJSONAdapter:
    """Fetch JSON over HTTP without browser or AI infrastructure."""

    source_types = frozenset({"http_json", "rest", "json"})

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
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.request(
                method=source.method,
                url=source.endpoint,
                headers=source.headers,
                params=source.params,
                json=source.body,
            )
            response.raise_for_status()
            return RawPayload(
                data=response.json(),
                content_type=response.headers.get("content-type"),
                status_code=response.status_code,
                headers=dict(response.headers),
                metadata={"source_type": source.type},
            )
        finally:
            if owns_client:
                await client.aclose()
