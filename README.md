# Workspace Fabric

> **Software-defined workspace infrastructure for dynamically connecting
> physical and virtual resources.**

Workspace Fabric is an open-source platform that abstracts the wiring of
a modern workspace into a unified, software-controlled fabric.

Instead of thinking about HDMI inputs, USB ports, KVM buttons, or remote
console URLs, operators interact with logical workspaces, scenes, and
endpoints. Workspace Fabric determines the best available path to
satisfy that request.

## Project Status

**Early development**

The project is currently focused on building the core architecture and
the first hardware drivers.

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
4.  Build the core fabric model.
5.  Expose a REST API.
6.  Build a web interface.
7.  Integrate with external automation platforms.

## Contributing

The project is in its earliest stages. Suggestions, design discussions,
bug reports, and contributions are welcome as the architecture evolves.

## License

Licensed under the Apache License 2.0.
