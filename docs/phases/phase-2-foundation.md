# Phase 2: Foundation

## Status

Complete

## Purpose

This document marks the transition from architecture definition into implementation.

Phase 1 established the vision, architecture, resource model, driver contract, capability model, transaction model, and reference hardware notes.

Phase 2 begins the construction of Workspace Fabric.

The goal of Phase 2 is not to control real hardware. The goal is to build the core orchestration foundation using mock drivers.

## Phase 2 Objective

Build a working core that can:

```text
load configuration
  -> build resource graph
  -> validate workspace
  -> plan transaction
  -> execute against mock drivers
  -> report resulting state
```

## Phase 2 Non-Goals

Phase 2 should not include:

- Real UHD-808 driver.
- Real UKM404 driver.
- PiKVM integration.
- Windows Display Agent.
- Production web UI.
- Multi-user support.
- Multi-fabric federation.
- Local Console Virtualization.
- Plugin marketplace.
- Advanced policy engine.

These features depend on the core foundation.

## Milestone 1: Repository Skeleton

Create the initial repository structure.

Expected folders:

```text
workspace-fabric/
  docs/
  examples/
  src/
  tests/
  .ai/
```

Acceptance criteria:

- Repository has agreed structure.
- Existing documentation is committed.
- AI guidance documents are committed.
- Example configuration exists.
- No production logic required yet.

## Milestone 2: Configuration Loader

Implement configuration loading.

Acceptance criteria:

- Load YAML config.
- Validate top-level schema version.
- Parse fabrics, drivers, hosts, displays, USB devices, matrices, and workspaces.
- Report clear validation errors.
- Unit tests cover valid and invalid config.

## Milestone 3: Resource Graph

Build the resource graph from configuration.

Acceptance criteria:

- Resource references resolve correctly.
- Missing references fail validation.
- Duplicate IDs fail validation.
- Per-matrix USB host maps are represented.
- Invalid USB route targets are detectable.
- Resource graph can be inspected or dumped for debugging.

## Milestone 4: Mock Drivers

Implement mock drivers.

Expected mock drivers:

- Mock video matrix driver.
- Mock USB matrix driver.
- Optional mock remote console driver.

Acceptance criteria:

- Mock drivers report capabilities.
- Mock drivers maintain internal state.
- Mock drivers support planned actions.
- Mock drivers can simulate unsupported capabilities.
- Mock drivers can simulate failures.

## Milestone 5: Capability Validation

Implement capability validation.

Acceptance criteria:

- Support `supported`, `unsupported`, and `unknown`.
- Support policies `ignore`, `prefer`, `require`, and `disable`.
- `prefer` produces warnings when unsupported.
- `require` fails validation when unsupported or unknown.
- Tests cover success, warning, and failure cases.

## Milestone 6: Transaction Planner

Implement transaction planning.

Acceptance criteria:

- A workspace can be converted into a transaction plan.
- Plan references driver instances.
- Plan includes video route actions.
- Plan includes USB route actions.
- Plan includes warnings for optional unsupported capabilities.
- Dry-run output is available.

## Milestone 7: Transaction Executor

Implement transaction execution against mock drivers.

Acceptance criteria:

- Plans execute against mock drivers.
- Mock state updates.
- Transaction results are structured.
- Partial failure can be represented.
- Transaction history is recorded in memory or simple local storage.

## Milestone 8: Minimal Interface

Implement a minimal CLI or REST API.

Preferred minimum CLI:

```text
workspace-fabric config validate
workspace-fabric graph show
workspace-fabric workspace list
workspace-fabric apply <workspace>
workspace-fabric apply <workspace> --dry-run
workspace-fabric state
```

Acceptance criteria:

- User can apply `work`, `desktop`, and `hybrid_meeting` against mock drivers.
- User can view resulting state.
- User can run dry-run.

## Phase 2 Completion Criteria

Phase 2 is complete when Workspace Fabric can apply example workspaces using mock drivers and produce explainable transaction results.

At that point, real driver development may begin.
-
