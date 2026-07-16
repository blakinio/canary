# ADR-20260714: Real Tibia registry as code

- Status: accepted
- Date: 2026-07-14
- Owners: repository-wide agent governance
- Related module IDs: all registry modules
- Related task/PR: `CAN-20260714-real-tibia-module-registry` / #324

## Context

Real Tibia parity work spans many gameplay, world, protocol, persistence and tooling domains. Chat history and repeated large prompts are not durable. A single manually maintained Markdown index cannot enforce unique identities, valid dependencies, source roles, freshness or generated-file consistency. A single monolithic YAML registry would also become a frequent multi-agent conflict point.

The existing evidence registry, parity playbook, module programs, validation reports and task lifecycle already define how conclusions and implementations are delivered. The missing layer is a compact machine-readable discovery graph connecting stable module identities to those sources of truth.

## Decision

Adopt a registry-as-code design with:

1. one JSON-compatible YAML record per module;
2. separate category, source and immutable-baseline registries;
3. JSON Schemas plus domain validation;
4. deterministic standard-library Python tooling for validation, generation, lookup and freshness;
5. generated Markdown indexes that are never edited manually;
6. multidimensional maturity rather than one optimistic status;
7. module path patterns as discovery hints, not ownership permissions;
8. detailed programs only when a domain needs multiple PRs or long-lived state;
9. no copied gameplay encyclopaedia inside registry records.

## Alternatives considered

| Alternative | Benefits | Risks/reason rejected |
|---|---|---|
| One large Markdown taxonomy | Easy to start | Not machine-checkable; duplication and staleness are invisible. |
| One monolithic `modules.yaml` | One parse target | Every module edit conflicts in the same file; poor multi-agent ownership. |
| A detailed program file for every system | Rich context | Creates empty/speculative documents and high maintenance cost. |
| External database/service | Flexible queries | Adds infrastructure, availability and trust boundaries for repository governance. |
| Runtime code annotations only | Close to implementation | Does not cover official evidence, client, wiki, donor, docs or cross-module planning. |

## Consequences

### Positive

- Module additions are independently owned and mergeable.
- CI detects malformed records, invalid references, cycles and generated drift.
- Agents can discover relevant modules by path and follow dependencies.
- Source authority and proof dimensions remain explicit.
- Freshness is visible without deleting historical evidence.
- The system scales without requiring every module to have a large program.

### Trade-offs

- JSON-compatible YAML is less expressive than unrestricted YAML.
- Path patterns require conservative maintenance and may overlap.
- Registry maturity is metadata and can still become stale; freshness and task preflight remain mandatory.
- Generated indexes add files, but their content is deterministic and checked.

## Compatibility and migration

Existing module catalogue, programs, validation reports and task records remain authoritative for their existing responsibilities. The registry links to them and is introduced incrementally. Existing tasks are not required to be rewritten immediately with `module_ids`; new parity tasks should use the bounded template.

## Validation

The dedicated workflow compiles the tool, runs focused tests, validates schemas/domain rules and checks generated indexes. Repository ownership and required CI remain mandatory before merge.

## Rollback or supersession

Revert the feature merge to remove the registry foundation. A future replacement must preserve stable module IDs or provide an explicit migration map.
