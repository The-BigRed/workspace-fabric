# Workspace Fabric v0.4.0 Release Checklist

This checklist prepares the v0.4.0 release. Do not mark a step complete until
it has been run against the final release tree.

## Documentation Review

- [ ] Review `README.md`.
- [ ] Review `PROJECT_STATUS.md`.
- [ ] Review `CHANGELOG.md`.
- [ ] Review `docs/roadmap.md`.
- [ ] Review `docs/architecture.md`.
- [ ] Review `docs/driver-contract.md`.
- [ ] Review `docs/phases/phase-5-relationship-oriented-control-plane`.
- [ ] Confirm ADR-0005 and ADR-0009 are accepted and consistently titled.
- [ ] Confirm no active document treats Phase 4 as current.
- [ ] Confirm no document claims Phase 5 behavior is implemented.

## Version and Package Metadata

- [ ] Confirm release version target is `v0.4.0`.
- [ ] Read package versions from each package `pyproject.toml`.
- [ ] Confirm package metadata is internally consistent.
- [ ] Confirm CLI version output, if implemented, agrees with release policy.
- [ ] Decide whether package metadata versions require a release bump.

## Quality Gates

Run the repository-defined commands:

```powershell
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m build .\packages\core
git diff --check
```

- [ ] Formatter passes.
- [ ] Linter passes.
- [ ] Unit and integration tests pass.
- [ ] Core package tests pass.
- [ ] Package builds pass.
- [ ] Working tree whitespace check passes.

## Package Builds

Build fresh wheels for:

- [ ] `packages/driver-api`
- [ ] `packages/driver-mock`
- [ ] `packages/driver-orei-uhd808`
- [ ] `packages/driver-orei-ukm404`
- [ ] `packages/core`

## Isolated Installation

- [ ] Create a clean temporary virtual environment.
- [ ] Install the freshly built wheels.
- [ ] Import `workspace_fabric`.
- [ ] Import `workspace_fabric.drivers`.
- [ ] Call `get_driver_catalog()`.
- [ ] Confirm expected driver plugins are discovered through installed entry
  points.
- [ ] Confirm driver API compatibility validation succeeds.
- [ ] Confirm the core wheel does not contain vendor driver implementations.

## CLI and Configuration Workflows

- [ ] Validate `examples/physical-local.yaml`.
- [ ] Run existing CLI validation workflows.
- [ ] Run dry-run workflows for documented example workspaces.
- [ ] Confirm configured missing-driver behavior remains structured.
- [ ] Confirm installed-but-unused driver behavior remains side-effect free.

## Physical Regression

- [ ] Run physical UHD-808 regression for `desktop`.
- [ ] Run physical UHD-808 regression for `work`.
- [ ] Run physical UHD-808 regression for `hybrid_meeting`.
- [ ] Run physical UKM404 regression for `desktop`.
- [ ] Run physical UKM404 regression for `work`.
- [ ] Run physical UKM404 regression for `hybrid_meeting`.
- [ ] Confirm observed state is correct after each apply.
- [ ] Confirm structured hardware failure behavior remains intact.

## Release Artifacts

- [ ] Review `CHANGELOG.md`.
- [ ] Review `RELEASE_NOTES_v0.4.0.md`.
- [ ] Confirm release notes do not claim Phase 5 implementation.
- [ ] Confirm release checklist reflects final validation commands.
- [ ] Confirm documentation links render correctly.

## Repository State

```powershell
git status
git diff --check
git diff --stat
git tag --list v0.4.0
```

- [ ] No unintended files are staged.
- [ ] No secrets or private deployment data are included.
- [ ] Documentation paths match the repository layout.
- [ ] Generated files are either committed intentionally or ignored.
- [ ] `v0.4.0` tag does not already exist, or existing tag is intentional.

## Commit, Tag, and Publish

Do not perform these steps until the release owner approves them.

- [ ] Create the release commit.
- [ ] Create an annotated `v0.4.0` tag.
- [ ] Push the release commit.
- [ ] Push the release tag.
- [ ] Create the GitHub release using `RELEASE_NOTES_v0.4.0.md`.

## Phase Transition

- [ ] Confirm Phase 4 is complete.
- [ ] Confirm Phase 5 is current.
- [ ] Confirm Milestone 5.1 is the next implementation target.
- [ ] Confirm Phase 6 is Core Interfaces.
- [ ] Confirm Phase 7 is Configuration Experience.
- [ ] Confirm Phase 8 is Productization.
- [ ] Confirm Release 1.0 follows Phase 8.
