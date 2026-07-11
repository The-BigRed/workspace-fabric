# Workspace Fabric Architecture

## Purpose

This document describes the architectural structure of Workspace Fabric.

**Workspace Fabric is a hardware-agnostic control plane for dynamically
reconfigurable workspaces.**

It translates user intent into coordinated actions across independently
packaged drivers, configured controllers, physical devices, software agents,
and future service integrations.

Accepted architectural rationale is recorded in `docs/architecture/adr/`.

## Architectural Goals

Workspace Fabric is designed to:

- Abstract vendor behavior behind stable driver contracts.
- Support physical and virtual resources equally.
- Remain API-first.
- Be deterministic and explainable.
- Preserve truthful physical topology.
- Treat controllers, resources, capabilities, transactions, configuration, and
  drivers as first-class concepts.
- Support optional capabilities without reducing the platform to the lowest
  common denominator.
- Execute changes as validated transactions.
- Preserve an open, inspectable configuration representation.
- Support interactive configuration driven by installed driver metadata.
- Allow drivers to be installed, upgraded, rolled back, removed, and versioned
  independently from the core application.
- Preserve backward compatibility whenever practical.

Workspace Fabric is not an automation engine. Automation systems consume its
public API.

## Layered Architecture

```text
                           Clients
                CLI • API • Web UI • Automation
                              │
                              ▼
                  +------------------------+
                  | Workspace Fabric Core  |
                  +------------------------+
                              │
          +-------------------+-------------------+
          │                                       │
          ▼                                       ▼
     Configuration                          Resource Graph
          │                                       │
          +-------------------+-------------------+
                              ▼
                    Transaction Planner
                    Transaction Executor
                    Desired/Observed State
                              │
                              ▼
                    Controller Instances
                              │
                              ▼
                    Driver API Contract
                              │
                              ▼
                 Installed Driver Plugins
                              │
         +--------------------+--------------------+
         │                    │                    │
         ▼                    ▼                    ▼
    Video Drivers        USB Drivers        Other Drivers
         │                    │                    │
         +--------------------+--------------------+
                              ▼
                    Physical/Virtual Systems
```

The architecture flows in one direction. Clients express intent. The core
validates and plans. Controllers bind configuration to installed driver types.
Drivers translate assigned actions into native operations. Drivers do not make
global policy decisions or coordinate directly with one another.

## Package Architecture

Workspace Fabric separates runtime responsibilities into independently
versioned packages.

### Core Application

The core owns:

- Configuration loading and validation
- Resource graph construction
- Desired and observed state coordination
- Capability policy evaluation
- Transaction planning and execution
- Persistence and transaction history
- CLI, API, and user interfaces
- Installed-driver discovery and compatibility validation

The core must not contain or directly import vendor-specific protocol behavior.

### Driver API

The Driver API is a shared package containing portable contracts used by both
the core and driver implementations.

It owns:

- Driver interfaces
- Action and result models
- Capability representations
- State and health models
- Structured issue categories
- Plugin metadata contract
- Driver API compatibility version

The Driver API must remain free of orchestration policy and vendor-specific
implementation details.

### Driver Implementations

A driver implementation is an independently installable package for a hardware
family, platform, protocol, software agent, or service.

A driver package owns:

- Native communication behavior
- Driver-specific validation
- Static and discovered capability metadata
- Port and endpoint metadata
- Driver-specific state parsing
- Package version and compatibility declaration
- Entry-point registration

Installing a driver makes it available to the core. Removing an unused driver
must not affect unrelated operation.

### Driver Packs

A driver pack is an optional convenience metapackage depending on several
individual driver packages. Driver packs do not replace individual package
versioning, discovery, rollback, or removal.

## Driver Discovery

Installed drivers are discovered through standard Python package entry points.
The entry-point group is defined by ADR-0006.

The core builds a driver catalog from compatible plugins and records clear
diagnostics for plugins that cannot be loaded or are incompatible.

