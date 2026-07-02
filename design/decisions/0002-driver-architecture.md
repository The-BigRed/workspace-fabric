# ADR 0002: Use a modular driver architecture

## Status

Accepted

## Context

Workspace Fabric is intended to control and coordinate many kinds of devices and connection paths. The initial hardware includes an OREI UHD-808 HDMI matrix and OREI UKM-404 USB matrices, but the longer-term vision includes BMCs, IP KVMs, remote consoles, audio routing, virtualization platforms, and automation systems.

If the project is built around one specific device type, such as an HDMI matrix, it will become difficult to extend without rewriting major parts of the system.

## Decision

Workspace Fabric will use a modular driver architecture.

Each supported device or platform will be represented by a driver module. Drivers are responsible for speaking the native protocol of the device or service they support. The rest of the system should interact with drivers through stable internal interfaces rather than vendor-specific commands.

Examples include:

- OREI UHD-808 HDMI matrix driver
- OREI UKM-404 USB matrix driver
- Dell iDRAC driver
- HPE iLO driver
- Lenovo XClarity or IMM driver
- Proxmox API driver
- Home Assistant API driver

## Rationale

This keeps the core fabric model independent from any single vendor, protocol, or hardware category. HDMI switching, USB switching, BMC console access, IP KVM access, and remote console launchers can all become capabilities exposed by drivers.

This supports the larger goal of Workspace Fabric: providing a unified workspace experience without requiring the user to think in terms of individual cables, ports, or vendor-specific control methods.

## Consequences

The first implementation should avoid hard-coding OREI-specific behavior into the core control plane.

Device-specific commands belong in driver modules. Higher-level concepts such as endpoints, routes, scenes, capabilities, and workspaces belong in the core model.

This may require a little more structure early in the project, but it should reduce future rewrites as new hardware and integrations are added.
