"""Generic dlt source adapter.

The adapter intentionally knows nothing about Shopify, Stripe, HubSpot, SQL
databases, or other concrete sources. A dlt source/resource factory is resolved
through a registry and executed behind the SourceAdapter protocol.
"""

from __future__ import annotations

import asyncio
import importlib
from collections.abc import Callable, Mapping
from typing import Any, Protocol, cast, runtime_checkable

from pydantic import BaseModel

from uncertainAPI.core.specs import SourceSpec
from uncertainAPI.core.types import ExecutionContext, RawPayload

DltSourceFactory = Callable[..., object]


class DltSourceConfigurationError(ValueError):
    """Raised when a dlt-backed SourceSpec is incomplete or ambiguous."""


class DltDataShapeError(TypeError):
    """Raised when a dlt source yields data the JSON runtime cannot normalize."""


@runtime_checkable
class DltSourceRegistry(Protocol):
    """Resolve a logical or import-path reference to a dlt source factory."""

    def resolve(self, reference: str) -> DltSourceFactory:
        ...


@runtime_checkable
class DltResourceDiscoverer(Protocol):
    """Optional capability for discovering resources exposed by a dlt source."""

    async def resources(self, source: SourceSpec) -> tuple[str, ...]:
        ...


class StaticDltSourceRegistry:
    """Explicit registry useful for applications, plugins, and tests."""

    def __init__(self, factories: Mapping[str, DltSourceFactory]) -> None:
        self._factories = dict(factories)

    def resolve(self, reference: str) -> DltSourceFactory:
        try:
            return self._factories[reference]
        except KeyError as exc:
            raise DltSourceConfigurationError(
                f"No dlt source factory registered as {reference!r}"
            ) from exc


class ImportPathDltSourceRegistry:
    """Resolve trusted local source factories using module:attribute paths."""

    def resolve(self, reference: str) -> DltSourceFactory:
        module_name, separator, attribute_path = reference.partition(":")
        if not separator or not module_name or not attribute_path:
            raise DltSourceConfigurationError(
                "dlt factory references must use 'module:attribute' syntax"
            )

        module = importlib.import_module(module_name)
        value: object = module
        for attribute in attribute_path.split("."):
            value = getattr(value, attribute)

        if not callable(value):
            raise DltSourceConfigurationError(
                f"dlt factory reference {reference!r} is not callable"
            )
        return cast(DltSourceFactory, value)


class DltSourceAdapter:
    """Execute any registered dlt source/resource as JSON-like raw records.

    dlt remains an optional dependency and is imported only when this adapter is
    actually executed. One dlt resource maps to one UncertainAPI integration so
    records from unrelated resource schemas cannot be mixed accidentally.
    """

    source_types = frozenset({"dlt"})

    def __init__(self, *, registry: DltSourceRegistry | None = None) -> None:
        self._registry = registry or ImportPathDltSourceRegistry()

    def supports(self, source: SourceSpec) -> bool:
        return source.type.lower() in self.source_types

    async def fetch(self, source: SourceSpec, context: ExecutionContext) -> RawPayload:
        return await asyncio.to_thread(self._fetch_sync, source)

    async def resources(self, source: SourceSpec) -> tuple[str, ...]:
        return await asyncio.to_thread(self._discover_resources_sync, source)

    def _fetch_sync(self, source: SourceSpec) -> RawPayload:
        dlt_module = _require_dlt()
        factory_reference = _factory_reference(source)
        factory = self._registry.resolve(factory_reference)
        factory_kwargs = _factory_kwargs(source)
        produced: Any = factory(**factory_kwargs)

        requested_resource = _requested_resource(source)
        selected_resource = _select_resource(produced, requested_resource)
        max_items = _max_items(source)

        records = _materialize_json_records(selected_resource, max_items=max_items)
        return RawPayload(
            data=records,
            content_type="application/json",
            metadata={
                "source_type": source.type,
                "connector": "dlt",
                "factory": factory_reference,
                "resource": requested_resource or _single_selected_resource(produced),
                "record_count": len(records),
                "dlt_version": str(getattr(dlt_module, "__version__", "unknown")),
            },
        )

    def _discover_resources_sync(self, source: SourceSpec) -> tuple[str, ...]:
        _require_dlt()
        factory = self._registry.resolve(_factory_reference(source))
        produced: Any = factory(**_factory_kwargs(source))
        return _resource_names(produced)


