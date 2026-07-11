# Phase 6: Functional and Driver Expansion

## Status

Planned

## Purpose

Expand Workspace Fabric after the modular driver platform and user-facing
product are stable.

Phase 6 is ongoing platform growth rather than a prerequisite for declaring the
core product complete.

## Expansion Categories

### Existing Driver Capabilities

Potential UHD-808 work:

- EDID clone and assignment
- EDID data query
- Scaler control
- Output stream control
- CEC
- ARC
- Additional identity and firmware reporting

Potential UKM404 work:

- Additional discovered capabilities
- Richer identity and diagnostics
- Firmware-specific behavior
- Features exposed through real product use

### Operating-System Agents

- Windows Display Agent
- Linux display or endpoint agents
- macOS display or endpoint agents
- Approved local resource exposure

### Remote Console

- PiKVM
- Enterprise IP-KVM
- iDRAC
- iLO
- XClarity / IMM
- Generic Redfish where appropriate

### Additional Routing Hardware

- HDMI and DisplayPort matrices
- USB matrices
- Audio matrices and DSPs
- Broadcast and professional AV routing
- Capture and presentation devices

### Platform and Service Drivers

- Hypervisors
- Remote desktop/session providers
- Power and wake integrations
- Monitoring and health providers
- Other workspace-related services

## Driver Packs

Driver packs may provide convenient installation groups, such as vendor packs
or use-case packs. A pack is a metapackage only. Individual drivers retain their
own versions and may be installed, upgraded, rolled back, or removed
independently.

## Core Extension Rules

A driver should use the existing Driver API whenever possible.

When a real integration exposes a missing general capability:

1. Confirm the capability is broadly meaningful and not vendor-specific.
2. Update or add an ADR when the model changes.
3. Extend the Driver API backward-compatibly where practical.
4. Release the core or Driver API according to semantic versioning.
5. Keep older compatible drivers operational where practical.

Do not add vendor-specific commands, configuration fields, or state shapes to
the core merely to accelerate one driver.

## Release Model

- Driver-only fix: driver patch release.
- Driver-only compatible feature: driver minor release.
- Backward-compatible core or Driver API feature: relevant minor release.
- Breaking public or Driver API change: relevant major release.
- Driver pack dependency update: driver-pack release only.

## Completion

Phase 6 has no fixed final completion requirement. It is the continuing
expansion phase after the first complete product release. Individual drivers,
capabilities, and integration groups should define their own milestones and
acceptance criteria.
