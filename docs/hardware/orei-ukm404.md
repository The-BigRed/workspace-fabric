# OREI UKM404 Hardware Notes

## Purpose

This document captures hardware-specific observations and driver requirements for the OREI UKM404 USB matrix.

These notes inform the UKM404 driver but should not define the generic Workspace Fabric architecture.

## Role in Reference Deployment

The OREI UKM404 is the initial reference USB matrix for Workspace Fabric.

The current deployment uses two UKM404 devices.

Potential USB resources include:

- Keyboard.
- Mouse.
- Camera.
- Microphone.
- Speakers.
- Stream Deck.
- YubiKey.
- PiKVM HID endpoint.
- Spare devices.

## Multiple Matrix Support

Workspace Fabric must support multiple UKM404 instances.

Each instance must have its own:

- Driver configuration.
- Host map.
- Device map.
- Capabilities.
- Observed state.

## Per-Matrix Host Maps

Host mappings are per matrix.

Example:

```yaml
usb_matrices:
  ukm404_a:
    hosts:
      1: desktop
      2: work_laptop
      3: pikvm
      4: spare_laptop

  ukm404_b:
    hosts:
      1: desktop
      2: work_laptop
      3: controller
      4: rack_server
```

Maintaining consistent host numbering across matrices may be a deployment best practice, but it is not an architectural requirement.

## USB Device Ownership

Each USB device belongs to exactly one USB matrix.

Example:

```yaml
usb_devices:
  camera:
    matrix: ukm404_a
    device_port: 3

  speakers:
    matrix: ukm404_b
    device_port: 1
```

A USB route is valid only if the matrix that owns the USB device has the requested host attached.

## Validation Example

Valid:

```text
speakers -> controller

speakers belongs to ukm404_b.
controller is attached to ukm404_b.
Route is valid.
```

Invalid:

```text
camera -> controller

camera belongs to ukm404_a.
controller is not attached to ukm404_a.
Route is invalid.
```

## Candidate Capability Report

Initial expected capabilities:

```yaml
capabilities:
  usb_routing: supported
  per_device_routing: supported
  route_query: unknown
  usb3: supported
  host_emulation: unknown
  device_emulation: unknown
```

These values should be verified during driver implementation.

## Driver Requirements

The UKM404 driver should eventually support:

- Connect to the matrix.
- Route USB device port to host port.
- Query route state if supported.
- Report capabilities.
- Support multiple instances.
- Return structured errors and warnings.

## Non-Goals

The UKM404 driver should not:

- Assume global host numbering.
- Coordinate directly with other UKM404 instances.
- Interpret high-level workspace intent.
- Own the resource graph.
- Own transaction planning.

## Architectural Lesson

The UKM404 deployment directly informed the rule:

> Resource attachment is explicit. No global port symmetry is assumed.

This rule belongs to the Workspace Fabric core, not the UKM404 driver.