def _require_dlt() -> Any:
    try:
        return importlib.import_module("dlt")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "DltSourceAdapter requires the optional dlt dependency. "
            "Install with: pip install 'uncertainapi[dlt]'"
        ) from exc


def _factory_reference(source: SourceSpec) -> str:
    reference = source.options.get("factory")
    if not isinstance(reference, str) or not reference.strip():
        raise DltSourceConfigurationError(
            "dlt sources require options['factory'] as a registry key or import path"
        )
    return reference.strip()


def _factory_kwargs(source: SourceSpec) -> dict[str, Any]:
    value = source.options.get("kwargs", {})
    if not isinstance(value, dict):
        raise DltSourceConfigurationError("dlt options['kwargs'] must be an object")
    return dict(value)


def _requested_resource(source: SourceSpec) -> str | None:
    value = source.options.get("resource")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DltSourceConfigurationError("dlt options['resource'] must be a non-empty string")
    return value.strip()


def _max_items(source: SourceSpec) -> int | None:
    value = source.options.get("max_items")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise DltSourceConfigurationError("dlt options['max_items'] must be a positive integer")
    return value


def _resource_names(produced: Any) -> tuple[str, ...]:
    resources = getattr(produced, "resources", None)
    if resources is None:
        name = getattr(produced, "name", None)
        return (str(name),) if name else ()

    selected = getattr(resources, "selected", None)
    if isinstance(selected, Mapping):
        return tuple(str(name) for name in selected)
    if isinstance(resources, Mapping):
        return tuple(str(name) for name in resources)
    return ()


def _single_selected_resource(produced: Any) -> str | None:
    names = _resource_names(produced)
    if len(names) == 1:
        return names[0]
    return None


def _select_resource(produced: Any, requested_resource: str | None) -> Any:
    names = _resource_names(produced)

    if requested_resource is None:
        if len(names) > 1:
            raise DltSourceConfigurationError(
                "dlt sources exposing multiple resources require options['resource']; "
                f"available resources: {', '.join(names)}"
            )
        return produced

    selector = getattr(produced, "with_resources", None)
    if callable(selector):
        if names and requested_resource not in names:
            raise DltSourceConfigurationError(
                f"dlt resource {requested_resource!r} not found; "
                f"available resources: {', '.join(names)}"
            )
        return selector(requested_resource)

    produced_name = getattr(produced, "name", None)
    if produced_name is not None and str(produced_name) == requested_resource:
        return produced

    raise DltSourceConfigurationError(
        f"dlt factory does not expose selectable resource {requested_resource!r}"
    )


def _materialize_json_records(produced: Any, *, max_items: int | None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for item in produced:
        for record in _records_from_item(item):
            records.append(record)
            if max_items is not None and len(records) >= max_items:
                return records

    return records


def _records_from_item(item: object) -> list[dict[str, Any]]:
    if isinstance(item, dict):
        return [_string_keyed_dict(item)]

    if isinstance(item, (list, tuple)):
        records: list[dict[str, Any]] = []
        for value in item:
            records.extend(_records_from_item(value))
        return records

    if isinstance(item, BaseModel):
        return [_string_keyed_dict(item.model_dump())]

    raise DltDataShapeError(
        "dlt sources used by the JSON runtime must yield mappings, Pydantic models, "
        "or pages containing those values"
    )


def _string_keyed_dict(value: Mapping[object, Any]) -> dict[str, Any]:
    return {str(key): item for key, item in value.items()}
