# AGENTS.md

This file is the entry point for AI coding agents working in Workspace Fabric.
It supplements, but does not replace, the stable project documentation and
accepted ADRs.

## Read First

Read these documents in order:

1. `README.md`
2. `PROJECT_STATUS.md`
3. `docs/roadmap.md`
4. `CONTRIBUTING.md`
5. `ai/PROJECT_BRIEF.md`
6. The current phase document under `docs/phases/`
7. The current implementation checklist under `ai/implementation/`
8. `docs/philosophy.md`
9. `docs/architecture.md`
10. `docs/architecture/adr/`, especially ADR-0005, ADR-0006, and ADR-0009
11. `docs/driver-contract.md`
12. `docs/configuration-model.md`
13. `docs/capability-model.md`
14. `docs/developer-standards.md`
15. Relevant hardware documentation and observations

Use `docs/glossary.md` whenever terminology is unclear.

## Source of Truth

When documents disagree, prefer:

1. Accepted ADRs
2. Stable documents under `docs/`
3. `PROJECT_STATUS.md` and `docs/roadmap.md`
4. AI guidance under `ai/`
5. Examples and historical captures

Do not rewrite architecture documentation to justify an implementation
shortcut. Report conflicts before implementing behavior that contradicts an
accepted ADR.

## Project Objective

Workspace Fabric is a software-defined workspace control plane. It validates,
plans, executes, and observes deterministic changes across physical devices,
software agents, and services.

Workspace Fabric is not an automation engine. OpenClaw, Home Assistant, AI, and
other systems consume its public API.

## Current Scope

Phase 4 is complete. The current phase is:

```text
Phase 5 - Relationship-Oriented Control Plane
```

The objective is to implement the relationship-oriented orchestration model
defined by accepted ADR-0005 and ADR-0009 while preserving the modular driver
platform established in Phase 4.

Current sequence:

1. Endpoint metadata
2. Relationship model
3. Relationship planner
4. Driver integration
5. Relationship groups
6. Planner validation
7. Regression and physical validation

## Enduring Package Boundaries

The Phase 4 package boundary remains authoritative:

```text
core ----------+
               +--> driver-api
implementation-+
```

Rules:

- Core code must not import vendor driver packages.
- Driver packages must not import core orchestration modules.
- Core and drivers may depend on the shared Driver API.
- Driver discovery must use Python package entry points.
- Do not implement production discovery by scanning arbitrary source folders.
- Existing driver type identifiers should remain stable unless an accepted ADR
  and release plan require a pre-1.0 breaking change.
- An unused installed driver must have no runtime side effects.
- A configured but missing driver must fail validation with a structured error.
- Driver versions must remain independent from the core version.

## Phase 5 Responsibility Boundary

The guiding rule is:

```text
Drivers describe; the core decides.
```

Driver responsibilities:

- Describe endpoint metadata and constraints.
- Report endpoint direction, accepted endpoint types, cardinality, disconnect
  support, and required-assignment behavior.
- Report capabilities as supported, unsupported, or unknown.
- Apply assigned device-local actions.
- Keep vendor-specific and domain-specific execution inside driver packages.

Core responsibilities:

- Interpret relationship intent.
- Reconcile desired state within managed scope.
- Apply global policy and conflict detection.
- Validate endpoint compatibility and cardinality.
- Produce deterministic transaction plans.
- Report structured unsupported, unknown, and non-executable outcomes.

Relationship extension points and structured unsupported/unknown outcomes are
in scope for Phase 5.

## Repository Direction

The repository remains a monorepo:

```text
packages/
  core/
  driver-api/
  driver-mock/
  driver-orei-uhd808/
  driver-orei-ukm404/

docs/
examples/
integration-tests/
scripts/
ai/
```

Do not create separate Git repositories unless explicitly instructed.

Prefer standard Python packaging and minimal custom tooling.

## Driver Discovery Contract

Drivers register under:

```text
workspace_fabric.drivers
```

Discovery should use `importlib.metadata.entry_points()` or the supported
stable equivalent.

The core must:

- Discover installed plugins
- Validate duplicate driver type identifiers
- Validate Driver API compatibility
- Isolate and report plugin-load failures
- Build a catalog usable by future public APIs and authoring tools

## Development Expectations

Before changing code:

1. Identify the current milestone.
2. List the ADRs and stable documents governing the change.
3. Audit existing behavior before proposing a rewrite.
4. Identify expected files and packages to change.
5. Define acceptance criteria.
6. State backward-compatibility implications.

During Phase 5:

- Implement mock drivers before physical drivers where practical.
- Keep existing validated physical functionality operational at every milestone
  boundary.
- Preserve the working physical configuration unless a documented migration is
  required.
- Avoid adding new hardware capabilities.
- Preserve stable public configuration identifiers whenever practical.
- Add compatibility adapters only when they are explicit, tested, and
  temporary.
- Do not represent a partially completed relationship migration as complete.

Pre-1.0 internal and Driver API changes are allowed when required by accepted
architecture, but every completed phase and point release must leave the
repository coherent, integrated, and operational.

## Testing Requirements

Every Phase 5 change should run the applicable formatter, linter, unit tests,
package build tests, isolated wheel tests, and integration tests.

Coverage must include:

- Endpoint metadata validation
- Relationship intent validation
- Cardinality validation
- Disconnect support and required-assignment behavior
- Structured supported, unsupported, and unknown outcomes
- Existing plugin discovery
- Existing driver lifecycle behavior
- Existing transaction behavior
- Existing mock behavior
- Existing physical UHD-808 and UKM404 regression at phase completion

Every coding-agent result must state the exact commands run and whether they
succeeded.

## Phase 5 Non-Goals

Do not implement these unless explicitly requested to satisfy a Phase 5
requirement:

- REST API or production server
- Authentication or permissions
- Web, desktop, or tablet applications
- Interactive configuration authoring
- Windows Display Agent
- PiKVM-specific implementation
- EDID, scaling, CEC, audio DSP policy, or other domain-specific execution
- New hardware drivers
- Multi-user orchestration
- Multi-fabric federation
- Plugin marketplace

REST API work is deferred to Phase 6. EDID, scaling, CEC, audio DSP policy, and
other domain-specific execution features are future driver or domain-policy
work built on top of the Phase 5 relationship model.

## Coding Standards

Workspace Fabric targets Python 3.13 or newer. Follow the version and tooling
specified by the active package `pyproject.toml` files.

- Prefer readability over cleverness.
- Use typed, explicit interfaces.
- Return structured errors.
- Avoid hidden global state.
- Preserve semantic versioning.
- Preserve backward compatibility whenever practical.
- Keep vendor-specific behavior inside driver packages.
- Keep orchestration policy inside the core.

## Command Execution

Coding agents are expected to execute routine development commands directly
within the repository workspace, including Python, pytest, Black, Ruff, package
builds, and temporary virtual-environment validation.

Use the repository virtual environment when present:

```text
.\.venv\Scripts\python.exe
```
