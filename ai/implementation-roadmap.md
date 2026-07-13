# Workspace Fabric Implementation Roadmap for AI

## Current Phase

Phase 5 - Relationship-Oriented Control Plane

The modular driver platform is complete. The current objective is to implement
the relationship-oriented orchestration model defined by ADR-0005 and ADR-0009
while preserving the Driver -> Controller -> Resource -> Workspace -> Scene ->
Patch object model.

The stable Phase 5 plan is `docs/phases/phase-5-relationship-oriented-control-plane`.

## Implementation Order

1. Milestone 5.1 - Endpoint Metadata
2. Milestone 5.2 - Relationship Model
3. Milestone 5.3 - Relationship Planner
4. Milestone 5.4 - Driver Integration
5. Milestone 5.5 - Relationship Groups
6. Milestone 5.6 - Planner Validation
7. Milestone 5.7 - Regression and Physical Validation

Do not create detailed implementation plans beyond the active milestone unless
requested.

## Architectural Guidance

- Drivers are reusable code.
- Controllers are configured driver instances.
- Resources represent physical devices and endpoints.
- Workspaces describe reusable operating environments.
- Scenes compose one or more workspaces.
- Patches perform partial, non-destructive routing changes.
- Endpoint relationships are planner concepts owned by the core.

Preserve this model. Do not invent alternate abstractions.

## Phase 5 Guidance

- Drivers describe endpoint metadata and constraints.
- The core decides relationship intent, reconciliation, managed scope, and
  global policy.
- Mock implementations should be updated before physical drivers where
  practical.
- Existing point-to-point route actions remain the current execution
  primitives.
- Existing validated UHD-808 and UKM404 behavior must remain operational.
- Unsupported and unknown outcomes must be structured and explicit.

## Deferred Until Later Phases

- REST API and public interface work: Phase 6
- Interactive configuration UI: Phase 7
- Product packaging and production release readiness: Phase 8
- EDID, scaling, CEC, audio DSP policy, PiKVM-specific behavior, Windows
  Display Agent behavior, and new hardware drivers: future driver or
  domain-policy work unless separately scheduled
