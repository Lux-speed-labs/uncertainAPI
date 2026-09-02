# Phase 3 — Connector Ecosystem Through dlt

## Purpose

Phase 3 expands source coverage without turning UncertainAPI into a connector
maintenance project.

The rule is:

> One generic dlt adapter, not one UncertainAPI adapter per upstream system.

dlt remains optional. The minimal UncertainAPI installation still does not
install or import dlt.

## Why dlt

dlt already provides reusable source infrastructure for:

- declarative REST APIs;
- SQL databases;
- filesystem and object-storage sources;
- community and dlt-maintained verified sources.

Those capabilities should remain upstream responsibilities wherever they fit.

## Architecture

    SourceSpec(type="dlt")
              |
              v
      DltSourceAdapter
              |
              v
       DltSourceRegistry
          /         \
         /           \
 Static registry   Import-path registry
         \           /
          \         /
         dlt source/resource
              |
              v
         JSON-like rows
              |
              v
     JMESPath MappingEngine
              |
              v
    JSON Schema ContractValidator

The IntegrationRuntime does not know that dlt is involved.

## Source registration

Applications can register dlt source factories explicitly:

    registry = StaticDltSourceRegistry({
        "supplier": supplier_source,
        "shopify": shopify_source,
    })

    adapter = DltSourceAdapter(registry=registry)

Or trusted local code can be resolved by import path:

    SourceSpec(
        type="dlt",
        endpoint="dlt://shopify",
        options={
            "factory": "my_project.sources.shopify:shopify_source",
            "resource": "products",
        },
    )

Adding another dlt source requires a new registry entry or source module, not a
new UncertainAPI adapter class.

## Verified sources

Verified source code remains owned and maintained by its upstream dlt source
implementation. A project may install/eject/configure that source in the normal
dlt way and expose its source factory to DltSourceAdapter.

UncertainAPI does not duplicate source-specific pagination, authentication,
incremental extraction, API traversal, or schema-acquisition logic that the dlt
source already implements.

## One resource per integration

A dlt source may expose several resources with unrelated schemas. UncertainAPI
therefore requires an explicit resource when a source exposes more than one.

This gives a stable relationship:

    one integration
        -> one source resource
        -> one mapping
        -> one canonical contract

The same dlt source can back several UncertainAPI integrations when multiple
resources are required.

## Resource discovery

DltSourceAdapter implements the optional DltResourceDiscoverer capability:

    resources = await adapter.resources(source_spec)

This allows applications and future control planes to discover resource names
without hard-coding the dlt catalog into UncertainAPI.

## Runtime behavior

dlt extraction is synchronous from the adapter's perspective and is executed
through asyncio.to_thread so it does not block the async IntegrationRuntime event
loop.

The adapter materializes JSON-compatible mappings and Pydantic records into a
RawPayload. Unsupported dataframe/Arrow/native objects are rejected in this
phase rather than leaking provider-specific types into the core runtime.

## Secrets

IntegrationPlan objects must not contain plaintext credentials.

dlt sources should resolve credentials using normal dlt configuration/secrets,
environment configuration, or an application-owned factory/registry that is
connected to a secret manager.

## Installation

    pip install "uncertainapi[dlt]"

The alias below is also available for connector-focused installations:

    pip install "uncertainapi[connectors]"

Neither extra is part of the default or standard deterministic runtime.

## Explicit non-goals

Phase 3 does not:

- fork or vendor dlt verified sources;
- create ShopifyAdapter, StripeAdapter, SalesforceAdapter, etc.;
- make dlt mandatory;
- replace UncertainAPI canonical mapping or contract validation with dlt schemas;
- expose dlt-specific objects across core interfaces;
- implement browser acquisition;
- implement semantic source discovery or AI repair.
