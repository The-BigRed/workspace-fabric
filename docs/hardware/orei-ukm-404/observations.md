# OREI UKM404 Observations

## Purpose

This document captures real-world observations, lab findings, deployment notes, and hardware-specific behavior for the OREI UKM404 USB matrix.

These notes inform the UKM404 driver, but they do not define the generic Workspace Fabric architecture.

Use this file as the hardware lab notebook. When an observation materially affects driver behavior, reflect the validated result in `driver.md` and, where appropriate, `protocol-notes.md`.

---

## Role in Reference Deployment

The OREI UKM404 is the initial reference USB matrix for Workspace Fabric.

The current deployment uses two UKM404 devices.

Potential USB resources include:

- Keyboard
- Mouse
- Camera
- Microphone
- Speakers
- Stream Deck
- YubiKey
- PiKVM HID endpoint
- Spare devices

---

## Multiple Matrix Support

Workspace Fabric must support multiple UKM404 instances.

Each instance must have its own:

- Driver configuration
- Host map
- Device map
- Capabilities
- Observed state

Observation status:
- Design requirement based on reference deployment.

---

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

Observation status:
- Required by intended deployment.

---

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

Observation status:
- Validated as an architectural requirement from the dual-UKM404 deployment model.

---

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

---

## Architectural Lesson

The UKM404 deployment directly informed the Workspace Fabric rule:

> Resource attachment is explicit. No global port symmetry is assumed.

This rule belongs to the Workspace Fabric core, not the UKM404 driver.

The UKM404 driver should respect this model but should not own the resource graph or transaction planning.

---

## Lab Notes

Use dated sections for new observations.

### YYYY-MM-DD

Observation:
- TBD

Hardware / Firmware:
- TBD

Impact:
- TBD

Driver implication:
- TBD

Status:
- Unverified / Confirmed / Superseded
