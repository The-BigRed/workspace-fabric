# Workspace Fabric Architecture Summary for AI

## One-Sentence Summary

Workspace Fabric is a control plane that weaves independent workspace resources into a coherent, programmable operating environment.

## Core Architecture

```text
User / API / Automation
        |
        v
Workspace Fabric Core
        |
        +-- Resource Graph
        +-- State Engine
        +-- Capability Validator
        +-- Transaction Planner
        +-- Transaction Executor
        |
        v
Driver Manager
        |
        v
Driver Instances
        |
        v
Hardware / Agents / Remote Services
```

## Resource Model

The core manages logical resources:

- Fabrics
- Hosts
- Displays
- Video sources
- Video outputs
- USB matrices
- USB devices
- Remote consoles
- Workspaces
- Routes
- Capabilities

Implementation details such as HDMI ports, RS-232 commands, EDID blobs, and TCP sockets belong to driver configuration and driver internals.

## Driver Model

Drivers are resource providers and hardware translators.

Drivers:

- Report capabilities.
- Report observed state where possible.
- Validate driver-specific actions.
- Plan driver-specific actions.
- Apply driver-specific actions.

Drivers do not coordinate directly with other drivers.

## Capability Model

Capabilities are optional and instance-specific.

Policies:

- `ignore`
- `prefer`
- `require`
- `disable`

Do not assume optional features exist.

## Transaction Model

Workspace changes are transactions.

Flow:

```text
desired state
  -> validation
  -> transaction plan
  -> execution
  -> verification
  -> result
```

## V0 Scope

V0 uses mock drivers only.

V0 should prove:

```text
config -> graph -> validate -> plan -> mock apply -> state
```
