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
5. `docs/philosophy.md` for the engineering philosophy and design litmus test.
6. `docs/architecture.md` for the layered architecture and core boundaries.
7. `docs/resource-model.md`, `docs/configuration-model.md`,
   `docs/capability-model.md`, and `docs/transaction-model.md` for the core
   models.
8. `docs/driver-contract.md` before writing or changing any driver code.
9. `PROJECT_STATUS.md` for the current milestone, then the corresponding phase document
    (for example, `docs/phase-3-hardware-drivers.md`), followed by `ai/implementation-roadmap.md`.
10. `docs/developer-standards.md` and `ai/coding-guidelines.md` before making
   code changes.
11. `design/decisions/` for accepted Architecture Decision Records.
12. `examples/local-workspace.yaml` for the current mock configuration shape.
13. `docs/reference-platform.md` and and the appropriate device directory under `docs/hardware/`
    for reference hardware context before hardware-related work.

Use `docs/glossary.md` whenever terminology is unclear.

## Source of Truth

- Stable architecture and model documentation lives in `docs/`.
- Accepted design decisions live in `design/decisions/`.
- Current phase and milestone status lives in `PROJECT_STATUS.md`; phase-level
  sequencing lives in `docs/roadmap.md`.
- AI-specific summaries and guardrails live in `ai/`.
- Contribution expectations live in `CONTRIBUTING.md`.
- Examples are implementation patterns and test fixtures, not replacements for
  the model documents.
- Reference platform and hardware notes validate the architecture and guide
  driver work, but they do not define the core model.
- `docs/design/architecture-capture-2026-07.md` is historical design capture and
  source material. Prefer the permanent docs and ADRs for current decisions.

If documents disagree, prefer accepted ADRs first, then the stable documents in
`docs/`, then AI summaries in `ai/`, then examples. Update documentation when an
architecture change is intentionally made.

Hardware protocol references live under:

docs/hardware/

When implementing or modifying a hardware driver, read the corresponding
vendor documentation before writing code.

Driver implementations should match the documented protocol unless an
observation file explicitly documents verified behavior that differs.

## Project Objective

Workspace Fabric is a software-defined workspace control plane. Users describe
the workspace they want; the system validates that intent, plans a transaction,
and coordinates drivers to apply it across physical devices, software agents,
and remote services.

The core idea is intent over implementation. The project is not a KVM, matrix
controller, remote desktop launcher, or automation engine. It is the control
plane that automation systems and user interfaces consume.

## Current Scope

Check `PROJECT_STATUS.md` for the current phase and milestone. The project has completed
Phase 2: Foundation and is ready to begin Phase 3: Hardware Integration.

The current milestone is Driver Contract Hardening. Before implementing real hardware drivers,
stabilize and document the driver contract, including capabilities, observed state, errors,
timeouts, and transaction behavior.

The intended Phase 3 order is:

1. Driver contract hardening.
2. Physical lab configuration.
3. OREI UHD-808 video driver.
4. OREI UKM404 USB driver.
5. End-to-end physical smoke test.
6. Safety and recovery behavior.

Do not implement PiKVM integration, a production web UI, multi-user support, multi-fabric
federation, Local Console Virtualization, plugin marketplaces, or advanced policy engines
until the Phase 3 hardware milestones are complete.

## Architecture Boundaries

- Keep `src/workspace_fabric/core/` hardware agnostic.
- Put vendor-specific protocols and device behavior only in drivers.
- Treat resources, capabilities, transactions, and configuration as first-class
  models.
- Keep planning separate from execution.
- Drivers report capabilities and observed state, validate driver-specific
  actions, and apply assigned actions.
- Drivers must not coordinate directly with other drivers or make global policy
  decisions.
- Optional capabilities are negotiated per driver instance. Do not assume EDID,
  scaling, fast switching, HPD control, route query, or similar features exist.
- Resource attachment is explicit. Do not assume global port symmetry or shared
  USB host maps across matrices.

## Development Expectations

- Before making code changes, identify the current milestone, list the project documents used to
  guide the implementation, summarize the implementation plan, identify the files expected to
  change, and define the acceptance criteria. Do not proceed if the task conflicts with the
  documented milestone sequence.
