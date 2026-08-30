# Interface-First Architecture

## Status

This document defines a hard architectural constraint for uncertainAPI 0.2+.

The open-source runtime must depend on **interfaces/protocols**, not concrete
frameworks, infrastructure vendors, agent libraries, storage systems, or
observability products.

## Goal

A developer must be able to extend uncertainAPI by implementing a protocol and
registering the implementation. Extending the system must not require editing
the core runtime.

## Core ports

### SourceAdapter

Responsible for acquiring raw source data.

Examples of implementations:

- HTTP/JSON
- REST
- GraphQL
- HTML
- XML
- CSV
- Cloudflare Browser Rendering
- Browserbase
- Browserless
- Zyte
- custom enterprise source

The runtime must never contain provider-selection conditionals tied to specific
vendors.

### MappingEngine

Transforms a `RawPayload` into canonical record candidates.

Possible implementations include:

- JSONPath
- JMESPath
- CSS/XPath
- custom mapping DSL
- customer-defined mapper

The private CertainAPI compiler may generate a mapping, but the OSS runtime only
executes it.

### ContractValidator

Validates canonical records against a stable contract.

The primary persisted contract format should be language-neutral JSON Schema.
Pydantic remains a convenient Python authoring interface.

### RuntimeObserver

Receives execution lifecycle events without coupling the runtime to telemetry
vendors.

Expected implementations:

- no-op observer
- structured logging
- OpenTelemetry
- Pymidil/Midil
- customer-provided observer

Pymidil is an adapter, not an architectural dependency.

### ArtifactStore

Stores raw/evidence artifacts behind opaque references.

Possible implementations:

- filesystem
- Cloudflare R2
- AWS S3
- MinIO
- customer object store

### PlanRegistry

Loads and persists versioned `IntegrationPlan` objects.

Possible implementations:

- in-memory
- filesystem
- PostgreSQL
- HTTP CertainAPI registry
- customer registry

### SecretResolver

Resolves opaque `auth_ref` values at execution time.

Integration plans must not carry plaintext secrets.

Possible implementations:

- environment variables
- HashiCorp Vault
- AWS Secrets Manager
- cloud KMS-backed store
- CertainAPI credential broker

### StateStore / CheckpointStore

Persists execution state such as:

- ETag
- Last-Modified
- pagination cursor
- watermark
- incremental sync token
- retry checkpoint
- latest successful observation

Possible implementations:

- in-memory
- Redis
- PostgreSQL
- customer state backend

### DestinationAdapter

Delivers normalized output.

Possible implementations:

- callback
- webhook
- PostgreSQL
- Kafka/Redpanda
- S3/R2
- customer database
- custom event bus

### ProviderRouter

Selects an acquisition implementation from compatible providers.

The OSS project may provide a basic deterministic router. CertainAPI Cloud may
provide a proprietary cost/reliability-aware implementation.

### RateLimiter / ConcurrencyController

Enforces source-, tenant-, or provider-level limits without tying the runtime to
a particular Redis or queue implementation.

### Scheduler / JobDispatcher

Optional integration boundary for recurring execution.

The core runtime must remain executable without a scheduler.

## Dependency direction

Correct:

```text
Runtime
  ↓
Protocol
  ↑
Concrete implementation
```

Incorrect:

```text
Runtime
  ↓
Cloudflare SDK / Django model / Pymidil / AG2 / Playwright
```

## Provider neutrality

The core package must not expose:

- Django model classes;
- DRF requests/responses;
- FastAPI request objects;
- Playwright page/browser objects;
- Selenium drivers;
- AG2 agents;
- Midil/Pymidil classes;
- provider-specific browser response types;
- cloud-vendor SDK objects.

All provider-specific data must be converted into uncertainAPI-owned value
objects before crossing into the core.

## Serialization

The following should be serializable:

- `SourceSpec`
- `ContractSpec`
- `MappingSpec`
- `IntegrationSpec`
- `IntegrationPlan`
- execution metadata
- drift events

This allows plans to move between:

- Python processes;
- CertainAPI Cloud;
- databases;
- queues;
- object storage;
- a future Go executor.

## OSS/private boundary

The OSS interfaces are public.

CertainAPI Cloud may implement these interfaces with proprietary components,
including:

- semantic source inspection;
- schema inference;
- automatic mapping;
- source intelligence;
- adaptive provider routing;
- semantic drift analysis;
- repair compilation;
- confidence scoring.

The open-source package must never import the private CertainAPI package.

## Extension test

A proposed feature passes the architecture test when a third party can add it by:

1. implementing an existing protocol, or defining a narrowly justified new port;
2. registering/injecting that implementation;
3. leaving the runtime unchanged.

If adding a new provider requires editing the central executor, the abstraction
is incomplete.

## Current 0.2 foundation

The `feature/0.2-interface-runtime` branch introduces:

- `SourceSpec`
- `ContractSpec`
- `MappingSpec`
- `IntegrationSpec`
- `IntegrationPlan`
- `SourceAdapter`
- `MappingEngine`
- `ContractValidator`
- `RuntimeObserver`
- `ArtifactStore`
- `PlanRegistry`
- dependency-injected `IntegrationRuntime`
- initial deterministic `HTTPJSONAdapter`

Django/DRF and AG2 are being moved from mandatory dependencies to optional
integration extras.
