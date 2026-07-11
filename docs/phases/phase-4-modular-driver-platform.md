# Phase 4: Modular Driver Platform

## Status

Current

## Purpose

Separate driver implementations from the Workspace Fabric core so they can be
installed, discovered, upgraded, rolled back, removed, and versioned
independently.

The goal is not to redesign the working physical drivers. The goal is to
formalize package, dependency, discovery, compatibility, and lifecycle
boundaries before Phase 5 builds public APIs and configuration interfaces around
them.

## Constraints

- Keep one Git repository.
- Produce independently installable packages.
- Preserve stable driver type identifiers.
- Preserve current YAML compatibility whenever practical.
- Preserve Phase 3 physical behavior.
- Use standard Python packaging and entry points.
- Avoid new hardware capabilities during migration.

## Milestone 4.1 – Architecture and Audit

**Status:** ✅ **COMPLETE** (2026-07-11)

**Documentation:**
- [Detailed Audit Report](../../ai/implementation/milestone-4.1-audit.md)
- [Phase 4 Implementation Checklist](../../ai/implementation/phase-4-implementation-checklist.md)

### Deliverables

- ✅ ADR-0006 accepted and documented.
- ✅ Audit of current driver imports, registries, factories, and configuration
  validation complete.
- ✅ All vendor-specific dependencies in core code identified with locations.
- ✅ Current package and test coupling documented.
- ✅ Migration order and temporary compatibility adapters defined.

### Acceptance Criteria

- ✅ The current implementation is understood before restructuring.
- ✅ No speculative rewrite is approved without evidence from the audit.
- ✅ The package and dependency targets are explicit.

### Key Findings

**Hard-Coded Registry:**
- Location: `src/workspace_fabric/drivers/factory.py`
- Directly imports vendor drivers (OREI UHD-808, OREI UKM-404)
- Cannot be independently installed, upgraded, or removed

**Vendor-Specific Dependencies in Core:**
- 3 direct vendor imports in factory
- Re-exports in `drivers/__init__.py`
- Mock detection hard-coded in `cli/app.py`

**Migration Strategy:**
1. **4.2** – Monorepo packages (core, driver-api, driver-mock, driver-orei-*)
2. **4.3** – Versioned Driver API (extract interfaces, add compatibility version)
3. **4.4** – Entry-point discovery (replace factory registry)
4. **4.5** – Driver metadata catalog (plugin descriptor)

**Compatibility Guarantees:**
- No breaking changes to YAML configuration format
- Driver type identifiers remain stable
- Physical behavior preserved from Phase 3
- Temporary adapters designed for smooth transition

## Milestone 4.2 – Monorepo Package Structure

### Deliverables

Create or migrate toward:

```text
packages/
  core/
  driver-api/
  driver-mock/
  driver-orei-uhd808/
  driver-orei-ukm404/
```

Add a root development workspace for coordinated formatting, linting, testing,
and builds.

### Acceptance Criteria

- Each package has independent metadata.
- Each package can be built independently.
- Root development commands can validate all packages.
- Package ownership and dependency direction are documented.

## Milestone 4.3 – Versioned Driver API

### Deliverables

Extract shared portable contracts into `workspace-fabric-driver-api`:

- Base interfaces
- Action and result models
- Capability models
- Health and state models
- Structured issue categories
- Plugin descriptor
- Compatibility version

### Acceptance Criteria

- Driver API imports neither core nor vendor implementations.
- Core and drivers compile against the Driver API.
- Existing route actions remain compatible.
- API version validation is tested.

## Milestone 4.4 – Installed-Driver Discovery

### Deliverables

- Define entry-point group `workspace_fabric.drivers`.
- Discover plugins through `importlib.metadata`.
- Remove hard-coded vendor registration from core code.
- Detect duplicate driver type identifiers.
- Isolate and report plugin-load failures.

### Acceptance Criteria

- Installing a test plugin makes it discoverable.
- Uninstalling it removes it from the catalog.
- Core code contains no vendor-specific import for discovery.
- Discovery results are deterministic and diagnosable.

## Milestone 4.5 – Driver Metadata and Catalog

### Deliverables

Each plugin reports:

- Driver type
- Display name
- Driver package version
- Supported Driver API version
- Factory
- Configuration requirements
- Port metadata
- Capability metadata

### Acceptance Criteria

- Core can list all compatible installed drivers.
- Incompatible plugins are listed as unavailable with diagnostics or rejected
  according to the accepted API design.
- Catalog data is sufficient for Phase 5 controller onboarding.

## Milestone 4.6 – Driver Migration

### Deliverables

- Migrate mock drivers.
- Migrate UHD-808.
- Migrate UKM404.
- Preserve protocol implementations and tests.
- Preserve configuration identifiers.

### Acceptance Criteria

- Core imports no OREI implementation modules.
- Driver packages import no core orchestration modules.
- Existing unit and mocked transport tests pass.
- Existing physical configuration resolves the same driver types.

## Milestone 4.7 – Lifecycle and Compatibility

### Deliverables

Test:

- Install
- Unused installed driver
- Upgrade
- Rollback
- Removal
- Missing configured driver
- Incompatible Driver API
- Broken plugin
- Duplicate driver type

### Acceptance Criteria

- Removing an unused driver does not affect startup.
- Removing a configured driver yields `missing_driver` during validation.
- Compatible upgrades and rollbacks require no core change.
- Incompatible plugins fail before controller construction.
- Unrelated compatible drivers continue loading when practical.

## Milestone 4.8 – Physical Regression

### Deliverables

Repeat the Phase 3 validation sequence against independently installed OREI
driver packages.

### Acceptance Criteria

- `desktop`, `work`, and `hybrid_meeting` pass.
- UHD-808 state remains observed.
- UKM404 state remains observed.
- Structured failure behavior remains intact.
- No vendor-specific imports remain in the core distribution.

## Phase Completion Criteria

Phase 4 is complete when:

- Core and drivers are independently installable and versioned.
- Dynamic entry-point discovery is operational.
- Driver API compatibility is explicit.
- Missing and incompatible drivers produce structured diagnostics.
- Mock and OREI drivers are external to the core package.
- Driver lifecycle tests pass.
- Physical regression tests pass.

## Non-Goals

- Production API service
- Web or desktop UI
- Interactive configuration authoring
- Windows Display Agent
- PiKVM
- New OREI capabilities
- Additional hardware drivers
- Multi-user or federation features
