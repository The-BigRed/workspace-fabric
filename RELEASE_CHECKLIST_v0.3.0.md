# Workspace Fabric v0.3.0 Release Checklist

Historical release-provenance document. The active release checklist is
`RELEASE_CHECKLIST_v0.4.0.md`.

## Documentation Review

- [ ] Review `README.md`.
- [ ] Review `PROJECT_STATUS.md`.
- [ ] Review `docs/roadmap.md`.
- [ ] Review `docs/architecture.md`.
- [ ] Review `docs/driver-contract.md`.
- [ ] Accept ADR-0006.
- [ ] Review Phase 3 completion and Phase 4–6 plans.
- [ ] Confirm hardware observations and smoke-test records are current.

## Version

- [ ] Set the authoritative core version to `0.3.0`.
- [ ] Update any runtime `__version__` value.
- [ ] Confirm CLI version output reports `0.3.0` if implemented.
- [ ] Confirm package metadata is internally consistent.

## Quality Gates

Run the repository-defined commands. Typical commands may include:

```powershell
python -m ruff format --check .
python -m ruff check .
python -m pytest
workspace-fabric config validate --config examples\physical-local.yaml
```

- [ ] Formatting passes.
- [ ] Linting passes.
- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Physical configuration validates.
- [ ] Dry-run succeeds for all physical workspaces.
- [ ] Physical smoke test passes for `desktop`.
- [ ] Physical smoke test passes for `work`.
- [ ] Physical smoke test passes for `hybrid_meeting`.
- [ ] Observed state is correct after each apply.

## Repository State

```powershell
git status
git diff --check
git diff --stat
```

- [ ] No unintended files are staged.
- [ ] No secrets or private deployment data are included.
- [ ] Documentation paths match the repository layout.
- [ ] Generated files are either committed intentionally or ignored.

## Commit and Tag

Suggested release commit:

```powershell
git add .
git commit -m "Release Workspace Fabric v0.3.0"
```

Create an annotated tag:

```powershell
git tag -a v0.3.0 -m "Workspace Fabric v0.3.0 - first physically validated release"
```

Push commit and tag:

```powershell
git push origin HEAD
git push origin v0.3.0
```

- [ ] Release commit created.
- [ ] Annotated tag created.
- [ ] Commit pushed.
- [ ] Tag pushed.

## GitHub Release

- [ ] Create GitHub release from `v0.3.0`.
- [ ] Use `RELEASE_NOTES_v0.3.0.md` as the release body.
- [ ] Mark as prerelease if that matches the project policy.
- [ ] Confirm links and rendered formatting.

## Phase Transition

- [ ] Confirm `PROJECT_STATUS.md` names Phase 4 as current.
- [ ] Confirm current milestone is 4.1.
- [ ] Begin Phase 4 with an implementation audit before moving files.
- [ ] Do not add Phase 6 driver features during the packaging migration.
