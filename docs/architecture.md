# Workspace Fabric Architecture

## Purpose

This document describes the architectural structure of Workspace Fabric.

**Workspace Fabric is a hardware-agnostic control plane for dynamically
reconfigurable workspaces.**

It weaves independent workspace resources into a coherent, programmable
operating environment.

Rather than describing one hardware platform, this document describes the
logical architecture responsible for translating user intent into coordinated
actions across physical devices, software agents, and future workspace
resources.

Implementation details, hardware behavior, and architectural rationale are
documented elsewhere. Accepted rationale for the configuration model is
recorded under `docs/architecture/adr/`.

## Architectural Goals

Workspace Fabric is designed to:

- Abstract hardware behind logical concepts.
- Support physical and virtual resources equally.
- Remain API-first.
- Be deterministic and explainable.
- Be easy to integrate with external automation and AI systems.
- Allow new hardware to be added through modular drivers.
- Model user intent without hiding physical topology.
- Treat controllers, resources, capabilities, transactions, and configuration
  as first-class architectural objects.
- Support optional capabilities without reducing the platform to the lowest
  common denominator.
- Execute changes as validated transactions.
- Scale naturally from a single personal workspace to multiple independent
  fabrics.
- Preserve an open, inspectable configuration representation.
- Support an interactive configuration experience driven by driver metadata.

Workspace Fabric is **not** an automation engine. It provides the deterministic
control plane that automation systems consume.

## Layered Architecture

Workspace Fabric follows a layered architecture that separates user intent,
orchestration, hardware abstraction, and physical resources.

```text
                       Clients
           CLI • API • Web UI • Automation
                          │
                          ▼
               +----------------------+
               |   Workspace Fabric   |
               |    Control Plane     |
               +----------------------+
                          │
          +---------------+---------------+
          │                               │
          ▼                               ▼
     Configuration                 Resource Graph
          │                               │
          └───────────────┬───────────────┘
                          ▼
                 Transaction Planner
                Transaction Executor
            Desired & Observed State
                          │
                          ▼
                 Controller Instances
                          │
                          ▼
                   Driver Abstraction
                          │
        +-----------------+-----------------+
        │                 │                 │
        ▼                 ▼                 ▼
   Video Drivers     USB Drivers     Other Drivers
        │                 │                 │
        +-----------------+-----------------+
                          │
                          ▼
                 Physical Infrastructure
```

The architecture intentionally flows in one direction.

Clients express intent. The control plane validates that intent and produces a
transaction plan. Controller instances bind configuration to driver
implementations. Drivers translate assigned actions into vendor-specific
operations. Physical hardware or services perform the requested actions.

Drivers do not coordinate with one another and do not make global policy
decisions.

## Architectural Layers

### Layer 1 – Physical Infrastructure

Examples include:

- HDMI matrices
- USB matrices
- Audio routing hardware
- KVMs
- Servers
- Displays
- Keyboards
- Mice
- Cameras
- Microphones
- Speakers
- BMCs such as iDRAC, iLO, XClarity, and Redfish implementations
- Virtualization platforms
- Operating-system agents

These are the real devices and services being managed.

### Layer 2 – Driver Abstraction

Drivers implement hardware- or service-specific behavior.

Responsibilities include:

- Declaring configuration requirements.
- Translating native commands and responses.
- Reporting capabilities.
- Reporting observed state.
- Describing known ports and endpoint types.
- Validating driver-specific actions.
- Applying assigned actions.
- Returning structured errors, warnings, and unsupported-state results.
- Hiding vendor-specific protocol details from the core.

A driver is code. It is not a configured physical device.

The core system never communicates directly with hardware.

### Layer 3 – Controller Instances

A controller is a configured instance of a driver.

A controller binds:

- A stable instance identifier.
- A driver type.
- Connectivity and authentication settings.
- Instance-specific capability results.
- Discovered or declared hardware identity.
- Ports, endpoints, and observed state associated with that device.

Multiple controllers may use the same driver. For example, two OREI UKM404
devices use the same driver implementation but have separate addresses,
identity, state, and physical connections.

Controllers are the boundary between reusable driver code and a specific
reachable device, agent, or service.

### Layer 4 – Control Plane

The control plane contains the orchestration engine.

Its responsibilities include:

- Loading and validating configuration.
- Maintaining the resource graph.
- Maintaining desired and observed state.
- Validating workspace, scene, and patch requests.
- Negotiating capabilities.
- Planning transactions.
- Coordinating controller actions.
- Recording transaction history.
- Reconciling state where supported.
- Explaining execution decisions.

The control plane owns policy and coordination. Drivers own implementation of
assigned operations.

### Layer 5 – Configuration and Resource Model

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

The arrows describe how later concepts build on earlier ones. They are not
necessarily ownership relationships in every serialized configuration.

#### Drivers

Drivers are reusable code modules that implement communication and behavior for
a hardware family, software agent, or service.

#### Controllers

Controllers configure individual driver instances and represent reachable
devices or services.

#### Resources

Resources represent the things users and the planner reason about.

Examples include:

- Hosts
- Video sources
- Displays and capture sinks
- USB host endpoints
- Keyboards
- Mice
- Cameras
- Microphones
- Remote consoles
- Logical or composite endpoints

Resources may represent whole devices or individual endpoints. Physical
connections associate resources with controller ports and describe the actual
installed topology.

#### Workspaces

A workspace describes a reusable operating environment.

It identifies the resources and routes needed for one coherent working context,
such as:

- A desktop on the primary monitor with the primary keyboard and mouse.
- A work laptop on both monitors with the webcam and microphone.
- A PiKVM capture path for a selected video source.

