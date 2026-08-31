# Phase 2 — Reusable Deterministic Runtime MVP

## Purpose

Phase 2 turns the Phase 1 interfaces into a useful end-to-end open-source runtime
without rebuilding commodity mapping, validation, or transport infrastructure.

The project rule remains:

> **Integrate mature infrastructure instead of reimplementing it.**

## Built-in reusable components

### HTTP/JSON adapter

HTTPJSONAdapter handles deterministic REST and JSON HTTP sources using the
optional httpx dependency.

### GraphQL adapter

GraphQLAdapter treats GraphQL as a first-class source type while still using
ordinary HTTP transport. Query text, variables, and operation name are data in
SourceSpec.options; they are not hard-coded into the executor.

### JMESPath mapping

JMESPathMappingEngine uses the mature jmespath package for:

- record selection;
- source-field lookup;
- nested field projection.

A deliberately small transform layer handles deterministic type conversion and
string normalization. It does not perform discovery, semantic mapping, or repair.

### JSON Schema validation

JSONSchemaContractValidator uses jsonschema Draft 2020-12 validation.
The persistent contract stays language-neutral JSON Schema.

## Standard runtime

create_standard_runtime() composes:

    HTTPJSONAdapter ─┐
                     ├─> JMESPathMappingEngine -> JSONSchemaContractValidator
    GraphQLAdapter ──┘

This is a convenience composition only. Every component remains replaceable
through the Phase 1 protocols.

## Optional dependency sets

- uncertainapi[http] — HTTP and GraphQL transport
- uncertainapi[mapping] — JMESPath mapping
- uncertainapi[validation] — JSON Schema validation
- uncertainapi[runtime] — mapping + validation
- uncertainapi[standard] — HTTP + GraphQL + mapping + validation

The minimal package still depends only on Pydantic.

## Boundary

Phase 2 does not add:

- source discovery;
- schema inference;
- semantic mapping generation;
- adaptive provider routing;
- drift reasoning;
- AI repair;
- browser automation;
- scheduler infrastructure.

Those remain later-phase or CertainAPI Cloud responsibilities.
