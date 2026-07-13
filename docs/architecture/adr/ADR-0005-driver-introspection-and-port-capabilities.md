# ADR-0005: Driver Metadata and Endpoint Introspection

## Status

Accepted

## Context

Workspace Fabric is intentionally designed to support a wide variety of physical devices, software agents, operating-system integrations, and future service-based controllers without embedding vendor-specific knowledge in the core orchestration engine.

Different controllers expose different:

* Endpoint types
* Port layouts
* Routing capabilities
* Connection constraints
* Optional capabilities
* Identity information
* Configuration requirements

Examples include:

* HDMI matrices
* USB matrices
* Audio DSPs
* Operating-system agents
* Remote console platforms
* Future AV-over-IP systems

While these controllers differ significantly in implementation, the Workspace Fabric core must validate configuration, construct a truthful resource graph, plan deterministic transactions, and expose a generic configuration experience without requiring controller-specific logic.

Early discussion focused primarily on using metadata to simplify future configuration authoring. As the architecture matured, it became clear that driver metadata serves a much broader role.

Driver metadata is now a foundational architectural contract consumed by:

* Configuration authoring
* Configuration validation
* Resource graph construction
* Transaction planning
* Capability negotiation
* Diagnostics
* User interfaces
* Future automation and AI consumers

The driver is the authoritative source describing the hardware or software it represents.

The core is responsible for interpreting that information to make orchestration decisions.

---

## Decision

Every Workspace Fabric driver shall expose machine-readable metadata describing the controller, its endpoints, capabilities, configuration requirements, and supported operations.

Driver metadata is descriptive rather than prescriptive.

Drivers describe the hardware or software they implement.

The Workspace Fabric core interprets that information when validating configuration, constructing topology, planning transactions, and coordinating controllers.

Drivers do not make orchestration decisions.

---

## Metadata Categories

Driver metadata is organized into several conceptual categories.

### Controller Metadata

Controller metadata describes the driver implementation and configured controller instance.

Examples include:

* Driver type identifier
* Display name
* Supported transports
* Driver version
* Driver API compatibility
* Supported firmware families where applicable
* Connectivity capabilities
* Authentication requirements
* Optional documentation references

---

### Endpoint Metadata

Endpoint metadata describes the controller's externally visible connection points.

Each endpoint should describe information such as:

* Endpoint identifier
* Endpoint category
* Direction
* Accepted resource types
* Routing constraints
* Disconnect support
* Static properties
* Runtime-discovered properties where supported

Conceptually:

```yaml
endpoints:

  video_inputs:

    direction: sink

    accepts:
      - video_source

    cardinality:

      incoming:
        min: 1
        max: 1

      outgoing:
        min: 0
        max: many

    supports_disconnect: false
```

Another example:

```yaml
endpoints:

  usb_device_ports:

    direction: source

    accepts:
      - keyboard
      - mouse
      - camera
      - microphone

    cardinality:

      outgoing:
        min: 1
        max: 1

    supports_disconnect: false
```

These examples describe hardware behavior.

They do not dictate how Workspace Fabric should apply routes.

---

### Capability Metadata

Drivers advertise optional functionality through capability metadata.

Examples include:

* Route state discovery
* EDID management
* Scaling
* CEC
* Fast switching
* Health reporting
* Identity discovery
* Operating-system integration
* Future controller-specific capabilities

Capabilities remain controller-instance specific.

Unknown capability information should be reported honestly rather than inferred.

---

### Configuration Metadata

Drivers describe the information required to configure a controller instance.

Examples include:

* Required connection parameters
* Optional parameters
* Authentication methods
* Timeout settings
* Validation rules
* Transport-specific requirements

This metadata enables generic configuration authoring without embedding vendor-specific logic into the configuration application.

---

### Identity Metadata

Where supported, drivers should expose identity information describing the connected controller.

Examples include:

* Vendor
* Model
* Serial number
* Firmware version
* Hardware revision
* Runtime identity

