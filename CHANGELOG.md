# Changelog

All notable changes to Workspace Fabric are documented in this file.

The project follows the principles of **Keep a Changelog** and **Semantic
Versioning**.

## [Unreleased]

### Added

- Phase 4.5 driver metadata catalog for listing available and unavailable
  installed driver plugins with structured diagnostics.
- Serializable descriptor metadata for mock, UHD-808, and UKM404 driver
  packages covering configuration requirements, ports, and capabilities.
- Isolated wheel regression coverage for the `workspace-fabric-core` driver
  catalog package contents and installed entry-point discovery.
- Phase 4.6 driver migration regression coverage for core/package dependency
  boundaries.
- Portable sdist-to-wheel packaging regression coverage for
  `workspace-fabric-core`.
- Phase 4.7 lifecycle and compatibility regression coverage for installed,
  removed, upgraded, rolled back, missing, incompatible, broken, and duplicate
  driver plugins.
- Phase 4.8 installed-wheel physical regression coverage for the reference
  `desktop`, `work`, and `hybrid_meeting` workspace transitions using
  independently installed UHD-808 and UKM404 driver packages.

### Changed

- Mock, UHD-808, and UKM404 tests now exercise implementation classes from the
  independently installable driver packages.
- Driver package factories accept configuration-like objects without importing
  core configuration models.
- Core source now lives under `packages/core/src` so the core package is
  self-contained when built from its sdist.
- Configuration validation now checks configured driver types against installed
  entry-point discovery before controllers are constructed.
- Physical regression validation now exercises installed OREI driver packages
  and verifies observed UHD-808 and UKM404 state without reintroducing vendor
  implementations into the core package.

### Fixed

- `workspace-fabric-core` wheels now package the real `workspace_fabric`
  implementation, including `workspace_fabric.drivers`, instead of the stale
  Phase 4.2 scaffold-only package.
- `workspace-fabric-core` now builds successfully through the normal
  sdist-to-wheel PEP 517 flow without depending on repository-relative
  `../../src` paths.
- Configured missing, incompatible, duplicate, and broken driver plugins now
  fail with structured driver lifecycle diagnostics during validation.

### Removed

- Legacy mock, UHD-808, and UKM404 implementation modules from the core
  `workspace_fabric.drivers` package.

### Planned

Development toward Release 1.0 continues with:

- Phase 4 – Modular Driver Platform
- Phase 5 – Core Interfaces
- Phase 6 – Configuration Experience
- Phase 7 – Productization

Planned work is tracked in the project Backlog.

---

## [0.3.0] - 2026-07-10

### Added

- Physical hardware support validated.
- OREI UHD-808 HDMI matrix driver.
- OREI UKM404 USB matrix driver.
- Windows Display Agent architecture.
- PiKVM integration architecture.
- End-to-end physical routing validation.
- Driver capability model.
- Driver introspection model.
- Configuration object model.
- Workspace, Scene, and Patch architecture.
- Authentication and Authorization architecture (ADR-0007).
- Project planning framework.
- Release strategy.
- Architectural Considerations.
- Project Backlog.

### Changed

- Roadmap rewritten to conclude with Release 1.0.
- Development planning transitioned toward release-based governance.
- Documentation reorganized into Architecture, Planning, and History.
- README and supporting documentation synchronized with current architecture.

### Notes

Version 0.3 represents the first complete architectural checkpoint following
validation of the reference hardware environment.

The project is now transitioning from hardware integration into development of
the public interfaces and user experience.

---

## [0.2.0]

### Added

- Configuration loader.
- Resource graph.
- Capability validation.
- Transaction planner.
- Transaction executor.
- Mock driver framework.
- Persistent state support.
- Initial command-line interface.

### Notes

Version 0.2 established the hardware-independent Workspace Fabric control
plane.

---

## [0.1.0]

### Added

- Initial repository.
- Core project philosophy.
- Architectural vision.
- Initial documentation.
- Architectural Decision Record framework.

### Notes

Version 0.1 established the architectural foundation upon which Workspace
Fabric is built.