- Do not rewrite architecture documents to justify an implementation shortcut. If implementation
  and documentation conflict, stop and report the conflict unless explicitly asked to update the
  architecture.
- Prefer small, focused changes aligned with the documented milestone sequence.
- Follow `CONTRIBUTING.md` for contributor expectations.
- Ask for clarification rather than inventing architecture that is not in the
  docs.
- Preserve abstraction boundaries even when only a single implementation currently exists.
  Avoid coupling core logic to specific hardware or protocols for convenience.
- Keep pull requests focused.
- Use mock drivers first to prove core behavior.
- Validate before applying changes.
- Return structured errors and warnings.
- Do not silently ignore invalid configuration.
- Logs should explain what was requested, planned, executed, and observed.
- When implementing or modifying a hardware driver, keep the associated
  hardware documentation synchronized. Driver behavior should remain consistent
  with `protocol-notes.md` and `driver.md`. Newly verified hardware behavior
  should be recorded in `observations.md` when it differs from vendor
  documentation or materially affects driver behavior.

## Coding Standards

This is a Python project. ADR 0001 records Python as the primary implementation
language.

Follow:

- `.editorconfig` for whitespace and file formatting.
- `pyproject.toml` for Black and Ruff settings.
- `docs/developer-standards.md` for engineering expectations.
- `ai/coding-guidelines.md` for AI-specific implementation rules.

Current formatter and lint expectations include Python 3.14, line length 100,
Black formatting, Ruff formatting, and Ruff lint rules `E`, `F`, `I`, `B`, and
`UP`.

Workspace Fabric targets the latest stable CPython release. Contributors should develop and test
using the version specified in `pyproject.toml`.

## Testing Requirements

Every core behavior should include unit tests for success, validation failures,
and edge cases. Use mock drivers whenever practical.

Every Codex change should:

- Include the exact commands used for formatting, linting, and testing.
- State whether those commands completed successfully.
- Explain any skipped tests or known limitations.

Minimum early test coverage should include:

- Valid configuration.
- Missing references.
- Duplicate IDs.
- Valid USB route.
- Invalid USB route caused by missing host attachment.
- Capability `prefer` warning.
- Capability `require` failure.
- Transaction dry run.
- Mock transaction execution.

## Repository Navigation

- `docs/` contains stable project documentation.
- `docs/hardware/` contains vendor-specific hardware documentation.

  Each supported hardware device should have its own directory containing:

  - Vendor manual(s) (read-only reference)
  - `protocol-notes.md` (engineering protocol reference)
  - `observations.md` (verified hardware behavior and lab discoveries)
  - `driver.md` (Workspace Fabric driver documentation)

  Hardware documentation supplements the driver implementation but does not
  define the Workspace Fabric architecture.
- `ai/` contains AI prompts, summaries, conventions, and roadmap guidance.
- `design/decisions/` contains accepted ADRs.
- `examples/` contains sample configuration.
- `src/workspace_fabric/config/` is for configuration loading and validation.
- `src/workspace_fabric/core/` is for resource graph, planning, transactions,
  and state.
- `src/workspace_fabric/drivers/` is for driver interfaces, mock drivers, and
  future hardware or service drivers.
- `src/workspace_fabric/api/` and `src/workspace_fabric/cli/` are interface
  layers over the same core services.
- `tests/` mirrors the implementation areas.

## Implementation Constraints

- YAML is the initial configuration format.
- V0 may start with a single config file but should not prevent later split
  configuration.
- Config must include a schema version and be validated before use.
- Missing references, duplicate IDs, invalid capability policies, and invalid
  routes should fail clearly.
- Dry-run planning is required before real application behavior.
- Transaction rollback is not required for V0, but transaction records should
  preserve enough information to support future rollback or undo.
- If hardware state cannot be queried, report `unknown`; do not pretend success
  or support.
- Reference hardware informs drivers but must not define the core architecture.

## Working Style

When implementing new functionality:

1. Understand before implementing.
2. Extend before replacing.
3. Prefer incremental pull requests over large changes.
4. Preserve existing architecture unless explicitly instructed otherwise.
5. Leave the repository in a buildable and testable state.
