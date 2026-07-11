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
  → Controller
  → Resource
  → Workspace
  → Scene
  → Patch
```

Drivers implement behavior. Controllers configure installed driver instances.
Resources model physical and logical reality. Workspaces describe reusable
environments. Scenes compose complete states. Patches perform focused partial
changes.

## Current Status

- Phase 1: Complete
- Phase 2: Complete
- Phase 3: Complete
- Current phase: Phase 4 – Modular Driver Platform
- Release target: `v0.3.0`
- Current milestone: Driver packaging and discovery architecture

## Phase 4 Objective

Separate driver implementations from the core application so drivers are
independently installable, discoverable, upgradeable, rollbackable, removable,
and versioned.

The repository remains a monorepo for now, but it should produce independent
packages for the core, Driver API, mock drivers, and physical drivers.

## Phase 4 Priorities

1. Accept the driver packaging and discovery ADR.
2. Audit existing driver registration and imports.
3. Establish the package-oriented monorepo layout.
4. Extract a versioned Driver API package.
5. Implement entry-point-based driver discovery.
6. Define plugin metadata and compatibility checks.
7. Migrate mock, UHD-808, and UKM404 drivers without rewriting their behavior.
8. Validate install, upgrade, rollback, removal, and missing-driver behavior.
9. Repeat the physical smoke tests.

## Phase 4 Architecture Rules

- The core must not import vendor driver implementations.
- Driver implementations must not import core orchestration modules.
- The core and drivers may depend on the shared Driver API package.
- Runtime driver discovery must use standard Python package metadata, not
  arbitrary filesystem scanning.
- Driver type identifiers in existing configuration should remain stable.
- An installed but unused driver must not affect runtime behavior.
- Removing an unused driver must not affect startup or unrelated controllers.
- A configured but missing driver must produce a structured validation error.
- Driver package versions are independent from the core version.
- Compatible driver updates must not require a core release.
- Existing physical behavior must be preserved during packaging changes.

## Explicit Phase 4 Non-Goals

Do not implement the following during the driver modularization phase unless
required to preserve existing behavior:

- Production REST API
- Web UI
- Desktop or tablet client
- Interactive configuration authoring
- Windows Display Agent
- PiKVM
- New UHD-808 features such as EDID, scaler, CEC, or ARC control
- Additional hardware drivers
- Multi-user access control
- Multi-fabric federation
- Plugin marketplace

## Later Phases

Phase 5 productizes the platform through APIs, authentication, configuration
authoring, diagnostics, interfaces, deployment, and a complete user-facing
release.

Phase 6 expands functionality and the driver ecosystem, including Windows
Display Agent, PiKVM, additional OREI capabilities, and new hardware or service
integrations.

## Engineering Guidance

- Preserve accepted ADRs and architecture boundaries.
- Favor incremental migration over rewrites.
- Preserve backward compatibility whenever practical.
- Keep the repository buildable and testable after each milestone.
- Use mock drivers first for contract and lifecycle tests.
- Keep physical regression tests as the final acceptance gate.
- Report unknown or unsupported behavior honestly.
- Record newly verified hardware behavior in the relevant observation files.
