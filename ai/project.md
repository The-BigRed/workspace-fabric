# Workspace Fabric AI Project Context

## Project Summary

Workspace Fabric is a software-defined workspace control plane.

It translates user intent into deterministic operations across hardware,
software agents, and remote services.

## Core Idea

Workspace Fabric is not a KVM, matrix controller, remote desktop launcher, or
automation platform. It is the control plane consumed by those systems.

## Configuration Model

Driver
→ Controller
→ Resource
→ Workspace
→ Scene
→ Patch

Drivers implement behavior.
Controllers configure driver instances.
Resources model physical reality.
Workspaces describe reusable environments.
Scenes compose complete configurations.
Patches perform focused changes to the current state.

## Current Phase

Phase 3 – Hardware Integration

The goal is to validate the architecture against real hardware.

## AI Guidance

- Preserve abstraction boundaries.
- Keep drivers hardware-specific.
- Keep the core hardware-agnostic.
- Do not collapse workspaces, scenes, and patches into a single concept.
- Treat YAML as the serialized configuration, not the intended long-term authoring experience.
- Drivers should expose configuration requirements, ports, endpoint types, and capabilities suitable for future interactive configuration.

## Phase 3 Priorities

1. Driver contract
2. Physical lab
3. UHD-808
4. UKM404
5. Windows Display Agent
6. PiKVM
7. Physical validation
8. Safety/recovery
