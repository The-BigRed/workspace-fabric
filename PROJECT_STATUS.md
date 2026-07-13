# Project Status

## Current Version

**v0.4.0 release candidate**

Workspace Fabric is being prepared for the v0.4.0 documentation and planning
release. Phase 4 is complete, and the repository is transitioning to Phase 5.

Current package metadata, read from package `pyproject.toml` files:

| Package | Version |
| --- | --- |
| `workspace-fabric-core` | `0.3.0` |
| `workspace-fabric-driver-api` | `1.0.0` |
| `workspace-fabric-driver-mock` | `1.0.0` |
| `workspace-fabric-driver-orei-uhd808` | `1.0.0` |
| `workspace-fabric-driver-orei-ukm404` | `1.0.0` |

Release publication, tagging, and package version changes are separate release
operations and are not performed by this documentation transition.

---

# Current Phase

**Phase 5 - Relationship-Oriented Control Plane**

## Objective

Implement the relationship-oriented orchestration model defined by accepted
ADR-0005 and ADR-0009 while preserving the Phase 4 modular driver platform.

Phase 5 starts with Milestone 5.1 - Endpoint Metadata.

## Governing Decisions

| Decision | Status | Purpose |
| --- | --- | --- |
| ADR-0005: Driver Metadata and Endpoint Introspection | Accepted | Drivers describe endpoint metadata and capabilities. |
| ADR-0009: Endpoint Relationships and Route Orchestration | Accepted | The core interprets endpoint relationships, cardinality, reconciliation, and route orchestration. |

Phase 5 does not implement REST APIs, user interfaces, EDID management, video
scaling, CEC, audio DSP policy, Windows Display Agent behavior, PiKVM behavior,
or other domain-specific execution features.

---

# Phase Status

| Phase | Status |
| --- | --- |
| Phase 1 - Architecture | Complete |
| Phase 2 - Foundation | Complete |
| Phase 3 - Hardware Integration | Complete |
| Phase 4 - Modular Driver Platform | Complete |
| Phase 5 - Relationship-Oriented Control Plane | Current |
| Phase 6 - Core Interfaces | Planned |
| Phase 7 - Configuration Experience | Planned |
| Phase 8 - Productization | Planned |
| Release 1.0 | Planned after Phase 8 |

---

# Phase 4 Completion Summary

Phase 4 established the modular driver platform:

- Monorepo package boundaries for core, Driver API, mock drivers, and OREI
  drivers.
- Versioned Driver API package.
- Entry-point driver discovery.
- Driver metadata catalog.
- Mock and OREI driver migration out of the core package.
- Lifecycle and compatibility validation.
- Isolated wheel and sdist packaging validation.
- Physical regression validation using independently installed OREI driver
  packages.

Phase 4 functionality must remain operational throughout Phase 5.

---

# Current Development Focus

Milestone 5.1 focuses on endpoint metadata. Drivers describe endpoint direction,
accepted endpoint types, cardinality constraints, disconnect support, required
assignment, and structured supported/unsupported/unknown outcomes. The core
uses that descriptive metadata to validate and plan relationship-oriented
intent.

The guiding boundary is:

- Drivers describe.
- The core decides.

Mock implementations should be updated before physical drivers where practical.
Existing validated physical behavior remains a release-boundary requirement.

---

# Reference Environment

The reference laboratory currently includes:

## Video

- OREI UHD-808 HDMI Matrix

## USB

- OREI UKM404 USB Matrix

## Hosts

- Windows Desktop
- Dell Laptop
- PiKVM

## Displays

- Primary 4K monitor
- Secondary 2K monitor

This environment serves as the primary validation platform for Workspace Fabric
development. Windows Display Agent and PiKVM-specific implementation work
remains deferred.

---

# Documentation Status

Current documentation includes:

- Architecture
- Philosophy
- Architectural Decision Records
- Driver Contract
- Capability Model
- Configuration Model
- Developer Standards
- Roadmap
- Planning Documents
- CHANGELOG

Documentation is synchronized with the v0.4.0 release-candidate transition.

---

# Repository Status

Current repository state:

- Architecture stabilized
- Governance established
- Physical baseline validated
- Modular driver platform completed
- Phase 5 relationship-oriented control-plane planning active
- No Phase 5 implementation included in this documentation transition

Workspace Fabric is progressing from modular driver packaging toward
relationship-oriented orchestration.

---

**Last Updated**

2026-07-13