A workspace may use only a subset of available resources. It does not need to
describe the entire fabric.

#### Scenes

A scene composes one or more workspaces into one complete requested
configuration.

A personal installation may commonly use scenes containing a single workspace.
Larger environments may use scenes to coordinate multiple simultaneous
workspaces, operators, rooms, capture paths, or presentation roles.

Consumers may activate a scene without needing to know whether it contains one
workspace or many.

#### Patches

A patch performs a focused partial change against the current fabric state.

Examples include:

- Moving only a keyboard and mouse.
- Adding a Stream Deck to whichever workspace is currently active.
- Moving a webcam without changing video routing.
- Adding a diagnostic or PiKVM capture route.
- Temporarily mirroring an output.

Patches leave unrelated state unchanged. They are not incomplete workspaces or
small scenes; their partial-update semantics are intentional.

### Layer 6 – Interfaces

Workspace Fabric is API-first.

Interfaces may include:

- REST API
- CLI
- Web UI
- Desktop application
- Tablet application
- Future SDKs

Every interface uses the same control plane and domain model.

### Layer 7 – Integrations

External systems consume Workspace Fabric through stable APIs.

Examples include:

- Home Assistant
- Node-RED
- Stream Deck
- Voice assistants
- Monitoring systems
- AI or agent platforms

These systems may decide when a change should occur. Workspace Fabric validates,
plans, and executes the requested workspace, scene, or patch.

## Physical Topology and Resource Attachment

Workspace Fabric must preserve a truthful model of physical connectivity.

Drivers and controllers expose or declare ports. Resources are mapped to those
ports to represent what is physically connected.

For example:

```text
Desktop Display Output 1
          │
          ▼
UHD-808 Input 1
          │
          ▼
UHD-808 Output 1
          │
          ▼
Primary Display
```

The core reasons about logical resources, but it must not erase the underlying
topology needed for validation, planning, diagnostics, and explainability.

Resource attachment is explicit. The system must not assume that all matrices
have symmetrical ports, that multiple devices share identical host maps, or
that all drivers can query their current state.

## Configuration Authoring

The preferred Workspace Fabric configuration experience is interactive.

The intended workflow is:

1. Select a driver representing the device or service being added.
2. Enter the connectivity and authentication details required by that driver.
3. Create a controller instance.
4. Validate connectivity.
5. Query identity, ports, capabilities, and observed state where supported.
6. Create resources and map them to controller ports according to physical
   reality.
7. Compose resources into workspaces.
8. Compose one or more workspaces into scenes where useful.
9. Create patches for reusable partial changes.
10. Validate and serialize the resulting configuration.

Drivers should expose machine-readable metadata sufficient for a generic
configuration application to render appropriate forms and endpoints without
embedding device-specific UI logic.

Relevant metadata may include:

- Required and optional connection fields.
- Supported transports.
- Authentication requirements.
- Port groups and port counts.
- Endpoint direction.
- Media or resource types accepted by each port.
- Optional capabilities.
- Whether identity, topology, routes, or state can be queried.

Hardware discovery is opportunistic. When a device cannot report a value, the
configuration may supply it explicitly and the observed result must remain
`unknown` rather than being fabricated.

## YAML as Serialization

YAML is the initial configuration format and remains an exposed, editable source
of truth.

This is valuable because it provides:

- Transparency.
- Version control.
- Portability.
- Human inspection.
- Advanced customization.
- A recovery path when a UI does not yet support a feature.

However, manually maintaining a large, internally congruent topology is
error-prone. YAML is therefore not intended to be the final primary
configuration-authoring experience.

The object model must drive the YAML schema. The project must not constrain the
architecture merely to make manual YAML editing easier.

## Topology vs. Operational State

Workspace Fabric separates relatively static configuration from dynamic
behavior.

Static or slowly changing information includes:

- Controllers
- Physical devices
- Ports and endpoints
- Resource definitions
- Physical connections
- Declared capabilities

Dynamic information includes:

- Active routes
- Desired state
- Observed state
- Active workspaces
- Applied scenes
- Applied patches
- Transaction history
- Failures and warnings

This separation allows physical wiring to remain largely unchanged while
operational behavior changes continuously.

## Desired and Observed State

Workspace Fabric distinguishes requested state from verified state.

- **Desired state** records what the control plane intends to be true.
- **Observed state** records what controllers and drivers can verify.
- **Unknown state** is a legitimate result when hardware cannot report a value.

The system must not claim verification merely because a command was accepted or
no error was returned.

## Guiding Principles

1. Intent over implementation.
2. API-first, with all interfaces using the same control plane.
3. Driver isolation.
4. Explicit controller instances.
5. Truthful physical topology.
6. Deterministic behavior.
7. Explainable decisions.
8. Modular expansion.
9. Automation-friendly without embedding automation.
10. The control plane owns policy; drivers own implementation.
11. YAML remains open and editable, but need not be manually authored.
12. Architectural changes are captured intentionally in ADRs.

## Future Directions

Future enhancements may include:

- Interactive configuration authoring.
- Driver-assisted discovery and onboarding.
- Physical topology visualization.
- Multiple independent fabrics.
- Multi-fabric federation.
- Local Console Virtualization.
- Additional operating-system agents.
- Multi-user orchestration layers.
- Distributed control planes.
- High-availability controllers.
- Additional transport types.
- Rich desktop and tablet interfaces.
- Additional hardware and service drivers.
- Expanded patch operations and conflict resolution.

These capabilities should extend the architecture without requiring replacement
of the core domain model.
