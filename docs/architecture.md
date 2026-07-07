
# Workspace Fabric Architecture

## Purpose

This document describes the architectural structure of Workspace Fabric.

Workspace Fabric is a control plane that weaves independent workspace resources into a coherent, programmable operating environment.

Rather than describing hardware, this document describes the logical architecture responsible for translating user intent into coordinated actions across physical devices, software agents, and future workspace resources.

Implementation details, hardware behavior, and architectural rationale are documented elsewhere.

## Architectural Goals

Workspace Fabric is designed to:

- Abstract hardware behind logical concepts.
- Support physical and virtual resources equally.
- Remain API-first.
- Be deterministic and explainable.
- Be easy to integrate with external automation and AI systems.
- Allow new hardware to be added through modular drivers.
- Model user intent rather than hardware topology.
- Treat resources as first-class architectural objects.
- Support optional capabilities without reducing the platform to the lowest common denominator.
- Execute workspace changes as validated transactions.
- Allow physical and software resources to participate equally.
- Scale naturally from a single workspace to multiple independent fabrics.

Workspace Fabric is **not** an automation engine. It provides the control plane that automation systems consume.

## Layered Architecture

### Layer 1 – Physical Infrastructure

Examples:

- HDMI matrices
- USB matrices
- Audio routing hardware
- KVMs
- Servers
- Displays
- Keyboards
- Mice
- Speakers
- BMCs (iDRAC, iLO, XClarity, Redfish)
- Virtualization platforms

These represent the real resources being managed.

### Layer 2 – Drivers

Drivers communicate with individual devices using their native protocols.

Responsibilities:

- Translate native commands.
- Report capabilities.
- Report observed state.
- Execute toolkit actions.
- Hide vendor-specific implementations.

The core system should never communicate directly with hardware.

### Layer 3 – Core Resource Model

The core resource model defines the logical resources that describe a workspace. Users interact with resources rather than hardware, while drivers translate those resources into implementation-specific operations.

Examples include:

- Fabrics
- Hosts
- Displays
- Video Sources
- USB Devices
- Remote Consoles
- Workspaces
- Scenes
- Routes
- Capabilities

These logical resources are intentionally independent of hardware implementation.

Hardware-specific concepts such as ports, protocols, and command sets remain the responsibility of individual drivers.

This layer contains no vendor-specific logic.

### Layer 4 – Control Plane

The control plane contains the orchestration engine responsible for maintaining the resource graph, desired state, observed state, transaction planning, capability negotiation, driver coordination, and API presentation.

## Core Responsibilities

The Workspace Fabric core is responsible for:

- Maintaining the resource graph.
- Maintaining desired and observed state.
- Validating workspace requests.
- Negotiating capabilities.
- Planning transactions.
- Coordinating drivers.
- Recording transaction history.
- Explaining execution decisions.

The control plane is responsible for:

- Tracking observed state.
- Managing desired state.
- Reconciling differences.
- Selecting the best available path.
- Executing scenes.
- Coordinating multiple drivers.
- Exposing APIs.

The control plane should always be able to explain its decisions.

### Layer 5 – Interfaces

Workspace Fabric is API-first.

Interfaces may include:

- REST API
- CLI
- Web UI
- Tablet application
- Future SDKs

Every interface should use the same control plane.

### Layer 6 – Integrations

External systems consume Workspace Fabric through stable APIs.

Examples:

- OpenClaw
- Home Assistant
- Node-RED
- Stream Deck
- Voice assistants
- Monitoring systems

These systems provide automation or orchestration. Workspace Fabric provides deterministic execution.

## Topology vs Operational State

Workspace Fabric separates static configuration from dynamic behavior.

Static:

- Devices
- Endpoints
- Connections
- Capabilities

Dynamic:

- Routes
- State
- Scenes
- Toolkit actions
- Desired state

This separation allows the physical wiring to remain largely unchanged while operational behavior changes continuously.

## Guiding Principles

1. Intent over implementation.
2. API-first, UI-second.
3. Driver isolation.
4. Deterministic behavior.
5. Explainable decisions.
6. Modular expansion.
7. Automation-friendly without embedding automation.

## Future Directions

Future enhancements may include:

- Multiple independent fabrics.
- Multi-fabric federation.
- Local Console Virtualization.
- Operating system agents.
- Multi-user orchestration layers.
- Distributed control planes.
- High-availability controllers.
- Additional transport types.
- Rich tablet interfaces.
- Expanded toolkit actions.
- Additional hardware drivers.

These capabilities should extend the architecture without requiring changes to the core domain model.
