# OREI UHD-808 Observations

## Purpose

This document is the field-observation and lab-notes companion for the OREI UHD-808 HDMI matrix.

Use this file to capture verified behavior, quirks, deployment notes, and lessons learned while testing or using the device with Workspace Fabric.

Codex may read this file when implementing the driver, but changes to driver behavior should be reflected in `protocol-notes.md` when they become part of the stable driver contract.

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

Driver implication:

- The UHD-808 driver should report HPD/source-disable behavior as unsupported unless a verified hardware command exists.
- Operating-system display enable/disable behavior should be handled by a separate host-side display agent.

## EDID Management Observations

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

## Scaling and Upscaling Observations

The UHD-808 includes scaling/upscaling functionality.

Driver implications:

- Expose scaling as an optional capability.
- Treat scaling as associated with route/output behavior, not as a special display type.
- Support `prefer` and `require` policies from the capability model.

## Fast Switching Observations

The UHD-808 supports fast switching.

Driver implications:

- Expose fast switching as an optional capability.
- Do not assume fast switching exists in all video matrix drivers.
- Allow workspace definitions to prefer or require fast switching.

## Relationship to Windows Display Agent

Because the UHD-808 maintains active upstream links, a separate Windows Display Agent may be needed to enable or disable displays at the operating system level.

The UHD-808 driver and Windows Display Agent should remain separate drivers coordinated by the Workspace Fabric transaction engine.

## Non-Goals for UHD-808 Driver

The UHD-808 driver should not:

- Manage Windows display settings directly.
- Pretend to disable upstream displays if the hardware cannot do so.
- Assume all HDMI matrices have the same capabilities.
- Encode user-facing workspace logic.

## Lab Validation Log

Use this section as a running log for physical testing.

### YYYY-MM-DD - Test title

Setup:

- TODO

Action:

- TODO

Observed result:

- TODO

Driver decision:

- TODO

Follow-up:

- TODO

## Open Questions

Track unresolved hardware behavior here until it is confirmed.

| Question | Status | Notes |
|---|---:|---|
| Does Telnet use the exact same command set as RS232? | unverified | Confirm from manual and physical test. |
| Can current routing state be queried? | unverified | Needed for route reconciliation. |
| Can saved EDID profiles be applied, or only cloned? | unverified | Impacts capability report. |
| Are CEC commands exposed through the control protocol? | unverified | Keep separate from routing. |
| Can HPD behavior be controlled by command? | expected unsupported | Current observation suggests active links are maintained. |
