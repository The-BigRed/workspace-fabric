# Phase 6 – Core Interfaces

## Status

Planned

## Purpose

Expose the Workspace Fabric control plane through stable, versioned public
interfaces suitable for automation, user interfaces, and third-party
integration.

The purpose of this phase is **not** to add new routing capabilities. Instead,
it formalizes how external consumers interact with the functionality already
implemented during previous phases.

Completion of this phase establishes the Workspace Fabric API as the canonical
interface to the control plane.

---

# Design Principles

The following principles guide every deliverable in this phase.

- The public API is the canonical interface to Workspace Fabric.
- The CLI, Reference Web UI, desktop application, Home Assistant, OpenClaw,
  and third-party software are all API clients.
- The control plane remains the authoritative source for validation,
  authorization, planning, and transaction execution.
- Public interfaces remain deterministic and fully documented.
- API compatibility is preserved whenever practical.
- The local Administrative CLI exists solely for installation, bootstrap, and
  recovery. Its architectural boundary is defined by ADR-0008.

---

# Constraints

- Preserve the controller / driver boundary.
- Preserve Driver API compatibility introduced during Phase 4.
- Preserve transaction planning and execution behavior.
- Preserve YAML compatibility whenever practical.
- Introduce no privileged API consumers.
- Avoid duplicating orchestration logic outside the control plane.

---

# Milestone 6.1 – API Foundation

## Deliverables

- REST API service
- API versioning
- OpenAPI generation
- Standard error model
- Health endpoints
- Service configuration

## Acceptance Criteria

- API service starts successfully.
- Versioned endpoints are available.
- OpenAPI documentation is generated automatically.
- Health endpoints accurately report service status.
- Error responses are structured and documented.

---

# Milestone 6.2 – Administrative CLI

## Purpose

Implement the trusted local administrative interface used for installation,
bootstrap, recovery, and diagnostics.

## Deliverables

- Local administrative CLI executable
- Initial API key generation
- API key lifecycle management
- Configuration validation
- Service diagnostics
- Version reporting
- Health reporting
- Recovery tooling

## Acceptance Criteria

- Administrative CLI requires local operating-system access.
- Fresh installations can be initialized without a Web UI.
- Recovery from lost credentials is possible through local administration.
- Administrative operations invoke trusted application services directly.
- No network API endpoint bypasses authentication.
- Administrative functionality remains intentionally limited to installation,
  management, and recovery operations.

---

# Milestone 6.3 – Authentication and Authorization

## Deliverables

- API key authentication
- OAuth-style authorization scopes
- Authorization middleware
- Authenticated API key management
- Permission evaluation
- Authentication documentation

## Acceptance Criteria

- Requests without valid credentials are rejected.
- Authorization scopes are enforced consistently.
- Administrative CLI generated credentials function correctly.
- API key lifecycle management is available through authenticated API calls.
- No consumer receives implicit administrative privilege.

---

# Milestone 6.4 – Resource APIs

## Deliverables

REST endpoints for:

- Controllers
- Drivers
- Workspaces
- Scenes
- Patches
- Routes
- Relationships
- Capabilities
- Status
- Health

## Acceptance Criteria

- All managed resources expose stable UUIDs.
- CRUD operations are available where appropriate.
- Validation behavior matches existing CLI behavior.
- Public schemas are documented.

---

# Milestone 6.5 – Transaction APIs

## Deliverables

- Apply
- Preview
- Validate
- Dry-run
- Rollback preparation
- Transaction status

## Acceptance Criteria

- APIs utilize the existing transaction engine.
- No duplicate orchestration logic exists.
- Transaction results remain deterministic.
- Failure reporting is structured and documented.

---

# Milestone 6.6 – Public CLI

## Purpose

Provide a command-line client that consumes the public API.

## Deliverables

- Workspace commands
- Scene commands
- Patch commands
- Route commands
- Status commands
- Authentication support
- Connection profiles
- Output formatting

## Acceptance Criteria

- CLI communicates exclusively through the public API.
- CLI supports both local and remote Workspace Fabric instances.
- CLI behavior matches documented API behavior.
- No privileged internal application calls exist.

---

# Milestone 6.7 – API Documentation

## Deliverables

- OpenAPI specification
- Authentication guide
- Authorization scope reference
- API examples
- Error reference
- Integration examples

## Acceptance Criteria

- Documentation is sufficient for independent client development.
- Every public endpoint is documented.
- Authentication and authorization requirements are clearly described.

---

# Milestone 6.8 – Integration Validation

## Deliverables

Validate operation through:

- Public CLI
- API test suite
- Example client
- Automation examples

## Acceptance Criteria

- Every supported operation is available through the public API.
- Public CLI exercises only documented APIs.
- API behavior is deterministic.
- Third-party consumers require no knowledge of internal implementation.

---

# Phase Completion Criteria

Phase 6 is complete when:

- Stable versioned public APIs are available.
- API authentication and authorization are operational.
- Administrative CLI supports installation and recovery.
- Public CLI operates exclusively through the public API.
- API documentation is complete.
- Third-party clients can fully operate Workspace Fabric using only documented
  interfaces.

---

# Non-Goals

- Interactive configuration authoring
- Reference Web UI
- Desktop application
- Advanced topology visualization
- Driver onboarding workflows
- Plugin marketplace
- Multi-user management
- Federation
- Additional hardware capabilities

These capabilities are addressed in subsequent phases or future planning
documents.
