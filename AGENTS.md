# AGENTS.md

This file is an entry point for AI coding agents working in this repository.
It does not replace the project documentation. When details matter, read and
follow the referenced documents.

## Read First

Start with these documents, in this order:

1. `README.md` for the project summary, status, and repository layout.
2. `PROJECT_STATUS.md` and `docs/roadmap.md` for the current phase, current
   milestone, and longer-term phase sequence.
3. `CONTRIBUTING.md` for contribution expectations.
4. `ai/project.md` for AI-specific project context, current phase, priorities,
   and explicit non-goals.
5. `ai/tasks/` for reusable implementation workflows. Use the task that best
   matches the requested work before inventing a new implementation process.
6. `docs/philosophy.md` for the engineering philosophy and design litmus test.
7. `docs/architecture.md` for the layered architecture and core boundaries.
8. `docs/architecture/adr/` for accepted configuration architecture decisions.
9. `docs/resource-model.md`, `docs/configuration-model.md`,
   `docs/capability-model.md`, and `docs/transaction-model.md` for the core
   models.
10. `docs/driver-contract.md` before writing or changing driver code.
11. The phase document corresponding to the current milestone, followed by
    `ai/implementation-roadmap.md`.
12. `docs/developer-standards.md` and `ai/coding-guidelines.md` before making
    code changes.
13. `design/decisions/` for earlier accepted Architecture Decision Records.
14. `examples/local-workspace.yaml` and the current physical lab seed for
    configuration examples and test-fixture shapes.
15. `docs/reference-platform.md` and the appropriate device directory under
    `docs/hardware/` before hardware-related work.

Use `docs/glossary.md` whenever terminology is unclear.

## Source of Truth

- Stable architecture and model documentation lives in `docs/`.
- Configuration architecture decisions live in `docs/architecture/adr/`.
- Earlier accepted project ADRs may remain in `design/decisions/` until the
  repository adopts a single consolidated ADR location.
- Current phase and milestone status lives in `PROJECT_STATUS.md`; phase-level
  sequencing lives in `docs/roadmap.md`.
- AI-specific summaries and guardrails live in `ai/`.
- Contribution expectations live in `CONTRIBUTING.md`.
- Examples are implementation patterns and test fixtures, not replacements for
  model documents or accepted ADRs.
- Reference platform and hardware notes validate the architecture and guide
  driver work, but they do not define the core model.
- Historical architecture captures are source material only. Prefer permanent
  documentation and accepted ADRs for current decisions.

If documents disagree, prefer accepted ADRs first, then stable documents in
`docs/`, then AI summaries in `ai/`, then examples. Do not silently choose an
implementation-specific interpretation when an architectural conflict exists.

Hardware protocol references live under:

```text
docs/hardware/
```

When implementing or modifying a hardware driver, read the corresponding
vendor documentation before writing code.

Driver implementations should match the documented protocol unless an
observation file explicitly records verified behavior that differs.

## Project Objective

Workspace Fabric is a software-defined workspace control plane. Users describe
the environment or focused change they want; the system validates that intent,
plans a transaction, and coordinates drivers to apply it across physical
devices, software agents, and remote services.

The core idea is intent over implementation. The project is not a KVM, matrix
controller, remote desktop launcher, or automation engine. It is the control
plane that automation systems and user interfaces consume.

## Current Scope

Check `PROJECT_STATUS.md` for the current phase and milestone. The project has
completed Phase 2: Foundation and is executing Phase 3: Hardware Integration.

The intended Phase 3 order is:

1. Driver contract hardening.
2. Physical lab configuration.
3. OREI UHD-808 video driver.
4. OREI UKM404 USB driver.
5. Windows Display Agent.
6. PiKVM integration.
7. End-to-end physical smoke test.
8. Safety and recovery behavior.

Do not implement a production configuration UI, multi-user support,
multi-fabric federation, Local Console Virtualization, plugin marketplaces, or
advanced policy engines until the Phase 3 hardware milestones are complete.

## Architecture Boundaries

- Keep `src/workspace_fabric/core/` hardware agnostic.
- Put vendor-specific protocols and device behavior only in drivers.
- Treat controllers, resources, capabilities, transactions, and configuration
  as first-class models.
- Keep planning separate from execution.
- Drivers report capabilities and observed state, validate driver-specific
  actions, and apply assigned actions.
- Drivers must not coordinate directly with other drivers or make global policy
  decisions.
- Optional capabilities are negotiated per controller instance. Do not assume
  EDID, scaling, fast switching, HPD control, route query, or similar features
  exist.
- Resource attachment is explicit. Do not assume global port symmetry or shared
  USB host maps across matrices.

## Configuration Object Model

Workspace Fabric uses the following conceptual hierarchy:

```text
Driver
  ↓
Controller
  ↓
Resource
  ↓
Workspace
  ↓
Scene
  ↓
Patch
```

Definitions:

- A **driver** implements hardware- or service-specific behavior in code.
- A **controller** is a configured instance of a driver that communicates with
  one physical device, software agent, or service.
- A **resource** represents a physical device, logical object, or routable
  endpoint.
- A **workspace** describes a reusable operating environment.
- A **scene** composes one or more workspaces into a complete requested system
  configuration.
- A **patch** performs a focused, partial change to the current state while
  leaving unrelated state unchanged.

Do not use `driver` to mean a configured physical device. Configuration should
refer to a controller instance, while the controller selects the driver
implementation.

Do not collapse workspaces, scenes, and patches into one generic preset type.
Their differing scope and application semantics are intentional.

Do not introduce alternate configuration abstractions without first reviewing
the accepted ADRs and updating them when the architecture intentionally changes.

