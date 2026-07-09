# OREI UKM404 Protocol Notes

## Purpose

This document is the engineering reference for communicating with the OREI UKM404 USB matrix.

It summarizes the vendor protocol in a format convenient for driver development. It should remain synchronized with the driver implementation.

The vendor manual remains the authoritative source.

---

## Source Material

- Vendor manual: `OREI_UKM404_User_Manual.pdf` or equivalent vendor documentation.
- Original project notes: migrated from `orei-ukm404.md`.
- Verified driver behavior: to be added as implementation proceeds.

---

## Hardware Interfaces

### USB / Local Control

Status:
- TBD

Notes:
- Confirm whether the UKM404 exposes a serial, HID, vendor utility, network, or other control interface.
- Document operating system requirements for the control interface if any exist.

### Serial / RS-232

Status:
- TBD

Connector:
- TBD

Serial Settings:
- TBD

Notes:
- Populate only if the UKM404 provides RS-232 or a serial-style command interface.

### Network / Telnet / TCP

Status:
- TBD

Default Port:
- TBD

Authentication:
- TBD

Notes:
- Populate only if the UKM404 provides network control.

---

## Command Categories

The command categories below are expected areas for investigation during driver implementation.

- Device-to-host routing
- Route query / status
- Port status
- Device connection status
- Host connection status
- USB mode / speed reporting
- System information
- Reset / recovery behavior

---

## Command Reference

To be populated from the vendor documentation and verified during implementation.

| Command | Purpose | Parameters | Response | Status |
|---------|---------|------------|----------|--------|
| TBD | Route USB device port to host port | TBD | TBD | Planned |
| TBD | Query route state | TBD | TBD | Planned |
| TBD | Query device/host status | TBD | TBD | Planned |
| TBD | Query firmware/system info | TBD | TBD | Planned |

---

## Response Formats

To be populated.

Document:

- Success response format
- Failure response format
- Route query response format
- Status response format
- Timeout behavior
- Unexpected or malformed response behavior

---

## Error Responses

To be populated.

Document:

- Invalid port
- Unsupported command
- Busy / unavailable device
- Communication timeout
- Transport unavailable
- Unknown or malformed response

---

## Driver Mapping

| Workspace Fabric Driver Method | Protocol Command | Status |
|--------------------------------|------------------|--------|
| Connect | TBD | Planned |
| Disconnect | TBD | Planned |
| Route USB device to host | TBD | Planned |
| Query route state | TBD | Planned |
| Query capabilities | TBD | Planned |
| Query firmware/system info | TBD | Planned |

---

## Capability Verification

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

These values are provisional and must be verified against vendor documentation and physical hardware.

---

## Unsupported Features

Document verified hardware limitations here.

Examples:

- Host emulation unsupported: TBD
- Device emulation unsupported: TBD
- Route query unsupported: TBD

---

## Firmware Notes

Document firmware-specific behavior here.

| Firmware Version | Behavior / Note | Verified Date |
|------------------|-----------------|---------------|
| TBD | TBD | TBD |

---

## Verification Status

| Feature | Status | Notes |
|---------|--------|-------|
| Connect | Planned | TBD |
| Device-to-host routing | Planned | TBD |
| Route query | Unknown | Verify whether supported |
| Multiple instances | Planned | Required by reference deployment |
| USB 3 support | Expected | Verify during implementation |
| Host emulation | Unknown | Verify during implementation |
| Device emulation | Unknown | Verify during implementation |
