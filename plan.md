# UncertainAPI OSS Roadmap

## Architectural guardrails

Every phase must preserve these rules:

1. The default install stays lightweight.
2. Core runtime code depends on UncertainAPI-owned protocols and value objects.
3. Mature open-source infrastructure is integrated rather than reimplemented.
4. Provider-specific libraries remain optional and lazy-loaded.
5. Adding a provider should not require editing the central executor.
6. IntegrationPlan remains serializable and provider-neutral.
7. Plaintext credentials must not be embedded in plans.
8. Private CertainAPI intelligence is outside this public OSS roadmap.

---

## Phase 1 — Interface-first runtime foundation — COMPLETE

Scope:

- SourceSpec, ContractSpec, MappingSpec, IntegrationSpec, IntegrationPlan
- SourceAdapter, MappingEngine, ContractValidator, RuntimeObserver and infrastructure ports
- dependency-injected IntegrationRuntime
- source adapter resolver
- lightweight HTTP/JSON adapter
- removal of the legacy Django/DRF + AG2 + browser-first architecture
- minimal mandatory dependency surface

Acceptance:

- framework-independent runtime
- core import does not require optional providers
- CI green on Python 3.12 and 3.13

---

## Phase 2 — Reusable deterministic runtime MVP — COMPLETE

Scope:

- JMESPath mapping engine
- deterministic transforms
- JSON Schema Draft 2020-12 validator
- GraphQL adapter
- standard runtime composition
- optional capability extras
- end-to-end source -> mapping -> contract validation test

Acceptance:

- deterministic normalization works without AI
- mapping and validation use mature OSS libraries
- standard runtime remains replaceable through protocols

---

## Phase 3 — Connector ecosystem through dlt — IN PROGRESS

Scope:

- generic DltSourceAdapter
- StaticDltSourceRegistry
- ImportPathDltSourceRegistry
- resource discovery capability
- one dlt resource per UncertainAPI integration
- real dlt integration tests
- dlt kept outside the default and standard dependency sets

Acceptance:

- adding a new dlt source requires no new UncertainAPI adapter class
- multi-resource sources cannot silently mix schemas
- dlt extraction does not block the async runtime event loop
- default UncertainAPI import does not import dlt
- Phase 3 CI green

---

## Phase 4 — Browser provider abstraction

Goal:

Support JS-heavy and interactive acquisition without owning browser infrastructure.

Scope:

- provider-neutral BrowserSourceAdapter contract
- external provider adapters behind optional packages
- request/response conversion into UncertainAPI RawPayload
- no Playwright/Selenium objects across core boundaries
- deterministic provider selection interface
- browser capability and failure metadata

Potential providers may include managed browser/rendering services, but no provider
becomes mandatory.

Acceptance:

- a new browser provider can be added without executor changes
- core package installs no browser runtime
- browser payloads enter the same mapping/validation pipeline as API sources

---

## Phase 5 — Incremental execution and source state

Goal:

Make recurring integrations efficient without building a scheduler platform.

Scope:

- CheckpointStore implementations
- ETag / If-None-Match
- Last-Modified / If-Modified-Since
- cursor and watermark state
- incremental execution metadata
- source-level retry/rate-limit hooks
- secret resolution integration
- deterministic no-change results

Acceptance:

- repeated executions avoid unnecessary full fetches where the source supports it
- state is external to workers
- plans remain free of plaintext credentials

---

## Phase 6 — Delivery, change events, and deterministic drift signals

Goal:

Turn normalized records into useful downstream integration outputs.

Scope:

- DestinationAdapter implementations
- created / updated / deleted record events
- current-state comparison
- structural/type validation failure signals
- raw -> normalized -> current-state -> history lifecycle
- artifact references and lineage metadata

Acceptance:

- downstream delivery remains destination-neutral
- deterministic structural drift is observable
- semantic drift reasoning is not moved into OSS

---

## Phase 7 — Operational observability and worker controls

Goal:

Provide production visibility without coupling UncertainAPI to one telemetry vendor.

Scope:

- structured RuntimeObserver implementations
- OpenTelemetry adapter
- optional Midil/Pymidil adapter if retained
- execution timing and failure classification
- trace propagation
- coarse pause/throttle/drain integration points
- idempotency visibility

Acceptance:

- telemetry failures cannot break extraction
- observability remains optional
- no vendor-specific telemetry object leaks into core APIs

---

## Phase 8 — Plugin ecosystem, performance, and hardening

Goal:

Make UncertainAPI safe and practical for third-party extension.

Scope:

- plugin registration/discovery conventions
- adapter compatibility tests
- package-size/import-time benchmarks
- execution benchmarks
- security review of import-path/plugin boundaries
- dependency/license inventory
- error taxonomy stabilization
- public extension documentation

Acceptance:

- plugins can be distributed independently
- performance regressions are measurable
- optional integrations cannot silently bloat the core install

---

## Phase N — OSS 1.0 stabilization — END

Goal:

Freeze a dependable open-source runtime contract.

Scope:

- public API compatibility review
- IntegrationPlan schema versioning policy
- migration tooling/documentation
- complete examples for HTTP, GraphQL, dlt, browser provider, state, and destinations
- packaging and release automation
- supported Python/version matrix
- security and contributor documentation
- 1.0 release candidate and final release

End-state:

UncertainAPI is a small, deterministic, extensible execution runtime that can
consume heterogeneous sources through replaceable adapters and emit validated
stable contracts.

Automatic discovery, semantic mapping, semantic drift reasoning, repair
generation, confidence scoring, and adaptive source intelligence remain outside
the OSS runtime and are intentionally not described in this public roadmap.
