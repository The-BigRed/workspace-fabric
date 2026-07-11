# Workspace Fabric v0.3.0

## Summary

Workspace Fabric `v0.3.0` is the first physically validated release.

It closes Phase 3 by proving that the control-plane, resource graph,
transaction planner, executor, controller boundary, and driver contract can
apply complete logical workspaces through real HDMI and USB matrix hardware.

## Highlights

- Physical OREI UHD-808 video routing
- Physical OREI UKM404 USB routing
- Route-state query and observed-state reporting
- Physical lab configuration
- Desktop, work, and hybrid-meeting smoke tests
- Dry-run transaction preview
- Structured connection, timeout, rejection, state-query, and partial-success
  reporting
- Safety and recovery guidance

## Architectural Significance

This release establishes the working baseline before Phase 4 separates driver
implementations into independently installable and versioned packages.

The v0.3.0 release does not claim that drivers are already external plugins. It
captures the last verified state before that packaging and discovery refactor.

## Current Supported Reference Hardware

- OREI UHD-808 HDMI matrix
- OREI UKM404 USB matrix

Support reflects the operations physically validated during Phase 3. Additional
capabilities such as EDID, scaler, CEC, ARC, Windows display management, and
PiKVM integration remain future work.

## Known Limitations

- Driver implementations may still be packaged with or registered by the core
  in this baseline.
- No production REST API or graphical application exists yet.
- YAML remains the primary configuration mechanism.
- Driver installation, upgrade, rollback, and removal are not yet independent.
- Advanced UHD-808 capabilities remain incomplete.

## Next Phase

Phase 4 creates the modular driver platform:

- Independent core, Driver API, and driver packages
- Entry-point discovery
- Driver compatibility validation
- Independent semantic versioning
- Install, upgrade, rollback, removal, and missing-driver behavior
- Physical regression testing after migration
