# Workspace Fabric Driver Contract

## Purpose

This document defines the responsibilities and boundaries of Workspace Fabric drivers.

Drivers isolate vendor-specific behavior from the core orchestration engine. The core should never directly speak RS-232, TCP control protocols, Redfish, PiKVM APIs, Windows APIs, or any other vendor-specific interface.

## Driver Role

A driver is a software module that connects Workspace Fabric to a hardware device, software agent, platform, or service.

Examples:

- OREI UHD-808 video matrix driver.
- OREI UKM404 USB matrix driver.
- PiKVM driver.
- Windows Display Agent driver.
- iDRAC driver.
- Proxmox driver.
- Enterprise IP-KVM driver.

## Core Responsibilities

The Workspace Fabric core is responsible for:

- Loading configuration.
- Maintaining the resource graph.
- Maintaining desired and observed state.
- Validating workspace requests.
- Planning transactions.
- Coordinating driver actions.
- Persisting state and transaction history.
- Exposing APIs and user interfaces.

## Driver Responsibilities

A driver is responsible for:

- Connecting to its target device, service, or agent.
- Reporting capabilities.
- Reporting observed state where possible.
- Validating driver-specific actions.
- Translating generic actions into native commands.
- Applying assigned actions.
- Returning structured results.
- Returning structured errors.

## Driver Non-Responsibilities

A driver should not:

- Make global policy decisions.
- Coordinate directly with other drivers.
- Modify unrelated resources.
- Interpret high-level workspace intent.
- Assume global topology.
- Own the transaction engine.
- Hide unsupported features by pretending they succeeded.

## Driver Instances

Workspace Fabric must support multiple instances of the same driver type.

Example:

```yaml
drivers:
  uhd808_main:
    type: orei_uhd808
    connection:
      host: 192.0.2.10

  ukm404_a:
    type: orei_ukm404
    connection:
      host: 192.0.2.20

  ukm404_b:
    type: orei_ukm404
    connection:
      host: 192.0.2.21
```

Each driver instance has its own:

- Configuration.
- Capabilities.
- Resource attachments.
- Connection state.
- Observed state.

## Conceptual Interface

A driver should conceptually provide these functions:

```text
connect()
disconnect()
health()
get_capabilities()
get_state()
validate_action(action)
plan_action(action)
apply_action(action)
```

Exact method names may vary by implementation language.

## Connection

`connect()` establishes communication with the device, service, or agent.

It should not assume the device is fully functional. Capability and state queries should determine that separately.

## Health

`health()` reports whether the driver can currently communicate with its target.

Possible states:

```text
healthy
degraded
unreachable
unknown
```

## Capabilities

`get_capabilities()` returns the capabilities supported by this driver instance.

Capabilities must be instance-specific.

## State

`get_state()` reports observed state where available.

Drivers should distinguish:

- Observed state.
- Last known state.
- Assumed state.
- Unknown state.

If hardware cannot query state, the driver should report that limitation clearly.

## Validation

`validate_action(action)` checks whether a requested action is possible for this driver instance.

Validation should catch:

- Invalid ports.
- Unsupported capabilities.
- Invalid route requests.
- Unavailable target resources.
- Driver-specific constraints.

## Planning

`plan_action(action)` returns the hardware-specific action plan without applying it.

This enables dry runs and transaction previews.

## Applying

`apply_action(action)` performs the requested action.

The result should indicate:

- Success.
- Warning.
- Failure.
- Partial failure if applicable.
- Observed post-action state if available.

## Driver Coordination

Drivers must not communicate directly with each other.

All coordination happens through the core transaction engine.

Example:

- Video driver routes desktop video to PiKVM capture.
- USB driver routes PiKVM HID to desktop.
- PiKVM driver exposes launch URL.

The core coordinates these actions. The drivers remain independent.

## Error Categories

Recommended structured error categories:

```text
connection_failed
timeout
unsupported_capability
invalid_resource
invalid_port
invalid_route
hardware_rejected_command
state_query_failed
partial_apply
authentication_failed
authorization_failed
unknown_error
```

## Mock Drivers

Mock drivers are first-class drivers.

They should support:

- Capability reporting.
- State query.
- Route application.
- Dry-run planning.
- Failure injection.
- Unsupported capability simulation.

Mock drivers are required for V0 so the core can be implemented before hardware drivers.

## V0 Driver Scope

V0 should implement:

- Mock video matrix driver.
- Mock USB matrix driver.
- Mock remote console driver if useful.

Real UHD-808 and UKM404 drivers should wait until the core driver contract and transaction planner are stable.
