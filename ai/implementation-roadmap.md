# Workspace Fabric Implementation Roadmap for AI

## Phase 2 Foundation

The project is now entering Phase 2.

Do not begin real hardware drivers until foundation milestones are complete.

## Milestone 1: Config Loader

Implement:

- YAML loading.
- Schema version check.
- Basic validation.
- Clear errors.

## Milestone 2: Resource Graph

Implement:

- Resource objects.
- Reference resolution.
- Graph validation.
- Per-matrix USB host maps.
- Inspection/debug output.

## Milestone 3: Mock Drivers

Implement:

- Mock video matrix.
- Mock USB matrix.
- Optional mock remote console.
- Capability reporting.
- Mock state.

## Milestone 4: Capability Validation

Implement:

- Capability status.
- Policies.
- Warning/failure behavior.

## Milestone 5: Transaction Planner

Implement:

- Workspace to transaction plan.
- Video route actions.
- USB route actions.
- Dry-run output.

## Milestone 6: Transaction Executor

Implement:

- Execute plans against mock drivers.
- Record results.
- Represent partial failure.

## Milestone 7: Minimal Interface

Implement one of:

- CLI first, or
- REST API first.

CLI is acceptable for early development.

Minimum commands:

```text
workspace-fabric config validate
workspace-fabric graph show
workspace-fabric workspace list
workspace-fabric apply <workspace>
workspace-fabric apply <workspace> --dry-run
workspace-fabric state
```