## Configuration Authoring Direction

YAML is the initial serialized configuration format and remains an exposed,
editable source of truth. It is not intended to be the final primary authoring
experience.

The long-term configuration workflow should:

1. Let the user select a device driver.
2. Collect the connectivity settings required by that driver.
3. Create and validate a controller instance.
4. Query the controller for identity, ports, and supported capabilities when
   the hardware permits.
5. Let the user create resources and map them to the discovered endpoints that
   reflect physical reality.
6. Let the user compose resources into workspaces, scenes, and patches.
7. Serialize the resulting configuration to YAML.

Drivers should expose machine-readable configuration requirements, port
descriptions, endpoint direction, media type, and capabilities wherever
practical. Configuration interfaces should consume that metadata rather than
embedding device-specific behavior in the UI.

Do not prematurely implement the production configuration application during
Phase 3. Preserve the model and driver metadata needed to support it later.

## Development Expectations

- Before making code changes, identify the current milestone, list the project
  documents used to guide the implementation, summarize the implementation
  plan, identify files expected to change, and define acceptance criteria.
- Do not proceed when a task conflicts with the documented milestone sequence.
- Do not rewrite architecture documents to justify an implementation shortcut.
  If implementation and documentation conflict, stop and report the conflict
  unless explicitly asked to update the architecture.
- Prefer small, focused changes aligned with the milestone sequence.
- Follow `CONTRIBUTING.md` for contributor expectations.
- Ask for clarification rather than inventing architecture absent from the
  documentation.
- Preserve abstraction boundaries even when only one implementation exists.
- Avoid coupling core logic to specific hardware or protocols for convenience.
- Use mock drivers first to prove core behavior.
- Validate before applying changes.
- Return structured errors and warnings.
- Do not silently ignore invalid configuration.
- Logs should explain what was requested, planned, executed, and observed.
- Keep hardware documentation synchronized with driver behavior.
- Record newly verified hardware behavior in `observations.md` when it differs
  from vendor documentation or materially affects driver behavior.
- Prefer reusable workflows in `ai/tasks/` over ad hoc implementation
  processes. Update the appropriate task when a better workflow is discovered.

## Coding Standards

This is a Python project. The existing language-selection ADR records Python as
the primary implementation language.

Follow:

- `.editorconfig` for whitespace and file formatting.
- `pyproject.toml` for Black and Ruff settings.
- `docs/developer-standards.md` for engineering expectations.
- `ai/coding-guidelines.md` for AI-specific implementation rules.

Current formatter and lint expectations include Python 3.14, line length 100,
Black formatting, Ruff formatting, and Ruff lint rules `E`, `F`, `I`, `B`, and
`UP`.

Workspace Fabric targets the latest stable CPython release. Contributors should
develop and test using the version specified in `pyproject.toml`.

## Testing Requirements

Every core behavior should include unit tests for success, validation failures,
and edge cases. Use mock drivers whenever practical.

Every Codex change should:

- Include the exact commands used for formatting, linting, and testing.
- State whether those commands completed successfully.
- Explain skipped tests or known limitations.

Minimum early test coverage should include:

- Valid configuration.
- Missing references.
- Duplicate IDs.
- Unknown driver type.
- Invalid controller configuration.
- Valid USB route.
- Invalid USB route caused by missing host attachment.
- Capability `prefer` warning.
- Capability `require` failure.
- Transaction dry run.
- Mock transaction execution.
- Workspace application.
- Scene composition.
- Patch application that leaves unrelated state unchanged.

## Repository Navigation

- `docs/` contains stable project documentation.
- `docs/architecture/adr/` contains accepted configuration architecture ADRs.
- `docs/hardware/` contains vendor-specific hardware documentation.

  Each supported hardware device should have its own directory containing:

  - Vendor manual(s), retained as read-only references
  - `protocol-notes.md`
  - `observations.md`
  - `driver.md`

  Hardware documentation supplements the driver implementation but does not
  define Workspace Fabric architecture.

- `ai/` contains AI prompts, summaries, conventions, and roadmap guidance.
- `design/decisions/` contains earlier accepted ADRs pending consolidation.
- `examples/` contains sample configuration and test fixtures.
- `src/workspace_fabric/config/` is for configuration loading and validation.
- `src/workspace_fabric/core/` is for resource graph, planning, transactions,
  and state.
- `src/workspace_fabric/drivers/` is for driver interfaces, mock drivers, and
  hardware or service drivers.
- `src/workspace_fabric/api/` and `src/workspace_fabric/cli/` are interface
  layers over the same core services.
- `tests/` mirrors the implementation areas.

## Implementation Constraints

- YAML is the initial configuration serialization format.
- V0 may start with a single config file but should not prevent later split
  configuration.
- Configuration must include a schema version and be validated before use.
- Missing references, duplicate IDs, unknown driver types, invalid controller
  settings, invalid capability policies, and invalid routes should fail clearly.
- Dry-run planning is required before real application behavior.
- Transaction rollback is not required for V0, but transaction records should
  preserve enough information for future rollback or undo.
- If hardware state cannot be queried, report `unknown`; do not pretend success
  or support.
- Reference hardware informs drivers but must not define core architecture.
- Patches must change only their declared scope unless an explicit conflict or
  hardware constraint requires a broader plan. Such effects must be surfaced
  during validation or dry-run.

## Working Style

When implementing new functionality:

1. Understand before implementing.
2. Extend before replacing.
3. Prefer incremental pull requests over large changes.
4. Preserve existing architecture unless explicitly instructed otherwise.
5. Leave the repository in a buildable and testable state.
