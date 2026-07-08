# Workspace Fabric

> **Software-defined workspace infrastructure for dynamically connecting
> physical and virtual resources.**

Workspace Fabric is an open-source, hardware-agnostic control plane for
dynamically reconfigurable workspaces. It abstracts the physical and virtual connectivity of a
modern workspace into a unified, software-controlled fabric.

Instead of thinking about HDMI inputs, USB ports, KVM buttons, or remote
console URLs, operators interact with logical workspaces, scenes, and
endpoints. Workspace Fabric determines the best available path to
satisfy that request.

## Project Status

**Phase 3 – Hardware Integration**

Workspace Fabric has completed its foundational architecture and control plane.
The project currently includes configuration loading, resource graph construction,
transaction planning and execution, mock hardware drivers, persistent mock state, and a
functional command-line interface.

The current focus is replacing the mock drivers with hardware drivers, beginning with the
OREI UHD-808 HDMI matrix and OREI UKM404 USB matrix.

Initial hardware targets include:

-   OREI UHD-808 8×8 HDMI Matrix
-   OREI UKM-404 USB Matrix

Future support is expected for:

-   Dell iDRAC
-   HPE iLO
-   Lenovo XClarity / IMM
-   Proxmox VE
-   Home Assistant
-   Additional HDMI, USB, audio, KVM, and management platforms

## Why Workspace Fabric?

Traditional KVMs switch a keyboard, video, and mouse between computers.

Workspace Fabric takes a broader view.

It models an entire workspace as a collection of interconnected
resources and provides a control plane capable of coordinating physical
switching, remote management interfaces, and software consoles through
one consistent API.

The goal is not simply to switch cables.

The goal is to make the underlying transport largely irrelevant.

## Core Principles

-   Connect everything once.
-   Route using logical names rather than physical ports.
-   Separate hardware-specific logic into modular drivers.
-   Prefer open standards and interoperable APIs.
-   Keep automation transparent and explainable.
-   Design for both humans and automation.

## Long-Term Vision

Workspace Fabric should eventually allow an operator---or another
automation platform---to request outcomes such as:

-   "Work on my desktop."
-   "Open Server 12."
-   "Switch to Presentation Mode."

The control plane determines how to satisfy that request, whether by:

-   Switching an HDMI matrix
-   Switching a USB matrix
-   Launching an iDRAC or iLO console
-   Opening SSH or RDP
-   Waking a system with Wake-on-LAN
-   Applying a predefined scene
-   Combining multiple actions into one workspace transition

## Project Philosophy

Workspace Fabric prioritizes reliability, transparency, and
interoperability over novelty.

Hardware should be abstracted, never hidden. Users should understand
what the system is doing, and automated actions should be explainable,
predictable, and reproducible.

Workspace Fabric separates intent from implementation: users request outcomes
(such as a workspace or scene), while drivers determine how those outcomes are achieved
on specific hardware.

## Repository Layout

``` text
docs/        Stable project documentation
design/      Engineering notes, ADRs, experiments
src/         Source code
tests/       Automated tests
examples/    Sample configurations
scripts/     Development utilities
ai/          AI prompts, conventions, and architecture guidance
```

## Current Focus

Near-term milestones:

1.  Validate communication with the OREI UHD-808.
2.  Validate communication with the OREI UKM-404.
3.  Develop the first modular device drivers.
4.  Validate physical routing on real hardware.
5.  Expose a REST API.
6.  Build a web interface.
7.  Integrate with external automation platforms.

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

The project is in its earliest stages. Suggestions, design discussions,
bug reports, and contributions are welcome as the architecture evolves.

## License

Licensed under the Apache License 2.0.
