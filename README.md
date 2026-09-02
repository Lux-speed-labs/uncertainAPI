# UncertainAPI

A lightweight, interface-first Python runtime for executing portable data integration plans.

UncertainAPI 0.2 is being rebuilt around one principle:

> **Integrate mature infrastructure instead of reimplementing it.**

The runtime provides stable contracts and extension interfaces while connector, browser, mapping, storage, observability, and scheduling capabilities can be supplied by optional adapters.

## Status

`0.2.0-dev` is a pre-release architecture refactor. The current stable 0.1.x line used a Django/DRF + AI-agent extraction architecture. That implementation remains available in Git history and published 0.1.x releases, but it is not the architectural basis of 0.2.

## Core design

```text
IntegrationPlan
      ↓
IntegrationRuntime
      ↓
SourceAdapter
      ↓
MappingEngine
      ↓
ContractValidator
      ↓
ExecutionResult
```

The runtime depends on protocols rather than concrete providers.

Current public extension points include:

- `SourceAdapter`
- `SourceAdapterResolver`
- `MappingEngine`
- `ContractValidator`
- `RuntimeObserver`
- `ArtifactStore`
- `PlanRegistry`
- `CheckpointStore`
- `SecretResolver`
- `DestinationAdapter`
- `RateLimiter`
- `JobDispatcher`

See [docs/architecture/INTERFACES.md](docs/architecture/INTERFACES.md).

## Installation

Minimal core:

```bash
pip install uncertainapi
```

The default package intentionally has a very small dependency surface.

Optional capability sets:

```bash
pip install "uncertainapi[http]"        # REST/JSON + GraphQL transport
pip install "uncertainapi[mapping]"     # JMESPath mapping
pip install "uncertainapi[validation]"  # JSON Schema validation
pip install "uncertainapi[standard]"    # deterministic runtime MVP
pip install "uncertainapi[dlt]"         # dlt connector ecosystem
```

The standard runtime combines HTTP/GraphQL acquisition, JMESPath mapping, and
JSON Schema validation while keeping each component replaceable through the
public protocols.

## Minimal example

```python
from uncertainAPI.core import (
    ContractSpec,
    IntegrationPlan,
    IntegrationSpec,
    MappingSpec,
    SourceSpec,
)
from uncertainAPI.runtime import IntegrationRuntime

plan = IntegrationPlan(
    integration_id="products",
    plan_version="1",
    integration=IntegrationSpec(
        source=SourceSpec(
            type="custom",
            endpoint="example://products",
        ),
        contract=ContractSpec(
            name="ProductOffer",
            version="1",
            schema={"type": "object"},
        ),
        mapping=MappingSpec(),
    ),
)

# Supply implementations of SourceAdapter, MappingEngine and
# ContractValidator through dependency injection.
runtime = IntegrationRuntime(
    adapters=[my_source_adapter],
    mapper=my_mapping_engine,
    validator=my_contract_validator,
)

result = await runtime.execute(plan)
```

For the built-in deterministic composition:

```python
from uncertainAPI.runtime import create_standard_runtime

runtime = create_standard_runtime()
result = await runtime.execute(plan)
```

See [Phase 2 — Reusable Deterministic Runtime MVP](docs/architecture/PHASE_2_RUNTIME_MVP.md).

### dlt connector ecosystem

Phase 3 adds one generic optional adapter for dlt sources rather than
source-specific UncertainAPI connectors:

```python
from uncertainAPI.adapters import DltSourceAdapter, StaticDltSourceRegistry

adapter = DltSourceAdapter(
    registry=StaticDltSourceRegistry({
        "supplier": supplier_source,
    })
)
```

The corresponding plan uses `type="dlt"`, a factory reference, and optionally a
single resource name. New dlt sources can be registered without changing the
UncertainAPI executor or adding a new adapter class.

See [Phase 3 — Connector Ecosystem Through dlt](docs/architecture/PHASE_3_CONNECTOR_ECOSYSTEM.md).

## What UncertainAPI does not intend to rebuild

Where mature OSS or managed infrastructure already solves a commodity concern, UncertainAPI should integrate it behind an interface instead of recreating it.

Examples include:

- REST/API connector mechanics;
- pagination and incremental extraction;
- JSON query languages;
- JSON Schema validation;
- browser infrastructure;
- queues and schedulers;
- observability backends;
- object storage;
- OAuth/provider catalogs.

## CertainAPI relationship

UncertainAPI is the open-source execution runtime.

CertainAPI Cloud is planned as the private intelligence/control layer that discovers sources, generates mappings, compiles `IntegrationPlan` objects, detects semantic drift, repairs integrations, and manages production fleets.

The OSS runtime must never depend on CertainAPI Cloud.

## Migration from 0.1.x

The 0.2 line intentionally retires the Django-first `ExtractorView`, AG2 orchestration, built-in browser backends, Django models, project scaffolding CLI, and prototype task system from the core package.

See [docs/migration/0.1-to-0.2.md](docs/migration/0.1-to-0.2.md).

## Development

```bash
make install-dev
make test
make lint
make type-check
```

## License

MIT License.
