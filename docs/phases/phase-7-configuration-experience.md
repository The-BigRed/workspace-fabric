# Phase 7 – Configuration Experience

## Status

Planned

## Purpose

Provide a complete configuration and operational experience for Workspace
Fabric without requiring users to manually author or edit YAML.

Previous phases establish the architecture, hardware integration, modular
driver platform, relationship-oriented control plane, and stable public
interfaces. This phase focuses on making
those capabilities accessible through intuitive tooling while preserving YAML
as the authoritative serialized representation of the configuration model.

Completion of this phase enables operators to install hardware, build
workspaces, validate configurations, and manage their environment through
interactive tools.

---

## Design Principles

The following principles guide every deliverable in this phase.

- Configuration is authored through tools rather than manually editing YAML.
- YAML remains the canonical serialized representation of the configuration.
- The Reference Web UI is the default user interface for Workspace Fabric.
- The Reference Web UI remains an optional installation component.
- All user interfaces consume the same versioned public API.
- Additional user interfaces may be developed independently without requiring
  changes to the control plane.
- No user interface receives privileged access.
- Interactive tooling should prevent invalid configurations whenever practical.

---

## Constraints

- Preserve configuration model compatibility.
- Preserve Driver API compatibility.
- Preserve stable object UUIDs.
- Preserve the API-first architecture.
- Avoid duplicating validation logic within user interfaces.
- Keep the configuration service independent of any specific user interface.

---

## Milestone 7.1 – Configuration Service

### Deliverables

Implement a configuration service responsible for:

- Loading configuration
- Persisting configuration
- Validation
- Version management
- Import
- Export

### Acceptance Criteria

- Configuration service operates exclusively through the public API.
- Validation remains authoritative within the control plane.
- Configuration persistence is deterministic.

---

## Milestone 7.2 – Driver Onboarding

### Deliverables

Provide interactive workflows for:

- Discovering installed drivers
- Creating controllers
- Configuring controller properties
- Validating controller configuration
- Reporting compatibility issues

### Acceptance Criteria

- Supported drivers can be onboarded without editing YAML.
- Validation errors are presented before configuration is committed.
- Driver and endpoint metadata introduced during Phases 4 and 5 are sufficient
  for onboarding.

---

## Milestone 7.3 – Physical Topology

### Deliverables

Provide interactive management of:

- Controllers
- Devices
- Ports
- Connections
- Endpoint relationships

### Acceptance Criteria

- Physical topology can be created and modified interactively.
- Topology validation uses the existing capability model.
- Configuration remains consistent with the serialized YAML model.

---

## Milestone 7.4 – Workspace Authoring

### Deliverables

Provide interactive management of:

- Workspaces
- Scenes
- Patches
- Routes

Support:

- Create
- Edit
- Clone
- Delete
- Validate
- Preview

### Acceptance Criteria

- Complete workspace configurations can be authored without editing YAML.
- Validation occurs before changes are committed.
- Stable UUIDs are preserved.

---

## Milestone 7.5 – Reference Web UI

### Purpose

Provide the default browser-based user interface for Workspace Fabric.

The Reference Web UI is an optional installation component that consumes the
same public API available to every other client.

### Deliverables

Support:

- Dashboard
- Controller management
- Workspace management
- Scene management
- Patch management
- Route execution
- Status monitoring
- Diagnostics
- Authentication
- Configuration validation

### Acceptance Criteria

- The Reference Web UI consumes only documented public APIs.
- No privileged communication path exists.
- The Reference Web UI may be deployed independently of the Workspace Fabric
  controller.
- Complete configuration and operational workflows are available through the
  interface.

---

## Milestone 7.6 – User Experience

### Deliverables

Improve operational workflows including:

- Configuration validation
- Apply preview
- Confirmation dialogs
- Progress reporting
- Transaction history
- Error presentation
- Context-sensitive help

### Acceptance Criteria

- Common operational tasks require minimal manual intervention.
- User feedback is timely and actionable.
- Recovery guidance is available for common failures.
- Operators can understand planned actions before they are executed.

---

## Milestone 7.7 – End-to-End Validation

### Deliverables

Validate complete workflows including:

- New installation
- Driver onboarding
- Topology creation
- Workspace creation
- Route execution
- Configuration persistence
- Restart and recovery

### Acceptance Criteria

- A new operator can configure a functional Workspace Fabric installation
  without manually editing YAML.
- Configuration survives restart.
- Physical routing operates correctly.
- Validation remains deterministic.
- The complete workflow is achievable using only the Administrative CLI,
  public API, Reference Web UI, and documented procedures.

---

## Phase Completion Criteria

Phase 7 is complete when:

- Interactive configuration replaces manual YAML authoring.
- Driver onboarding is fully operational.
- Physical topology can be managed interactively.
- Workspaces, scenes, patches, and routes can be authored interactively.
- The Reference Web UI provides complete configuration and operational
  workflows.
- Every supported configuration task can be completed without manually editing
  YAML.
- Configuration remains API-first and YAML-compatible.

---

## Non-Goals

- Product packaging
- Installation tooling
- Backup and restore
- Release engineering
- Production diagnostics
- Long-term maintenance tooling
- Native desktop applications
- Enterprise deployment features
- Plugin marketplace

These capabilities are addressed during Productization or future planning
documents.
