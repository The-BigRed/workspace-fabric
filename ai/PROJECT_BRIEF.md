# Workspace Fabric AI Project Context

## Project Summary

Workspace Fabric is a software-defined workspace control plane. It translates
user intent into deterministic operations across hardware, software agents, and
remote services.

Workspace Fabric is not an automation engine. Automation systems are consumers
of its public API.

## Configuration Model

```text
Driver
  -> Controller
  -> Resource
  -> Workspace
  -> Scene
  -> Patch
```

Drivers implement behavior. Controllers configure installed driver instances.
Resources model physical and logical reality. Workspaces describe reusable
environments. Scenes compose complete states. Patches perform focused partial
changes.

## Current Status

- Phase 1: Complete
- Phase 2: Complete
- Phase 3: Complete
- Phase 4: Complete
- Current phase: Phase 5 - Relationship-Oriented Control Plane
- Release transition: `v0.4.0` release candidate
- Current milestone: 5.1 - Endpoint Metadata

## Phase 5 Objective

Implement the relationship-oriented orchestration model defined by:

- ADR-0005: Driver Metadata and Endpoint Introspection
- ADR-0009: Endpoint Relationships and Route Orchestration

The goal is to make endpoint relationships, constraints, cardinality, managed
scope, and reconciliation explicit in the core while preserving the modular
driver platform established during Phase 4.

## Phase 5 Priorities

1. Expand Driver API endpoint metadata.
2. Update mock drivers first where practical.
3. Add endpoint constraint validation.
4. Model relationships independently of native driver actions.
5. Extend the planner to reason about relationship intent.
6. Preserve existing point-to-point route actions as execution primitives.
7. Integrate existing OREI drivers without adding hardware capabilities.
8. Validate structured supported, unsupported, and unknown outcomes.
9. Repeat physical regression at phase completion.

## Phase 5 Architecture Rules

- Drivers describe; the core decides.
- Endpoint metadata and constraints are driver responsibilities.
- Relationship intent, reconciliation, and global policy are core
  responsibilities.
- Core code must not import vendor driver implementations.
- Driver implementations must not import core orchestration modules.
- Runtime driver discovery must use standard Python package metadata.
- Existing validated physical behavior must remain operational at every
  milestone boundary.
- Pre-1.0 internal interfaces may change when required by accepted ADRs, but
  each completed milestone and release must be coherent and operational.

## Explicit Phase 5 Non-Goals

Do not implement the following during Phase 5 unless required to preserve
existing behavior:

- Production REST API
- Web UI
- Desktop or tablet client
- Interactive configuration authoring
- Windows Display Agent
- PiKVM-specific implementation
- EDID, scaler, CEC, or ARC control
- Audio DSP policy
- Additional hardware drivers
- Multi-user access control
- Multi-fabric federation
- Plugin marketplace

REST API work is deferred to Phase 6. Domain-specific hardware execution is
future driver or policy-extension work built on the Phase 5 relationship model.

## Later Phases

Phase 6 exposes the control plane through stable public interfaces.

Phase 7 provides the interactive configuration experience.

Phase 8 productizes the platform for Release 1.0.

## Engineering Guidance

- Preserve accepted ADRs and architecture boundaries.
- Favor incremental migration over rewrites.
- Keep the repository buildable and testable after each milestone.
- Use mock drivers first for contract and planner tests.
- Keep physical regression tests as the final phase acceptance gate.
- Report unknown or unsupported behavior honestly.
- Record newly verified hardware behavior in the relevant observation files.
