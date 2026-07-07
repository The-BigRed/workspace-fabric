# Workspace Fabric AI Project Context

## Project Summary

Workspace Fabric is a software-defined workspace control plane.

It weaves independent workspace resources into a coherent, programmable operating environment.

Users describe intent. Workspace Fabric translates that intent into coordinated actions across hardware devices, software agents, and remote console systems.

## Core Idea

Workspace Fabric is not a KVM, matrix controller, remote desktop launcher, or automation engine.

It is a resource orchestration platform.

## Key Principles

1. Resources represent user intent.
2. Intent over implementation.
3. Hardware enriches the model but never defines it.
4. Drivers isolate hardware behavior.
5. Capabilities are negotiated, not assumed.
6. Resource attachment is explicit.
7. Transactions over commands.
8. Automation is a first-class interface.
9. Manual operation remains possible.
10. Reference hardware is not the architecture.

## Current Phase

The project is entering Phase 2: Foundation.

The goal is to build the core orchestration engine using mock drivers before writing real hardware drivers.

## Do Not Do These Things

Do not:

- Put vendor-specific protocol code in the core.
- Assume one global USB host map.
- Assume all matrices support EDID, scaling, fast switching, or HPD control.
- Implement real UHD-808 or UKM404 drivers before mock drivers.
- Build a polished UI before the planner and transaction engine work.
- Treat PiKVM as required for Workspace Fabric.
- Implement multi-fabric federation in V0.
- Implement multi-user RBAC in V0.
- Implement Windows Display Agent in V0.

## Implementation Priority

Build in this order:

1. Configuration loader.
2. Resource graph.
3. Mock drivers.
4. Capability validation.
5. Transaction planner.
6. Transaction executor.
7. Minimal CLI/API.
8. Real hardware drivers.
