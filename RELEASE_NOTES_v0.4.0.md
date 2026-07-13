# Workspace Fabric v0.4.0

## Summary

Workspace Fabric `v0.4.0` closes Phase 4 - Modular Driver Platform.

This release separates the core, shared Driver API, mock drivers, and OREI
drivers into independently installable packages while preserving the validated
Phase 3 physical routing behavior.

It also accepts the architecture for Phase 5 - Relationship-Oriented Control
Plane. Phase 5 behavior is planned next; it is not implemented by this release.

## Highlights

- Modular core and driver package architecture
- Versioned Driver API package
- Entry-point driver discovery
- Driver catalog and metadata
- Mock driver package migration
- OREI UHD-808 and UKM404 package migration
- Driver lifecycle and compatibility validation
- Isolated wheel and sdist packaging validation
- Physical regression validation through independently installed OREI packages
- Accepted ADR-0005 rewrite: Driver Metadata and Endpoint Introspection
- Accepted ADR-0009: Endpoint Relationships and Route Orchestration
- Phase roadmap updated to add Phase 5 and renumber Core Interfaces,
  Configuration Experience, and Productization

## Current Package Metadata

Current package versions reported by package metadata:

| Package | Version |
| --- | --- |
| `workspace-fabric-core` | `0.3.0` |
| `workspace-fabric-driver-api` | `1.0.0` |
| `workspace-fabric-driver-mock` | `1.0.0` |
| `workspace-fabric-driver-orei-uhd808` | `1.0.0` |
| `workspace-fabric-driver-orei-ukm404` | `1.0.0` |

Release tagging and any package version updates are separate release operations.

## Compatibility Notes

Workspace Fabric remains pre-1.0. Historical internal interfaces and Driver API
details may change when required by accepted architecture.

Every completed phase and point release must still leave the repository
coherent, integrated, and operational. At this boundary, Phase 4 behavior
remains the operational baseline.

## Next Phase

Phase 5 implements relationship-oriented orchestration:

- Endpoint metadata
- Endpoint constraints
- Relationship intent
- Relationship groups
- Managed scope reconciliation
- Structured supported, unsupported, and unknown outcomes

REST APIs are deferred to Phase 6. Interactive configuration is deferred to
Phase 7. Productization and Release 1.0 readiness are deferred to Phase 8.
