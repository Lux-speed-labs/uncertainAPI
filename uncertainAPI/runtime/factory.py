"""Convenience composition for the standard deterministic runtime."""

from __future__ import annotations

from uncertainAPI.adapters.graphql import GraphQLAdapter
from uncertainAPI.adapters.http_json import HTTPJSONAdapter
from uncertainAPI.core.interfaces import RuntimeObserver, SourceAdapterResolver
from uncertainAPI.mapping import JMESPathMappingEngine
from uncertainAPI.runtime.executor import IntegrationRuntime
from uncertainAPI.validation import JSONSchemaContractValidator


def create_standard_runtime(
    *,
    observer: RuntimeObserver | None = None,
    adapter_resolver: SourceAdapterResolver | None = None,
) -> IntegrationRuntime:
    """Compose the built-in deterministic HTTP/GraphQL runtime."""

    return IntegrationRuntime(
        adapters=[HTTPJSONAdapter(), GraphQLAdapter()],
        mapper=JMESPathMappingEngine(),
        validator=JSONSchemaContractValidator(),
        observer=observer,
        adapter_resolver=adapter_resolver,
    )
