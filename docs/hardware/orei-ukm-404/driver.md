# OREI UKM404 Driver

## Purpose

Provides Workspace Fabric support for the OREI UKM404 USB matrix.

This document describes the driver's public contract, capabilities, configuration, limitations, and implementation status.

Protocol-level details belong in `protocol-notes.md`. Real-world hardware observations belong in `observations.md`.

---

## Driver Status

Current Phase:
- Development

Current Milestone:
- Phase 3 hardware integration

Driver Version:
- Unreleased

---

## Supported Hardware

| Model | Status | Notes |
|-------|--------|-------|
| OREI UKM404 | Planned | Initial reference USB matrix |

Firmware Tested:
- TBD

---

## Transport

Current Transport:
- TBD

Future / Alternate Transport:
- TBD

Notes:
- Confirm the supported control interface from the vendor manual and physical testing.

---

## Supported Operations

| Operation | Status | Notes |
|-----------|--------|-------|
| Connect | Planned | Establish communication with one UKM404 instance |
| Disconnect | Planned | Cleanly close communication |
| Route USB device to host | Planned | Map one device-side port to one host-side port |
| Query route state | Unknown | Verify hardware support |
| Report capabilities | Planned | Report supported/unsupported/unknown capabilities |
| Support multiple instances | Planned | Required by reference deployment |
| Report structured errors/warnings | Planned | Required by driver contract |

---

## Capability Report

Initial expected capability report:

```yaml
capabilities:
  usb_routing: supported
  per_device_routing: supported
  route_query: unknown
  usb3: supported
  host_emulation: unknown
  device_emulation: unknown
```

These values are provisional. Update them as the vendor documentation and physical testing confirm actual behavior.

---

## Configuration

Example configuration shape:

```yaml
usb_matrices:
  ukm404_a:
    driver: orei-ukm404
    transport:
      type: TBD
      host: TBD
      port: TBD
    hosts:
      1: desktop
      2: work_laptop
      3: pikvm
      4: spare_laptop

  ukm404_b:
    driver: orei-ukm404
    transport:
      type: TBD
      host: TBD
      port: TBD
    hosts:
      1: desktop
      2: work_laptop
      3: controller
      4: rack_server

usb_devices:
  camera:
    matrix: ukm404_a
    device_port: 3

  speakers:
    matrix: ukm404_b
    device_port: 1
```

Configuration notes:

- Host maps are per matrix.
- Device ownership is explicit.
- Consistent host numbering across matrices is allowed but not required.
- A USB route is valid only when the selected device and host are attached to the same matrix instance.

---

## Driver Architecture

The UKM404 driver is responsible for one physical UKM404 instance.

It should:

- Maintain only instance-local configuration.
- Validate driver-specific port values.
- Apply assigned device-to-host route actions.
- Report capabilities and observed state.
- Return structured errors and warnings.

It should not:

- Assume global host numbering.
- Coordinate directly with other UKM404 instances.
- Interpret high-level workspace intent.
- Own the resource graph.
- Own transaction planning.

---

## Route Semantics

A UKM404 route maps a device-side USB port to a host-side USB port on the same physical matrix.

Example valid route:

```text
speakers -> controller

speakers belongs to ukm404_b.
controller is attached to ukm404_b.
Route is valid.
```

Example invalid route:

```text
camera -> controller

camera belongs to ukm404_a.
controller is not attached to ukm404_a.
Route is invalid.
```

The core planner should reject invalid cross-matrix routes before execution. The driver may still validate instance-local port values defensively.

---

## Known Limitations

- Route query support is unknown until verified.
- Host emulation support is unknown until verified.
- Device emulation support is unknown until verified.
- Cross-matrix USB routing is not supported by a single UKM404 driver instance.

---

## Testing Status

| Test | Status | Notes |
|------|--------|-------|
| Unit tests | Planned | Driver logic and validation |
| Mock transport tests | Planned | Command formatting and response parsing |
| Physical connection test | Planned | Confirm transport and handshake |
| Physical route test | Planned | Route device port to host port |
| Route query test | Unknown | Depends on hardware support |
| Multiple instance test | Planned | Validate two independent UKM404 configs |
| Invalid cross-matrix route test | Planned | Should fail in planner/config validation |

---

## Future Enhancements

- Add complete protocol command mapping after vendor manual extraction.
- Add firmware-specific notes after physical testing.
- Add recovery behavior for failed or partial route changes.
- Add observed-state reporting when supported by hardware.

---

## Change Log

### YYYY-MM-DD

- Initial driver documentation scaffold.
