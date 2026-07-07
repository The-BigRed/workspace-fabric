# OREI UHD-808 Hardware Notes

## Purpose

This document captures hardware-specific observations and driver requirements for the OREI UHD-808 HDMI matrix.

These notes inform the UHD-808 driver but should not define the generic Workspace Fabric architecture.

## Role in Reference Deployment

The OREI UHD-808 is the initial reference video matrix for Workspace Fabric.

It provides video routing between multiple source devices and displays.

Initial source devices may include:

- Personal desktop.
- Work laptop.
- PiKVM.
- Future auxiliary systems.

Initial destinations may include:

- Primary 4K display.
- Secondary 2K display.
- PiKVM capture input.
- Future outputs.

## Observed Behavior: Active HDMI Link

The UHD-808 maintains an active HDMI link to upstream source devices even when a source is not currently routed to a visible display.

Impact:

- Source systems may continue to believe displays are connected.
- Windows may not automatically disable displays that are no longer visible to the user.
- Switching can be fast because links remain active.
- Workspace Fabric may need an optional Windows Display Agent for OS-level display management.

This behavior is not inherently wrong. It may be beneficial in some deployments and undesirable in others.

## EDID Management

The UHD-808 can clone EDID from a destination display.

Observed behavior:

- EDID can be cloned.
- EDID does not automatically follow routing changes.
- EDID management should be exposed as an explicit driver capability.

Driver implications:

- Expose EDID clone if supported.
- Expose EDID profile apply if supported.
- Do not make EDID management part of basic route behavior.
- Allow scenes to request EDID behavior through capability policies.

## Scaling and Upscaling

The UHD-808 includes scaling/upscaling functionality.

Driver implications:

- Expose scaling as an optional capability.
- Treat scaling as associated with route/output behavior, not as a special display type.
- Support `prefer` and `require` policies from the capability model.

## Fast Switching

The UHD-808 supports fast switching.

Driver implications:

- Expose fast switching as an optional capability.
- Do not assume fast switching exists in all video matrix drivers.
- Allow workspace definitions to prefer or require fast switching.

## Candidate Capability Report

Initial expected capabilities:

```yaml
capabilities:
  video_routing: supported
  route_query: unknown
  edid_clone: supported
  edid_profile_apply: unknown
  scaler: supported
  upscale: supported
  fast_switching: supported
  hpd_control: unsupported
  cec: unknown
  audio_routing: unknown
```

These values should be verified during driver implementation.

## Driver Requirements

The UHD-808 driver should eventually support:

- Connect to the matrix.
- Route input to output.
- Query routing state if supported.
- Clone EDID from output if supported.
- Apply EDID profile if supported.
- Configure scaler/upscale mode if supported.
- Configure fast switching if supported.
- Report unsupported HPD/source-disable behavior.
- Return structured errors and warnings.

## Non-Goals

The UHD-808 driver should not:

- Manage Windows display settings directly.
- Pretend to disable upstream displays if the hardware cannot do so.
- Assume all HDMI matrices have the same capabilities.
- Encode user-facing workspace logic.

## Relationship to Windows Display Agent

Because the UHD-808 maintains active upstream links, a separate Windows Display Agent may be needed to enable or disable displays at the operating system level.

The UHD-808 driver and Windows Display Agent should remain separate drivers coordinated by the Workspace Fabric transaction engine.