The core must not use production folder scanning as the primary plugin
mechanism. Source-tree placement is a repository concern; package entry points
are the runtime contract.

## Architectural Layers

### Layer 1 – Physical and Virtual Infrastructure

Examples include:

- HDMI and USB matrices
- Audio routing hardware
- Displays and hosts
- Keyboards, mice, cameras, and microphones
- Remote console systems
- BMCs and hypervisors
- Operating-system agents
- Cloud or local services

### Layer 2 – Driver Implementations

Drivers translate portable actions into native operations and report health,
capabilities, and observed state.

Drivers must not:

- Interpret global workspace intent
- Coordinate directly with other drivers
- Modify unrelated resources
- Own transaction policy
- Pretend unsupported or unknown behavior succeeded

### Layer 3 – Driver API

The Driver API defines the stable interchange between the core and installed
drivers. Compatibility is explicit and independently versioned.

### Layer 4 – Controller Instances

A controller is a configured instance of an installed driver.

A controller binds:

- Stable instance identifier
- Driver type identifier
- Connectivity and authentication settings
- Instance-specific capabilities
- Identity and port metadata
- Observed state

Multiple controllers may use the same driver package.

### Layer 5 – Control Plane

The control plane owns orchestration, policy, planning, execution, persistence,
and explanation. It coordinates controllers only through the Driver API.

### Layer 6 – Configuration and Resource Model

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

A driver is implementation code. A controller is a configured reachable
instance. Resources are the objects users and planners reason about. Workspaces,
scenes, and patches express reusable intent at different scopes.

### Layer 7 – Interfaces

All interfaces use the same control plane:

- CLI
- REST API
- Web UI
- Desktop client
- Tablet interface
- SDKs

### Layer 8 – Integrations

External systems consume stable APIs. Home Assistant, Node-RED, Stream Deck,
voice assistants, monitoring systems, and AI platforms remain integrations, not
core orchestration logic.

## Physical Topology and Resource Attachment

Workspace Fabric preserves explicit physical connectivity. Drivers describe
ports and capabilities. Controllers represent installed instances. Resources
map to controller endpoints. The planner resolves logical intent to device-local
actions before invoking a driver.

The system must not assume symmetrical ports, shared host maps, or universally
queryable state.

## Driver Metadata and Configuration Authoring

The preferred configuration experience is interactive and driven by the
installed driver catalog.

A future authoring interface should:

1. List compatible installed drivers.
2. Read driver-declared configuration requirements.
3. Create a controller instance.
4. Validate connectivity.
5. Query identity, ports, capabilities, and state where supported.
6. Map resources to declared or discovered endpoints.
7. Compose workspaces, scenes, and patches.
8. Validate and serialize the result.

The UI must not embed vendor-specific configuration logic when driver metadata
can describe it generically.

## YAML as Serialization

YAML remains an exposed and editable source of truth. It provides transparency,
version control, portability, and recovery. It is not the intended final primary
authoring experience.

Configuration references stable driver type identifiers, not Python module
paths or package names. Packaging changes should not force deployment-specific
controller identifiers to change.

## Desired and Observed State

- **Desired state** records what the core intends to be true.
- **Observed state** records what drivers can verify.
- **Unknown state** is legitimate when verification is unavailable.

The core must not claim verification merely because a command was sent.

## Versioning and Compatibility

The core, Driver API, and driver implementations use independent semantic
versioning.

- Compatible driver releases do not change the core version.
- Backward-compatible core or Driver API extensions use minor releases.
- Breaking public or Driver API changes use major releases.
- Compatibility failures are reported before controller use.

## Guiding Principles

1. Intent over implementation.
2. API-first.
3. Driver isolation.
4. Explicit controller instances.
5. Truthful topology.
6. Deterministic behavior.
7. Explainable decisions.
8. Modular expansion.
9. Independent driver lifecycle.
10. The core owns policy; drivers own assigned implementation.
11. YAML remains open and editable.
12. Architectural changes are captured in ADRs.
13. Extend before replacing.
14. Preserve backward compatibility whenever practical.
