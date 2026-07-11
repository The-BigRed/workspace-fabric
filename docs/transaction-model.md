# Workspace Fabric Transaction Model

## Purpose

Workspace Fabric applies workspace changes as transactions rather than as isolated hardware commands.

A workspace change may require multiple coordinated actions across video matrices, USB matrices, operating system agents, remote console drivers, and future resource providers. Transactions provide a structured way to validate, plan, execute, verify, and record those changes.

## Desired State

Workspace Fabric is a desired-state system.

Users describe the workspace they want.

Example:

```yaml
workspace: hybrid_meeting
video:
  primary_4k: desktop_dp1
  secondary_2k: work_laptop_dp1
usb:
  keyboard: desktop
  mouse: desktop
  camera: work_laptop
  microphone: work_laptop
  speakers: work_laptop
```

The core determines how to achieve that state.

## Transaction Flow

A transaction follows this process:

```text
1. Receive desired state.
2. Resolve logical resources.
3. Validate resource graph.
4. Validate capabilities.
5. Detect conflicts.
6. Build transaction plan.
7. Optionally return dry-run preview.
8. Execute actions through drivers.
9. Verify resulting state where possible.
10. Record transaction result.
```

## Transaction Plan

A transaction plan is a structured list of actions required to reach desired state.

Example:

```yaml
transaction:
  id: tx_001
  workspace: hybrid_meeting
  actions:
    - driver: uhd808
      type: video_route
      source: desktop_dp1
      destination: primary_4k
      input_port: 1
      output_port: 1

    - driver: uhd808
      type: video_route
      source: work_laptop_dp1
      destination: secondary_2k
      input_port: 3
      output_port: 2

    - driver: ukm404_a
      type: usb_route
      device: keyboard
      host: desktop
      device_port: 1
      host_port: 1

    - driver: ukm404_a
      type: usb_route
      device: camera
      host: work_laptop
      device_port: 3
      host_port: 2
```

For hardware video drivers, `source` and `destination` are explanatory resource context. The
orchestration layer resolves them to device-local `input_port` and `output_port` values before the
driver applies the route.

For hardware USB matrix drivers, `device` and `host` are explanatory resource context. The
orchestration layer resolves them to device-local `device_port` and `host_port` values before the
driver applies the route.

## Validation

Validation should occur before hardware changes.

Validation should check:

- Referenced resources exist.
- Routes are possible.
- Required capabilities are supported.
- Requested USB hosts are attached to the owning USB matrix.
- Requested video outputs are available.
- Scene scope is honored.
- Resource conflicts are detected.
- Locks or reservations are respected in future multi-user deployments.

## Dry Run

A dry run validates the request and produces a transaction plan without applying hardware changes.

Example CLI concept:

```text
workspace-fabric apply hybrid_meeting --dry-run
```

Dry run is important for:

- Debugging.
- UI previews.
- AI explainability.
- Automation safety.
- Documentation examples.

## Execution

During execution, the core sends planned actions to the appropriate drivers.

Drivers execute only their assigned actions.

Drivers do not coordinate directly with each other.

The core remains the transaction coordinator.

## Verification

After execution, the core should verify the result where possible.

Verification may include:

- Querying current route state.
- Querying capability state.
- Querying agent state.
- Comparing observed state to desired state.
- Recording unknown or unverifiable state explicitly.

Not all hardware supports full verification. Drivers must report unknown state honestly.

## Result States

Recommended transaction result states:

```text
success
success_with_warnings
partial_success
failed_validation
failed_apply
unknown
```

## Partial Success

Partial success is expected in real deployments.

Examples:

- Video routes apply successfully but USB routing fails.
- Routing succeeds but scaler configuration is unsupported.
- Windows Display Agent is offline.
- A remote console launches but virtual media is unavailable.

Workspace Fabric should report exactly which actions succeeded, failed, or were skipped.

## Transaction History

Each transaction should produce a durable record.

A transaction record should include:

- Transaction ID.
- Requested workspace or desired state.
- Validation result.
- Planned actions.
- Execution result.
- Warnings.
- Errors.
- Observed final state if available.
- Timestamp.
- Requesting operator or integration where available.

## Rollback

Rollback is not required for V0.

However, the transaction model should preserve enough information to allow future rollback or undo features.

## Execution Ordering

Some actions may require ordering.

Examples:

- Apply EDID before routing a display.
- Route video to PiKVM before routing PiKVM HID.
- Route USB before launching a remote console.
- Apply Windows display settings after video routing.

V0 may use simple ordering rules. Future versions may implement dependency-aware planning.

## V0 Requirements

V0 should support:

- Desired state input.
- Validation.
- Transaction plan generation.
- Dry run.
- Mock execution.
- Transaction result reporting.

V0 does not need:

- Real hardware execution.
- Rollback.
- Complex dependency graph execution.
- Multi-user locking.
