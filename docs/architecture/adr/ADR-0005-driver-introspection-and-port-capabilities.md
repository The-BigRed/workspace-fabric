# ADR-0005: Driver Introspection and Port Capabilities

## Status
Proposed

## Context
Different controllers expose different port types, counts, and capabilities. For example, an HDMI matrix exposes video inputs and outputs, while a USB matrix exposes host-side and device-side USB ports. A future configuration UI should not need hard-coded logic for every supported device model.

Where possible, drivers should teach the system how they can be configured.

## Decision
Drivers should eventually expose machine-readable metadata describing controller capabilities, including port groups, port counts, directionality, accepted resource types, and optional hardware-discovered properties.

Example concept:

```yaml
ports:
  inputs:
    count: 8
    direction: sink
    accepts:
      - video_source

  outputs:
    count: 8
    direction: source
    accepts:
      - video_sink
```

For USB:

```yaml
ports:
  hosts:
    count: 4
    accepts:
      - usb_host

  devices:
    count: 4
    accepts:
      - keyboard
      - mouse
      - camera
      - microphone
      - hid
```

## Rationale
Driver introspection allows the configuration UI to be generic. Adding a new driver should not require rewriting the configuration application. The driver should expose what the UI needs in order to present valid configuration choices.

This also creates a path for connectivity verification, hardware discovery, validation, and safer scene execution.

## Consequences
- This is a future enhancement and does not need to block current physical driver work.
- Drivers should be designed so that capability metadata can be added later without major rewrites.
- Static capability definitions are acceptable before full hardware query support exists.
- Runtime-discovered information should override or enrich static capability definitions when available.
