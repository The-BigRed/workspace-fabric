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
- Phase 3.3 OREI UKM-404 USB Driver

Driver Version:
- Unreleased

---

## Supported Hardware

| Model | Status | Notes |
|-------|--------|-------|
| OREI UKM404 | Implemented, physical validation pending | Initial reference USB matrix |

Firmware Tested:
- TBD

---

## Transport

Current Transport:
- Configurable command transport implemented for `telnet`, `tcp`, and `serial`.

Future / Alternate Transport:
- Physical validation may refine line-ending and response-framing behavior.

Notes:
- `telnet` defaults to port `23`.
- `tcp` defaults to port `8000`.
- `serial` defaults to baud rate `115200`.
- The manual does not document command line endings; the implementation defaults to CRLF and
  allows `line_ending` to be configured.
- RS-232 support requires `pyserial`.

---

## Supported Operations

| Operation | Status | Notes |
|-----------|--------|-------|
| Connect | Implemented, physical validation pending | Establish communication with one UKM404 instance |
| Disconnect | Implemented, physical validation pending | Cleanly close communication |
| Route USB device to host | Implemented with mocked transport | Maps one device-side port to one host-side port |
| Query route state | Implemented with mocked transport | Uses documented per-device query command |
| Report capabilities | Implemented | Report supported/unsupported/unknown capabilities |
| Support multiple instances | Planned | Required by reference deployment |
| Report structured errors/warnings | Implemented | Required by driver contract |

---

## Capability Report

Initial expected capability report:

```yaml
capabilities:
  usb_routing: supported
  per_device_routing: supported
  route_query: supported
  usb3: supported
  host_emulation: unknown
  device_emulation: unknown
```

These values are based on the vendor manual and mocked transport tests. Physical hardware testing
must still confirm route query and transport behavior.

---

## Configuration

Example configuration shape:

```yaml
drivers:
  ukm404_a:
    type: orei_ukm404
    fabric: local_workspace
    connection:
      transport: telnet
      host: 172.24.3.193
      port: 23
      timeout_seconds: 2

  ukm404_serial:
    type: orei_ukm404
    fabric: local_workspace
    connection:
      transport: serial
      port: COM3
      baud_rate: 115200
      timeout_seconds: 2

  ukm404_b:
    type: orei_ukm404
    fabric: local_workspace
    connection:
      transport: telnet
      host: 172.24.3.194
      port: 23
      timeout_seconds: 2

usb_matrices:
  ukm404_a:
    driver: ukm404_a
    hosts:
      1: desktop
      2: work_laptop
      3: pikvm
      4: spare_laptop

  ukm404_b:
    driver: ukm404_b
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
- The orchestration layer resolves logical USB device and host IDs to `device_port` and
  `host_port` before invoking the driver.
- The driver consumes device-local ports and does not depend on environment-specific resource
  names.

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

The driver maps Workspace Fabric `usb_route` actions containing `device_port` and `host_port` to
UKM-404 route commands:

```text
set device x in host y
```

It queries route state with:

```text
get device x in host
```

The driver reports device-local port routes in observed state. The orchestration layer may
correlate those ports back to user-facing resources when it has the resource graph context.

---

## Known Limitations

- Route query support is documented and implemented, but still needs physical validation.
- Host emulation support is unknown until verified.
- Device emulation support is unknown until verified.
- Cross-matrix USB routing is not supported by a single UKM404 driver instance.
- TCP/Telnet command framing and serial line-ending behavior still require hardware validation.

---

## Testing Status

| Test | Status | Notes |
|------|--------|-------|
| Unit tests | Implemented | Driver logic and validation |
| Mock transport tests | Implemented | Command formatting and response parsing |
| Physical connection test | Planned | Confirm transport and handshake |
| Physical route test | Planned | Route device port to host port |
| Route query test | Implemented with mocked transport | Physical validation pending |
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

### 2026-07-09

- Implemented Milestone 3.3 driver routing/query behavior with mocked transport tests.
- Added configurable TCP, Telnet, and RS-232 command transports.
