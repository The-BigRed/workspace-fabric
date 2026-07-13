# Workspace Fabric Documentation Manifest

This manifest lists durable documentation that should remain synchronized
across releases. It is not a list of transient implementation notes.

## Root Documents

| File | Purpose |
| --- | --- |
| `README.md` | Public project overview and current status |
| `PROJECT_STATUS.md` | Authoritative implementation status |
| `CHANGELOG.md` | Released change history |
| `CONTRIBUTING.md` | Contribution guidance |
| `AGENTS.md` | AI coding-agent guidance |

## Stable Architecture

| File | Purpose |
| --- | --- |
| `docs/architecture.md` | High-level architecture |
| `docs/philosophy.md` | Engineering philosophy |
| `docs/driver-contract.md` | Core/Driver API/driver package contract |
| `docs/configuration-model.md` | Configuration model |
| `docs/capability-model.md` | Capability model |
| `docs/developer-standards.md` | Development standards |
| `docs/glossary.md` | Shared terminology |

## Architectural Decision Records

| File | Status |
| --- | --- |
| `docs/architecture/adr/ADR-0001-configuration-object-model.md` | Accepted |
| `docs/architecture/adr/ADR-0002-controller-driver-boundary.md` | Accepted |
| `docs/architecture/adr/ADR-0003-workspaces-scenes-and-patches.md` | Accepted |
| `docs/architecture/adr/ADR-0004-configuration-authoring-and-yaml.md` | Accepted |
| `docs/architecture/adr/ADR-0005-driver-introspection-and-port-capabilities.md` | Accepted: Driver Metadata and Endpoint Introspection |
| `docs/architecture/adr/ADR-0006-modular-driver-packaging-and-discovery.md` | Accepted |
| `docs/architecture/adr/ADR-0007-authentication-and-authorization-boundary.md` | Accepted |
| `docs/architecture/adr/ADR-0008-local-administration-boundary.md` | Accepted |
| `docs/architecture/adr/ADR-0009-endpoint-relationships-and-route-orchestration.md` | Accepted |

## Phase Plans

| File | Status |
| --- | --- |
| `docs/phases/phase-1-architecture.md` | Complete |
| `docs/phases/phase-2-foundation.md` | Complete |
| `docs/phases/phase-3-hardware-drivers.md` | Complete |
| `docs/phases/phase-4-modular-driver-platform.md` | Complete |
| `docs/phases/phase-5-relationship-oriented-control-plane` | Current |
| `docs/phases/phase-6-core-interfaces.md` | Planned |
| `docs/phases/phase-7-configuration-experience.md` | Planned |
| `docs/phases/phase-8-productization.md` | Planned |

## Planning

| File | Purpose |
| --- | --- |
| `docs/roadmap.md` | Phase roadmap to Release 1.0 |
| `docs/planning/README.md` | Planning framework |
| `docs/planning/backlog.md` | Accepted future work |
| `docs/planning/release-strategy.md` | Release process |
| `docs/planning/architectural-considerations.md` | Future architecture considerations |

## Release Provenance

| File | Purpose |
| --- | --- |
| `RELEASE_NOTES_v0.3.0.md` | v0.3.0 release notes |
| `RELEASE_CHECKLIST_v0.3.0.md` | v0.3.0 release checklist |
| `RELEASE_NOTES_v0.4.0.md` | v0.4.0 release notes |
| `RELEASE_CHECKLIST_v0.4.0.md` | v0.4.0 release checklist |

## Notes

- Transient AI implementation reports under `ai/implementation/` are not listed
  here unless promoted into durable release or architecture documentation.
- Historical release notes and completed release checklists should be retained
  as release provenance.