Runtime-discovered identity supplements static metadata but does not replace stable driver identifiers.

---

## Endpoint Constraints

Endpoint metadata should truthfully describe routing constraints exposed by the underlying controller.

Examples include:

* Minimum supported relationships
* Maximum supported relationships
* Directionality
* Accepted endpoint types
* Disconnect support
* Required assignment

Metadata describes hardware capabilities.

It does not define orchestration policy.

Workspace Fabric intentionally separates:

* What the hardware supports
* What the user requests
* How the core reconciles those requests

The interpretation of endpoint constraints is defined by the transaction planner and related architectural decisions.

---

## Responsibilities

Workspace Fabric intentionally separates description from orchestration.

### Drivers Describe

Drivers are responsible for describing:

* Controller identity
* Endpoints
* Capabilities
* Configuration requirements
* Routing constraints
* Supported operations
* Observed state where available

Drivers should expose truthful information rather than attempting to compensate for orchestration policy.

---

### The Core Decides

The Workspace Fabric core is responsible for:

* Configuration validation
* Resource graph construction
* Endpoint compatibility validation
* Capability negotiation
* Transaction planning
* Route reconciliation
* Conflict detection
* Supporting action selection
* Transaction execution

Drivers execute the operations assigned by the core.

Drivers do not determine user intent or global routing policy.

---

## Runtime Discovery

Where practical, runtime discovery should augment static metadata.

Examples include:

* Firmware version
* Installed option cards
* Available ports
* Connected endpoints
* Hardware capabilities
* Identity information

Runtime discovery should enrich static metadata rather than replace it.

Drivers must continue to provide sufficient metadata to support validation even when hardware is temporarily unavailable.

---

## Rationale

Driver metadata enables Workspace Fabric to remain hardware-independent.

Rather than teaching the core about every supported controller, drivers describe themselves through a consistent metadata model.

This allows:

* Generic configuration authoring
* Hardware-independent validation
* Dynamic topology construction
* Deterministic transaction planning
* Capability negotiation
* Rich diagnostics
* Future visualization
* Future automation
* Future AI-assisted tooling

New drivers participate in these workflows by exposing metadata rather than requiring modifications to the Workspace Fabric core.

This preserves the controller/driver boundary while allowing the platform to grow naturally as additional hardware classes are introduced.

---

## Consequences

* Driver metadata becomes the authoritative description of controller capabilities.
* The transaction planner consumes metadata rather than relying on hard-coded hardware assumptions.
* Configuration tooling remains generic across supported controller types.
* User interfaces remain hardware-independent.
* Future driver capabilities can extend metadata without requiring architectural changes when compatibility is preserved.
* Runtime discovery supplements, but does not replace, static driver metadata.
* Drivers remain responsible for describing hardware.
* The Workspace Fabric core remains responsible for orchestration.

---

## Alternatives Considered

### Hard-Code Controller Knowledge into the Core

Rejected.

Embedding controller-specific behavior into the Workspace Fabric core would tightly couple orchestration to individual hardware implementations and require core modifications whenever new controller types are introduced.

---

### User Interface Defines Supported Controllers

Rejected.

Configuration tooling should consume driver metadata rather than maintaining independent knowledge of supported hardware.

Doing otherwise would require updating the UI whenever a new driver becomes available.

---

### Drivers Implement Orchestration Policy

Rejected.

Drivers describe hardware capabilities and execute assigned operations.

Determining user intent, resolving conflicts, selecting supporting actions, and coordinating multiple controllers remain responsibilities of the Workspace Fabric core.

---

## Relationship to Other ADRs

* **ADR-0002** defines the controller and driver boundary.
* **ADR-0006** defines driver packaging, discovery, and lifecycle.
* **ADR-0009** defines endpoint relationships, routing cardinality, and how the Workspace Fabric core interprets endpoint metadata during orchestration.

Together these ADRs establish that drivers describe themselves through metadata while the Workspace Fabric core remains the sole authority responsible for validation, planning, reconciliation, and execution.
