# Workspace Fabric

> **Software-defined workspace infrastructure for dynamically connecting
> physical and virtual resources.**

Workspace Fabric is an open-source, hardware-agnostic control plane for
dynamically reconfigurable workspaces. It abstracts the physical and virtual
connectivity of a modern workspace into a unified, software-controlled fabric.

Instead of thinking about HDMI inputs, USB ports, KVM buttons, or remote
console URLs, operators interact with logical resources, workspaces, scenes,
and patches. Workspace Fabric determines how to satisfy that intent using the
available controllers, drivers, and physical topology.

## Project Status

**Phase 3 – Hardware Integration**

Workspace Fabric has completed its foundational architecture and control plane.
The project currently includes configuration loading, resource graph
construction, transaction planning and execution, mock hardware drivers,
persistent mock state, and a functional command-line interface.

The current focus is replacing mock drivers with hardware drivers, beginning
with the OREI UHD-808 HDMI matrix and OREI UKM404 USB matrix, then validating
complete routing against the physical lab.

Initial hardware targets include:

- OREI UHD-808 8×8 HDMI Matrix
- OREI UKM404 USB Matrix
- Windows Display Agent
- PiKVM

Future support is expected for:

- Dell iDRAC
- HPE iLO
- Lenovo XClarity / IMM
- Proxmox VE
- Home Assistant
- Additional HDMI, USB, audio, KVM, and management platforms

## Why Workspace Fabric?

Traditional KVMs switch a keyboard, video, and mouse between computers.

Workspace Fabric takes a broader view.

It models an entire workspace as a collection of interconnected resources and
provides a control plane capable of coordinating physical switching, remote
management interfaces, and software consoles through one consistent API.

The goal is not simply to switch cables.

The goal is to connect everything once and make the underlying transport
largely irrelevant to the operator.

## Core Principles

- Connect everything once.
- Route using logical names rather than physical ports.
- Model physical reality explicitly.
- Separate hardware-specific logic into modular drivers.
- Prefer open standards and interoperable APIs.
- Keep automation transparent and explainable.
- Design for both humans and automation.
- Preserve YAML as an open, inspectable configuration representation without
  requiring operators to author it manually.

## Configuration Model

Workspace Fabric uses the following conceptual hierarchy:

```text
Driver
  ↓
Controller
  ↓
Resource
  ↓
Workspace
  ↓
Scene
  ↓
Patch
```

- **Drivers** implement hardware- or service-specific behavior.
- **Controllers** are configured instances of drivers that communicate with
  specific devices or services.
- **Resources** represent physical devices, logical objects, and routable
  endpoints.
- **Workspaces** describe reusable operating environments.
- **Scenes** compose one or more workspaces into a complete requested
  configuration.
- **Patches** apply focused changes to the current state without redefining or
  reapplying an entire workspace or scene.

The preferred long-term configuration experience is interactive. Drivers expose
their configuration requirements, ports, and capabilities; users then describe
what is physically connected. YAML remains the serialized source of truth and
an advanced editing mechanism.

Architecture decisions and rationale are documented in
`docs/architecture/adr/`.

## Long-Term Vision

Workspace Fabric should eventually allow an operator—or another automation
platform—to request outcomes such as:

- "Work on my desktop."
- "Open Server 12."
- "Switch to Presentation Mode."
- "Add the Stream Deck to the current workspace."
- "Move the secondary keyboard and mouse without changing anything else."

The control plane determines how to satisfy that request, whether by:

- Switching an HDMI matrix
- Switching a USB matrix
- Launching an iDRAC or iLO console
- Opening SSH or RDP
- Waking a system with Wake-on-LAN
- Applying a predefined scene
- Applying a targeted patch
- Combining multiple workspaces into one coordinated state

## Project Philosophy

Workspace Fabric prioritizes reliability, transparency, and interoperability
over novelty.

Hardware should be abstracted, never hidden. Users should understand what the
system is doing, and automated actions should be explainable, predictable, and
reproducible.

Workspace Fabric separates intent from implementation. Users request outcomes,
while the control plane plans the change and drivers determine how assigned
actions are performed on specific hardware.

Workspace Fabric is not an automation engine. External automation systems may
decide when to request a workspace, scene, or patch; Workspace Fabric provides
deterministic validation and execution.

## Repository Layout

```text
docs/        Stable project documentation and architecture decisions
design/      Engineering notes and experiments
src/         Source code
tests/       Automated tests
examples/    Sample configurations and test fixtures
scripts/     Development utilities
ai/          AI prompts, conventions, and architecture guidance
```

## Current Focus

Near-term milestones:

1. Harden the driver contract.
2. Validate the physical lab configuration.
3. Develop the OREI UHD-808 driver.
4. Develop the OREI UKM404 driver.
5. Develop the Windows Display Agent.
6. Integrate PiKVM.
7. Validate end-to-end routing on real hardware.
8. Add safety, recovery, and clear failure handling.

## Current Capabilities

- Declarative YAML configuration
- Resource graph construction
- Capability validation
- Transaction planning
- Transaction execution
- Workspace transaction history
- Mock video and USB matrix drivers
- Persistent mock driver state
- Workspace-oriented CLI

## Current Limitations

The following are not yet implemented:

- Physical hardware drivers
- Driver-assisted controller discovery
- Interactive configuration authoring
- REST API
- Web UI
- Desktop application
- Tablet interface
- Multi-fabric orchestration

## Operator Smoke Test

```powershell
.\.venv\Scripts\Activate.ps1

workspace-fabric config validate
workspace-fabric workspace list
workspace-fabric apply hybrid_meeting --dry-run
workspace-fabric apply hybrid_meeting
workspace-fabric state
```

Expected results:

- Configuration validates successfully.
- Available workspaces are listed.
- Dry-run produces a transaction plan.
- Apply executes mock driver actions.
- State reflects the applied workspace and records the transaction.

## Contributing

The project is in its earliest stages. Suggestions, design discussions, bug
reports, and contributions are welcome as the architecture evolves.

Architectural changes should be captured in an Architecture Decision Record and
reflected in the stable documentation before implementation diverges from the
accepted model.

## License

Licensed under the Apache License 2.0.
