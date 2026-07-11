# Phase 4 Transition Bundle

This bundle contains complete replacement and new Markdown files for the
Workspace Fabric v0.3.0 release and revised Phase 4–6 roadmap.

## Suggested Destinations

| Bundle file | Suggested repository destination | Action |
| --- | --- | --- |
| `README.md` | `README.md` | Replace |
| `PROJECT_STATUS.md` | `PROJECT_STATUS.md` | Replace |
| `docs/roadmap.md` | `docs/roadmap.md` | Replace |
| `docs/architecture.md` | `docs/architecture.md` | Replace |
| `docs/driver-contract.md` | `docs/driver-contract.md` | Replace |
| `docs/architecture/adr/ADR-0006-modular-driver-packaging-and-discovery.md` | Same path | Add |
| `ai/AGENTS.md` | `AGENTS.md` or `ai/AGENTS.md`, matching current repository convention | Replace |
| `ai/project.md` | `ai/project.md` | Replace |
| `ai/implementation/phase-3-hardware-drivers.md` | Current Phase 3 implementation document | Replace |
| `ai/implementation/phase-4-modular-driver-platform.md` | Phase 4 implementation document | Add |
| `ai/implementation/phase-5-productization.md` | Phase 5 implementation document | Add |
| `ai/implementation/phase-6-functional-and-driver-expansion.md` | Phase 6 implementation document | Add |
| `RELEASE_NOTES_v0.3.0.md` | Repository root or release documentation directory | Add |
| `RELEASE_CHECKLIST_v0.3.0.md` | Repository root or release documentation directory | Add |

## Files Not Replaced

The bundle intentionally does not replace hardware-specific protocol,
observation, smoke-test, configuration, or command-reference files that were
already updated during Phase 3. Review those separately for remaining stale
status language.

The bundle also does not modify Python package metadata or source code because
the complete repository was not available. The release checklist identifies the
manual version and validation steps.

## Important Review Point

Confirm the repository's actual AI-document paths. Existing project material has
used both root-level `AGENTS.md` and an `ai/` directory. Place the supplied
content according to the authoritative current layout rather than duplicating
both.
