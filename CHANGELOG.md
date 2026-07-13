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

### Fixed

- `workspace-fabric-core` wheels now package the real `workspace_fabric`
  implementation, including `workspace_fabric.drivers`, instead of the stale
  Phase 4.2 scaffold-only package.

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
