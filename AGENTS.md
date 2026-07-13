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
5. `ai/project.md`
6. The current phase document under `ai/implementation/`
7. `docs/philosophy.md`
8. `docs/architecture.md`
9. `docs/architecture/adr/`, especially ADR-0006 during Phase 4
10. `docs/driver-contract.md`
11. `docs/configuration-model.md`
12. `docs/capability-model.md`
13. `docs/developer-standards.md`
14. Relevant hardware documentation and observations

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

Phase 3 is complete. The current phase is:

```text
Phase 4 – Modular Driver Platform
```

The objective is to separate drivers from the core application without changing
working physical behavior.

Current sequence:

1. Driver packaging and discovery ADR
2. Monorepo package structure
3. Versioned Driver API package
4. Entry-point discovery
5. Driver metadata and catalog
6. Mock and OREI package migration
7. Lifecycle and compatibility validation
8. Physical regression testing

## Phase 4 Package Boundaries

The target dependency direction is:

```text
core ───────────────┐
                    ├──> driver-api
implementation ─────┘
```

Rules:

- Core code must not import vendor driver packages.
- Driver packages must not import core orchestration modules.
- Core and drivers may depend on the shared Driver API.
- Driver discovery must use Python package entry points.
- Do not implement production discovery by scanning arbitrary source folders.
- Existing driver type identifiers should remain stable.
- An unused installed driver must have no runtime side effects.
- A configured but missing driver must fail validation with a structured error.
- Driver versions must remain independent from the core version.

## Repository Direction

The repository remains a monorepo. The expected direction is:

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

Do not create separate Git repositories during Phase 4 unless explicitly
instructed.

The exact build-workspace tooling should be selected through focused evaluation
and documented before broad restructuring. Prefer standard Python packaging and
minimal custom tooling.

## Driver Discovery Contract

Drivers register under:

```text
workspace_fabric.drivers
```

Discovery should use `importlib.metadata.entry_points()` or the supported stable
equivalent.

The core must:

- Discover installed plugins
- Validate duplicate driver type identifiers
- Validate Driver API compatibility
- Isolate and report plugin-load failures
- Build a catalog usable by future Phase 5 APIs and authoring tools

## Development Expectations

Before changing code:

1. Identify the current milestone.
2. List the ADRs and stable documents governing the change.
3. Audit existing behavior before proposing a rewrite.
4. Identify expected files and packages to change.
5. Define acceptance criteria.
6. State backward-compatibility implications.

During Phase 4:

- Prefer extraction and adaptation over rewriting physical drivers.
- Keep each migration step buildable and testable.
- Preserve the working physical configuration.
- Use mock packages for discovery and lifecycle tests first.
- Avoid adding new hardware capabilities.
- Keep public configuration identifiers stable.
- Add compatibility adapters only when they are explicit, tested, and temporary.

## Testing Requirements

Every Phase 4 change should run the applicable formatter, linter, unit tests,
package build tests, and integration tests.

Coverage must include:

- Plugin discovery
- Duplicate driver type identifiers
- Missing driver
- Incompatible Driver API
- Plugin-load failure
- Installed but unused driver
- Driver uninstall after configuration removal
- Driver upgrade and rollback
- Existing transaction behavior
- Existing mock behavior
- Physical smoke-test regression at the end of the phase

Every coding-agent result must state the exact commands run and whether they
succeeded.

## Phase 4 Non-Goals

Do not implement these unless explicitly requested to satisfy a Phase 4
requirement:

- REST API or production server
- Authentication or permissions
- Web, desktop, or tablet applications
- Interactive configuration authoring
- Windows Display Agent
- PiKVM
- EDID, scaler, CEC, or ARC expansion
- New hardware drivers
- Multi-user orchestration
- Multi-fabric federation
- Plugin marketplace

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

Coding agents are expected to execute routine development commands directly within the repository workspace, including Python, pytest, Black, Ruff, package builds, and temporary virtual-environment validation.

Use the repository virtual environment when present:

```text
.\.venv\Scripts\python.exe
