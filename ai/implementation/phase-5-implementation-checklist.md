# Phase 5 Implementation Checklist

This checklist guides implementation of Phase 5 - Relationship-Oriented
Control Plane.

The stable phase plan is:

```text
docs/phases/phase-5-relationship-oriented-control-plane
```

Use that plan as the source of milestone scope. This checklist records working
rules, validation expectations, and release-integrity requirements.

## Governing Documents

- `docs/phases/phase-5-relationship-oriented-control-plane`
- `docs/architecture/adr/ADR-0005-driver-introspection-and-port-capabilities.md`
- `docs/architecture/adr/ADR-0009-endpoint-relationships-and-route-orchestration.md`
- `docs/architecture/adr/ADR-0006-modular-driver-packaging-and-discovery.md`
- `docs/architecture.md`
- `docs/driver-contract.md`
- `docs/configuration-model.md`
- `docs/capability-model.md`
- `docs/developer-standards.md`
- `PROJECT_STATUS.md`
- `docs/roadmap.md`

Accepted ADRs are authoritative when documents conflict.

## Milestone Sequence

1. Milestone 5.1 - Endpoint Metadata
2. Milestone 5.2 - Relationship Model
3. Milestone 5.3 - Relationship Planner
4. Milestone 5.4 - Driver Integration
5. Milestone 5.5 - Relationship Groups
6. Milestone 5.6 - Planner Validation
7. Milestone 5.7 - Regression and Physical Validation

Do not create detailed implementation plans beyond the active milestone unless
explicitly requested.

## Expected Areas

Package and subsystem areas likely to change during Phase 5:

- `packages/driver-api/`
- `packages/driver-mock/`
- `packages/driver-orei-uhd808/`
- `packages/driver-orei-ukm404/`
- `packages/core/src/workspace_fabric/core/graph/`
- `packages/core/src/workspace_fabric/core/planner/`
- `packages/core/src/workspace_fabric/core/transactions/`
- `packages/core/src/workspace_fabric/drivers/`
- `tests/`
- `examples/`
- `docs/`

Do not move vendor-specific implementation code back into the core package.

## Phase 5 Rules

- Drivers describe; the core decides.
- Endpoint metadata and constraints are driver responsibilities.
- Relationship intent, reconciliation, managed scope, conflict detection, and
  global policy are core responsibilities.
- Mock implementations should be updated before physical drivers where
  practical.
- Existing point-to-point route actions remain valid execution primitives until
  a completed migration replaces them.
- Existing validated physical functionality must remain operational at every
  milestone boundary.
- Structured supported, unsupported, unknown, and non-executable outcomes are
  required.

## Pre-1.0 Release Integrity

Workspace Fabric does not promise historical compatibility for every pre-1.0
internal interface, configuration structure, or Driver API revision.

Architectural correctness may require breaking transitional pre-release
methods.

However, every completed milestone, phase, and point release must leave the
repository coherent, integrated, and operational:

- Core and included driver packages use congruent contracts.
- Tests, examples, documentation, package metadata, and CLI behavior agree.
- No partially completed relationship migration is represented as complete.
- Existing Phase 4 functionality remains operational.

## Milestone 5.1 Acceptance

Milestone 5.1 should establish endpoint metadata without changing physical
behavior.

Acceptance criteria:

- Driver API exposes endpoint metadata required by ADR-0005 and ADR-0009.
- Metadata supports endpoint direction, accepted endpoint types, cardinality,
  disconnect support, and required assignment.
- Metadata validation reports structured errors.
- Mock drivers implement the updated metadata contract first where practical.
- Existing OREI and mock route behavior continues operating.
- Package builds and isolated-wheel validation remain green.

## Required Validation Categories

Each milestone should run the applicable subset of:

- Formatter and linter
- Unit tests
- Driver API package tests
- Core package tests
- Driver package tests
- Entry-point discovery tests
- Driver API compatibility tests
- Isolated wheel installation tests
- Existing CLI workflow tests
- Example configuration validation
- Structured unsupported/unknown behavior tests
- Physical regression where behavior or package boundaries could affect
  validated hardware workflows

Phase completion requires physical UHD-808 and UKM404 regression.

## Documentation Updates

At each milestone:

- Update the active phase status when milestone state changes.
- Add or update the relevant implementation report under `ai/implementation/`.
- Update `CHANGELOG.md` for completed user-visible or release-relevant work.
- Update stable docs only when behavior or architecture actually changes.
- Confirm `README.md`, `PROJECT_STATUS.md`, `docs/roadmap.md`, and
  `AGENTS.md` remain consistent.

## Phase 5 Non-Goals

- REST API or production server
- Authentication or authorization implementation
- Web, desktop, or tablet applications
- Interactive configuration authoring
- Windows Display Agent implementation
- PiKVM-specific implementation
- EDID, scaling, CEC, audio DSP policy, or other domain-specific execution
- New hardware drivers
- Multi-user orchestration
- Multi-fabric federation
- Plugin marketplace

REST API work is Phase 6. Domain-specific behavior should use typed policy
extensions built on the relationship model after the generic Phase 5 foundation
exists.

## Phase 6 Handoff Requirements

Before Phase 5 is complete:

- The internal relationship model is stable enough to expose through public
  APIs.
- Endpoint metadata and constraints are implemented across included drivers.
- Relationship intent, relationship groups, and managed scope have deterministic
  planner semantics.
- Unsupported and unknown outcomes are structured and documented.
- Existing CLI workflows continue operating.
- Existing physical UHD-808 and UKM404 workflows pass regression.
- Documentation, tests, examples, and package metadata agree.
