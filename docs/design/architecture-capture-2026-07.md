# Architecture Capture

## Purpose

This document captures architectural decisions, observations, and design evolution discussed during the initial Workspace Fabric design sessions. It serves as an engineering notebook and decision capture prior to integrating those decisions into the permanent project documentation.

Unlike the Architecture document, which describes the current design, this document records why the architecture evolved the way it did. It is expected that its contents will eventually be incorporated into Architecture Decision Records (ADRs), hardware documentation, and the project's permanent design documents.

## Evolution of the Project

Workspace Fabric began as an effort to improve the author's personal dual-workstation desk.

The original objective was to replace a conventional dual-monitor KVM with a more flexible switching solution capable of independently routing displays and USB peripherals between a desktop and work laptop.

Early hardware discussions centered around HDMI matrices, USB matrices, and the possibility of software control through TCP/IP or RS-232.

As the design evolved, it became clear that the project was not fundamentally about switching hardware. The real problem being solved was the orchestration of workspace resources.

This realization shifted the project from a collection of hardware drivers to a software-defined control plane.

The project's name changed from Console Fabric to Workspace Fabric to better reflect this broader scope.

Rather than centering on remote console access, Workspace Fabric now treats displays, USB peripherals, remote consoles, audio devices, and future workspace resources as independently routable assets managed through a unified resource model.

The initial desktop deployment remains the project's reference implementation, but it is no longer considered the architectural boundary.

The architecture is intentionally being designed to support future expansion into multiple independent fabrics, enterprise IP-KVM platforms, broadcast environments, laboratories, and other operator workspaces without requiring changes to the core orchestration engine.

## Core Philosophy

Workspace Fabric is built around the idea that a physical workspace should be treated as programmable infrastructure rather than a collection of independent hardware devices.

Traditional KVM switches, AV matrices, USB switches, and remote console systems expose hardware-centric interfaces built around ports, cables, and vendor-specific commands. While these devices solve individual routing problems, they do not provide a unified abstraction for describing the workspace itself.

Workspace Fabric shifts the focus from hardware to intent.

Instead of asking which HDMI input should be connected to which output, the user expresses the desired workspace configuration using logical resources such as displays, hosts, USB peripherals, remote consoles, and workspace profiles. The control plane is responsible for translating that intent into the hardware operations required to achieve the requested state.

The architecture intentionally embraces hardware diversity rather than hiding it. Hardware-specific capabilities such as EDID management, display scaling, fast switching, CEC, or future vendor-specific features are considered enhancements to the resource model rather than exceptions to it. Drivers expose these capabilities in a consistent manner while allowing the core orchestration engine to remain hardware agnostic.

The long-term objective is not to replace existing hardware, but to provide a common control plane capable of orchestrating heterogeneous devices from multiple vendors using a consistent resource-oriented model.

As the project evolves, the same architectural principles should apply equally to a personal workstation, a broadcast control room, a home laboratory, or a geographically distributed enterprise console environment.

## What is a Resource?

During the evolution of Workspace Fabric, the concept of a "resource" emerged as the central architectural abstraction. This distinction is fundamental to the rest of the project.

A resource is anything the user thinks about when describing their desired workspace.

Examples include:

- Displays
- Computers (hosts)
- Keyboards
- Mice
- Cameras
- Microphones
- Speakers
- Remote consoles
- Workspace profiles

Users express intent by describing relationships between these resources rather than by manipulating hardware directly.

Conversely, many implementation details exist solely to enable the system and should not be modeled as resources. Examples include:

- HDMI input numbers
- USB host port numbers
- Matrix output ports
- TCP sockets
- RS-232 interfaces
- Vendor-specific command sets
- EDID data
- Internal routing tables

These implementation details belong to drivers and the control plane. They may be exposed for diagnostics or advanced configuration, but they are not part of the primary resource model.

This distinction became one of the defining architectural concepts of Workspace Fabric. The user interacts with resources and intent; the control plane and drivers manage the underlying implementation details.

## Architectural Principles

 Workspace Fabric's architecture is guided by the following principles:

1. **Resources represent user intent.** Everything the user thinks about when configuring a workspace should be modeled as a resource. Implementation details remain internal to drivers and the control plane.

2. **Intent over implementation.** Users describe the desired workspace. Workspace Fabric determines how to achieve it.

3. **Hardware enriches the model but never defines it.** Vendor-specific features should be exposed through capabilities without changing the core architecture.

4. **Drivers isolate hardware behavior.** All device-specific communication belongs inside drivers.

5. **Capabilities are negotiated, not assumed.** Optional features are discovered, exposed, and validated instead of being required globally.

6. **Resource attachment is explicit.** No assumptions are made regarding port numbering, host continuity, or matrix topology.

7. **Transactions over commands.** Workspace changes are planned, validated, executed, and verified as transactions rather than imperative command sequences.

8. **Automation is a first-class interface.** Every capability exposed through the user interface should also be available through a documented API.

9. **Manual operation remains possible.** Workspace Fabric augments hardware rather than replacing manual operation. Front-panel controls remain a valid recovery path.

10. **Reference hardware is not the architecture.** The initial OREI hardware defines the reference implementation, not the limits of the project.

## Resource Model Evolution

One of the most significant architectural changes during the early design process was the transition from a hardware-oriented model to a resource-oriented model.

Early discussions naturally revolved around physical hardware such as HDMI matrices, USB matrices, monitors, and KVM switches. As additional use cases were explored, it became apparent that modeling the hardware directly would tightly couple the architecture to specific vendors and implementations.

The project instead evolved toward a logical resource model in which the user interacts exclusively with resources meaningful to their workspace rather than the underlying hardware.

Examples include:

- Hosts
- Displays
- USB peripherals
- Remote consoles
- Workspace profiles
- Fabrics

These logical resources are intentionally separated from their physical implementation.

For example, a "Primary 4K Display" is modeled as a display resource rather than "Output 1" on a particular video matrix. Likewise, a "Conference Camera" is represented as a USB resource rather than "USB Device Port 3."

This abstraction allows the same workspace configuration to be applied across different hardware implementations while still allowing individual drivers to expose vendor-specific capabilities.

### Resource Relationships

Resources do not exist independently. Instead, they form an explicit graph describing how the workspace is connected.

Examples include:

- A Host owns one or more Video Sources.
- A Display is attached to a Video Output.
- A USB Device belongs to exactly one USB Matrix.
- A Remote Console targets a Host.
- A Workspace references collections of resources rather than hardware ports.

The explicit relationship model replaces assumptions that are commonly found in traditional KVM systems.

### Explicit Resource Attachment

One important architectural decision was that Workspace Fabric must never assume symmetrical hardware.

For example, multiple USB matrices may expose completely different host connections.

Example:

USB Matrix A

- Host 1 → Desktop
- Host 2 → Work Laptop
- Host 3 → PiKVM
- Host 4 → Spare Laptop

USB Matrix B

- Host 1 → Desktop
- Host 2 → Work Laptop
- Host 3 → Controller
- Host 4 → Rack Server

Although maintaining consistent host numbering across matrices is considered a deployment best practice, it is not an architectural requirement.

The core resource model therefore records host attachment explicitly for every matrix instance.

Route validation is performed against these relationships rather than inferred from naming conventions or port numbers.

This decision also naturally enables multiple independent matrices, multiple independent fabrics, and future distributed deployments without introducing special-case logic into the core architecture.

## Driver Model Evolution

As the resource model matured, it became clear that the core Workspace Fabric controller should have no knowledge of specific hardware implementations.

Initially, discussions centered around implementing support for specific devices such as the OREI UHD-808 HDMI matrix and OREI UKM404 USB matrix. However, this quickly revealed a fundamental architectural concern: embedding hardware-specific logic within the core controller would tightly couple the project to a single vendor and make future expansion increasingly difficult.

The architecture instead evolved toward a driver-based model.

Drivers are responsible for all communication with physical hardware. The Workspace Fabric core communicates exclusively with abstract driver interfaces and never with vendor-specific protocols or command sets.

This separation establishes a clear boundary between orchestration and implementation.

### Responsibilities of the Core

The Workspace Fabric core is responsible for:

- Maintaining the resource model.
- Maintaining desired and actual state.
- Validating requested workspace changes.
- Planning transactions.
- Coordinating multiple drivers.
- Providing APIs and user interfaces.
- Persisting configuration and state.

The core intentionally has no knowledge of:

- RS-232 command syntax.
- TCP control protocols.
- HDMI matrix implementations.
- USB switching implementations.
- Vendor-specific capabilities.

### Responsibilities of Drivers

Drivers are responsible for:

- Discovering hardware capabilities.
- Establishing communication with hardware.
- Translating generic actions into device-specific commands.
- Reporting current hardware state where possible.
- Reporting supported capabilities.
- Returning structured errors and status information.

Drivers should not make policy decisions.

They execute the plans produced by the Workspace Fabric core.

### Drivers as Resource Providers

A significant realization during the design process was that drivers are more than communication adapters.

Drivers provide the bridge between physical hardware and the logical resource model.

For example:

- A Video Matrix driver exposes video routing resources.
- A USB Matrix driver exposes USB routing resources.
- A PiKVM driver exposes remote console resources.
- A future Windows Display Agent exposes operating system display resources.
- A future enterprise IP-KVM driver exposes remote console capabilities for rack-mounted systems.

This allows the core architecture to remain independent of any individual hardware platform while still taking advantage of advanced vendor-specific functionality.

### Multiple Driver Instances

The architecture intentionally supports multiple instances of the same driver.

For example, a deployment may contain:

- Two OREI UHD-808 video matrices.
- Two OREI UKM404 USB matrices.
- Multiple PiKVM devices.
- Multiple enterprise KVM systems.

Each instance maintains its own configuration, capabilities, and resource attachments.

The core orchestrates interactions between these independent driver instances through the shared resource model.

### Driver Independence

Drivers must not communicate directly with one another.

All coordination occurs through the Workspace Fabric core.

This ensures that drivers remain independently testable, reusable, and replaceable without affecting other portions of the system.

The core remains the single authority responsible for orchestration and transaction planning.

## Capability Model

During evaluation of the initial reference hardware, it became apparent that devices providing similar core functionality often differed significantly in their advanced feature sets.

For example, the OREI UHD-808 provides features including EDID management, display scaling, and fast switching, while many other video matrices provide only basic routing functionality. Likewise, future USB matrices, remote console systems, and enterprise KVM platforms will expose different capabilities depending on vendor and model.

Rather than reducing all hardware to the lowest common denominator, Workspace Fabric intentionally embraces these differences through a capability-driven architecture.

### Capabilities as First-Class Concepts

Capabilities represent optional functionality exposed by a driver.

Examples include:

- Video routing
- Route state discovery
- EDID management
- EDID cloning
- Display scaling
- Fast switching
- CEC control
- USB device discovery
- Operating system display management
- Remote power control
- Virtual media

The Workspace Fabric core does not assume that any optional capability exists. Instead, drivers advertise the capabilities supported by each hardware instance.

### Capability Negotiation

Workspace definitions may request optional capabilities while allowing the core to determine whether they are available.

This introduces capability negotiation between the desired workspace and the underlying hardware.

Rather than asking:

> Enable Fast Switching.

A workspace may instead express intent similar to:

> Use Fast Switching if available.

or

> Fast Switching is required for this workspace.

This allows workspace definitions to remain portable across different hardware platforms while still taking advantage of advanced features when available.

### Capability Policies

Several capability policies emerged during the design discussions.

Examples include:

- **Ignore** — Workspace Fabric does not manage this capability.
- **Prefer** — Enable the capability when supported. Continue with a warning if unavailable.
- **Require** — The capability must exist or the workspace fails validation.
- **Disable** — Explicitly disable the capability when supported.

These policies allow advanced hardware features to be incorporated into workspace definitions without creating unnecessary hardware dependencies.

### Capabilities Belong to Drivers

An important architectural decision is that capabilities belong to individual driver instances rather than to the Workspace Fabric core.

For example:

One video matrix may support:

- EDID management
- Scaling
- Fast switching

while another supports only:

- Video routing

Both drivers remain fully compatible with the same orchestration engine.

### Capabilities Extend the Resource Model

Capabilities should enhance existing resources rather than redefine them.

For example, a Display resource remains a Display regardless of whether the underlying hardware supports scaling.

Scaling is modeled as an optional capability associated with the route rather than creating a specialized "Scaling Display" resource.

This distinction keeps the resource model stable while allowing hardware innovation to be incorporated naturally over time.

### Lessons Learned

The capability model proved to be one of the most significant architectural discoveries during early hardware evaluation.

It allows Workspace Fabric to remain hardware agnostic while avoiding the common trap of limiting the entire platform to the lowest common denominator supported by every device.

Instead, advanced hardware can expose richer functionality without requiring changes to the core orchestration engine or the logical resource model.

## Transaction Model

As the project evolved beyond simple video and USB switching, it became apparent that workspace changes frequently require coordinated operations across multiple independent devices.

For example, activating a "Hybrid Meeting" workspace may require:

- Re-routing multiple video outputs.
- Re-routing USB peripherals.
- Applying EDID profiles.
- Configuring display scaling.
- Selecting a remote console target.
- Updating Windows display configuration through the Windows Display Agent.

Executing these operations independently creates opportunities for inconsistent or partially applied workspace states.

To address this, Workspace Fabric adopts a transaction-oriented execution model.

### Desired State

Workspace Fabric is fundamentally a desired-state system.

Users describe the workspace they want rather than the individual commands required to create it.

For example, a workspace definition might specify:

- The Primary Display should show the Desktop.
- The Secondary Display should show the Work Laptop.
- Keyboard and mouse belong to the Desktop.
- Camera and microphone belong to the Work Laptop.
- Fast switching should be enabled when available.

The Workspace Fabric core is responsible for determining how to achieve this state using the available hardware.

### Transaction Planning

Rather than immediately executing hardware commands, Workspace Fabric first constructs a transaction plan.

This planning stage allows the controller to:

- Validate requested routes.
- Validate resource ownership.
- Validate capability requirements.
- Detect conflicts.
- Determine execution order.
- Identify unsupported features before hardware changes occur.

Planning before execution also enables dry-run operation, allowing users or automation systems to preview the effects of a workspace change without modifying hardware.

### Transaction Execution

Once validation succeeds, the transaction is executed by coordinating one or more drivers.

Each driver is responsible for carrying out only the actions assigned to it.

Drivers do not communicate directly with one another.

The Workspace Fabric core remains responsible for coordinating execution across all participating drivers.

### Verification

Whenever practical, the controller should verify that requested changes were successfully applied.

Verification may include:

- Querying driver state.
- Confirming active routes.
- Confirming capability configuration.
- Detecting partial failures.
- Recording warnings.

Not all hardware supports complete state discovery.

When verification is not possible, drivers should report that limitation explicitly rather than assuming success.

### Partial Success

Workspace Fabric recognizes that not all transactions will complete successfully.

Examples include:

- Video routing succeeds while USB routing fails.
- Routing succeeds but EDID programming is unsupported.
- Windows Display Agent is unavailable.
- One of several matrices is unreachable.

Rather than treating these situations as catastrophic failures, Workspace Fabric records the resulting state and reports which portions of the requested workspace were successfully applied.

This provides users and automation systems with an accurate representation of the resulting workspace state.

### Transaction History

Every transaction should produce a structured execution record.

This history provides:

- Auditability.
- Troubleshooting.
- Diagnostics.
- Automation feedback.
- Future rollback support.

Rollback is not a Version 1 objective.

However, transaction records should preserve sufficient information to support future rollback functionality without requiring architectural changes.

## Hardware Discoveries

The initial hardware evaluation phase validated several architectural assumptions while also revealing behaviors that significantly influenced the design of Workspace Fabric.

Rather than treating these observations as implementation details, they are captured here because they directly affected the evolution of the core architecture.

Although these discoveries were made using the initial reference hardware, they should not be interpreted as defining characteristics of Workspace Fabric itself. Instead, they illustrate the importance of maintaining a hardware-agnostic architecture capable of accommodating differing behaviors across vendors and product lines.

### OREI UHD-808

The OREI UHD-808 was selected as the initial reference implementation for video routing due to its support for multiple inputs and outputs, documented control interfaces, and advanced feature set.

Hands-on evaluation revealed several behaviors that significantly influenced the Workspace Fabric architecture.

#### Active HDMI Link

The UHD-808 maintains an active HDMI link to source devices regardless of the currently selected output.

This behavior provides extremely fast switching between destinations because source devices continue to believe displays remain attached.

While beneficial in many environments, it also introduces an important consequence for workstation use.

Windows continues to believe displays are connected even after they are no longer routed to a physical monitor.

This observation directly led to the concept of the optional Windows Display Agent, allowing Workspace Fabric to control operating system display state independently of physical routing.

Importantly, this behavior should not be considered incorrect. Different deployment scenarios may prefer persistent display detection or dynamic display enumeration.

Workspace Fabric should support either approach through appropriate drivers and optional operating system integrations.

#### EDID Management

The UHD-808 supports cloning EDID information from connected displays.

However, experimentation revealed that EDID selection does not automatically follow routing changes.

Instead, EDID management is treated as an independent configuration element.

This discovery reinforced the architectural decision that routing and capability configuration are separate concepts.

Workspace Fabric should therefore expose EDID management as an optional driver capability rather than embedding it within the routing model.

#### Scaling

The UHD-808 includes built-in scaling capabilities.

Rather than treating scaling as a property of displays, Workspace Fabric models scaling as an optional capability associated with a video route.

This preserves a stable resource model while allowing advanced hardware to expose richer functionality.

#### Fast Switching

The UHD-808 supports fast switching between routes.

Although beneficial for user experience, this feature is not universally available across video matrices.

Workspace Fabric therefore treats fast switching as an optional capability rather than a required feature of video routing.

#### Lessons Learned

The UHD-808 demonstrated that advanced video matrices frequently expose functionality beyond simple routing.

Rather than reducing all hardware to a common subset of features, Workspace Fabric should expose these capabilities through the driver model while allowing workspace definitions to remain portable across simpler hardware implementations.

### OREI UKM404

The OREI UKM404 was selected as the initial reference implementation for USB routing.

The reference deployment ultimately incorporated multiple UKM404 units, leading to one of the most important discoveries regarding the resource model.

#### Independent Host Topology

Although the reference deployment maintains consistent host assignments across multiple USB matrices where practical, experimentation demonstrated that this continuity cannot be assumed.

Different USB matrices may expose entirely different host connections.

For example, one matrix may provide access to a desktop, work laptop, PiKVM, and spare laptop, while another may instead provide access to the desktop, work laptop, controller, and rack server.

This observation resulted in the architectural decision that host attachment belongs to individual matrix instances rather than to the Workspace Fabric core.

The core resource model therefore records host attachment explicitly for every matrix.

#### Resource Ownership

Each USB device belongs to exactly one USB matrix.

Consequently, route validation must occur within the context of that matrix.

Workspace Fabric must never assume that a route valid for one matrix is valid for another.

This realization reinforced the broader architectural principle that resource relationships are explicit rather than inferred.

#### Multiple Matrix Coordination

The use of multiple USB matrices demonstrated the importance of treating every hardware device as an independent driver instance.

The Workspace Fabric core coordinates these driver instances through the resource model rather than assuming shared topology or synchronized configuration.

This design naturally supports future deployments involving additional matrices, alternative vendors, or distributed workspace fabrics.

#### Lessons Learned

USB routing proved to be considerably more topology-dependent than originally anticipated.

By modeling host attachment explicitly and avoiding assumptions about global port numbering, Workspace Fabric remains flexible enough to support arbitrary USB routing architectures without introducing special-case logic into the core controller.

## Windows Display Agent

One of the first architectural expansions beyond hardware control arose from evaluation of the OREI UHD-808.

Because the matrix maintains an active HDMI link to source devices, Windows continues to believe displays remain connected even when they are no longer routed to a physical monitor.

Although this behavior is advantageous in environments requiring rapid switching, it conflicts with one of the primary goals of the reference deployment: allowing Windows to dynamically adapt its desktop layout based on the displays currently visible to the user.

Initially, the problem was viewed as a limitation of the video matrix itself.

Further analysis led to a different conclusion.

The matrix is correctly maintaining link state for the deployment scenarios it was designed to support.

The missing component is operating system awareness.

This realization led to the concept of the **Windows Display Agent**.

Rather than attempting to force hardware to behave differently, Workspace Fabric can optionally coordinate with a lightweight operating system agent capable of managing Windows display configuration.

Potential responsibilities include:

- Enumerating available displays.
- Enabling and disabling displays.
- Applying operating system display profiles.
- Reporting current desktop configuration.
- Synchronizing operating system state with physical routing.

Additional display-focused responsibilities identified for the Windows Display Agent include:

- Changing which display Windows considers the primary display.
- Enabling or disabling specific displays.
- Applying known display layouts.
- Reporting display identity, availability, and current role.
- Exposing only approved display controls to Workspace Fabric.

The agent should not assume that every display, display setting, or operating system capability should automatically be controllable through the fabric.

Instead, the agent should have its own local configuration defining which displays and capabilities it exposes.

This is important because the operating system may have access to devices or settings that should remain outside Workspace Fabric's control.

The agent therefore becomes both a capability provider and a policy boundary.

It advertises only the resources and actions explicitly configured for fabric control.

Importantly, the Windows Display Agent is not considered part of the core Workspace Fabric architecture.

It is an optional driver providing operating system resources to the control plane.

Deployments that do not require operating system display management should not need to install or configure it.

This established an important architectural precedent.

Workspace Fabric drivers are not limited to physical hardware.

Drivers may expose capabilities originating from operating systems, cloud services, or software components whenever those capabilities contribute meaningful resources to the workspace model.

### Beyond Display Management

Although the initial purpose of the Windows Display Agent is display control, the same architectural pattern may eventually support other operating system-level resources.

For example, a future agent could expose local devices or services to Workspace Fabric in a controlled way.

One possible future direction is local device encapsulation.

In this model, an agent could capture a local peripheral or service, encapsulate it over TCP/IP, and make it available to a remote agent on another system. Workspace Fabric would then manage the logical connection between those agents as part of the broader fabric.

This idea is exploratory and outside the initial implementation scope.

However, it reinforces the architectural principle that agents are not limited to display management. An agent may eventually act as a software-defined endpoint provider, exposing approved local resources into the fabric under explicit user control.

## PiKVM Integration

Remote console capabilities were considered throughout the early design process.

The initial concept treated PiKVM as an external system that could be integrated into Workspace Fabric to provide remote console access to selected hosts.

As the architecture evolved, it became clear that PiKVM should not occupy a privileged position within the system.

Instead, PiKVM became the reference implementation of a broader architectural concept: the Remote Console.

### Remote Console as a Resource

Rather than modeling PiKVM directly, Workspace Fabric models Remote Console resources.

A Remote Console represents the ability to observe and interact with a host independently of the primary workspace displays.

PiKVM is simply one implementation of this concept.

Future implementations may include:

- TinyPilot
- JetKVM
- Enterprise IP-KVM platforms
- Vendor-specific management interfaces
- Future remote console technologies

This abstraction allows the Workspace Fabric core to remain independent of any specific remote console platform.

### PiKVM as a Driver

Within the architecture, PiKVM is implemented as a driver.

The PiKVM driver contributes resources and capabilities to the Workspace Fabric resource model rather than existing as a separate management application.

Potential capabilities include:

- Remote console sessions.
- USB HID routing.
- Video capture routing.
- Power control.
- Virtual media.
- Console launch integration.

As with other drivers, these capabilities are optional and are advertised through the driver capability model.

### Dynamic Console Routing

One of the more significant architectural ideas to emerge during the design process was the realization that PiKVM itself can become part of the workspace fabric.

Rather than permanently wiring PiKVM to a single host, Workspace Fabric can dynamically determine which host should be presented to the remote console.

This allows a single PiKVM instance to provide remote access to multiple systems through coordinated video and USB routing.

Workspace Fabric therefore treats the remote console as another destination within the overall resource model rather than as an isolated management device.

This realization ultimately led to the broader concept of Local Console Virtualization, in which Workspace Fabric itself may eventually consume remote console technologies and present them through locally attached workspace resources.

### Future Evolution

Although PiKVM serves as the initial reference implementation, the long-term architecture intentionally avoids coupling the Workspace Fabric core to any specific remote console platform.

Future drivers should allow enterprise IP-KVM systems and other remote console technologies to participate in the same orchestration model without requiring architectural changes.

This approach preserves hardware independence while enabling Workspace Fabric to scale from a personal workstation to larger laboratory, broadcast, or enterprise deployments.

## Multi-Fabric Architecture

The original Workspace Fabric concept assumed a single workspace consisting of two computers, two displays, and a collection of USB peripherals.

As the architecture evolved, it became apparent that the same orchestration principles could naturally extend beyond a single physical workspace.

This realization introduced the concept of a **Fabric** as a logical collection of resources managed by a common control plane.

Examples include:

- Personal workstation.
- Home laboratory.
- Broadcast control room.
- Development test bench.
- Data center rack.
- Remote colocation facility.

Each fabric owns its own resources, hardware topology, drivers, and configuration.

### Independent Fabrics

An important architectural decision is that fabrics are intentionally independent.

A fabric should not assume the existence of another fabric, nor should it depend upon shared hardware or common topology.

Each fabric is capable of operating autonomously.

This independence allows Workspace Fabric to scale naturally from a single workstation to multiple geographically distributed environments.

### Unified Management

Although fabrics remain independent, future versions of Workspace Fabric may present multiple fabrics through a common management interface.

For example:

Workspace Fabric

- Home Workspace
- Home Lab
- Church Broadcast Booth
- Colocation Rack
- Test Environment

From the user's perspective, selecting a different fabric should feel similar to selecting a different workspace rather than switching to an entirely different application.

### Distributed Resources

The multi-fabric architecture intentionally avoids assuming that all resources are locally accessible.

Future fabrics may expose:

- Local HDMI matrices.
- Local USB matrices.
- Remote PiKVM instances.
- Enterprise IP-KVM systems.
- Software-based resources.
- Cloud-hosted management endpoints.

The orchestration model remains identical regardless of where those resources physically reside.

### Future Federation

Although not a Version 1 objective, the architecture intentionally leaves room for federation between independent Workspace Fabric instances.

Possible future capabilities include:

- Shared authentication.
- Centralized monitoring.
- Cross-fabric automation.
- Global search.
- Unified dashboard.
- Resource discovery.

The core architecture should avoid assumptions that would prevent future federation.

### Multi-User Orchestration Layer

Another future direction is a higher-level orchestration layer capable of managing shared Workspace Fabric environments for multiple users.

The initial reference deployment is single-user, but the architecture should not assume that only one operator exists.

A future orchestration layer may need to support:

- External authentication.
- Role-based access control.
- Resource ownership.
- Device locking.
- Workspace reservations.
- Conflict detection.
- Audit logging.
- Multi-user policy enforcement.

This becomes especially important in larger deployments where multiple operators may share access to the same physical or virtual fabric.

For example, in a data center or broadcast environment, one operator should not be able to inadvertently steal a display, KVM session, USB path, or remote console resource that another operator is actively using.

This capability is not part of the initial implementation and may never be implemented by the original author. However, the core architecture should avoid assumptions that would make multi-user coordination impossible later.

In particular, Workspace Fabric should avoid hard-coding single-user ownership semantics into the core resource model. Resource state should be capable of representing ownership, locks, reservations, or policy constraints in the future, even if Version 1 does not enforce them.

### Lessons Learned

The introduction of the Fabric abstraction significantly broadened the scope of Workspace Fabric.

Rather than managing a single desk, the architecture now supports the orchestration of multiple independent workspace environments while preserving a consistent resource model and control philosophy.

This expansion occurred without requiring fundamental changes to the core architecture, reinforcing the flexibility of the resource-oriented design.

## Future Exploration

Several concepts emerged during the initial design process that are intentionally outside the scope of the first implementation but are considered valuable future directions.

These ideas should not influence Version 1 implementation decisions unless specifically required to avoid future architectural limitations.

Areas identified for future exploration include:

### Local Console Virtualization

One of the more significant architectural ideas to emerge during the design process was the realization that Workspace Fabric should not only integrate with remote console technologies, but may eventually become a consumer of those remote consoles.

Traditional remote console platforms such as PiKVM, iDRAC, iLO, IMM, or enterprise IP-KVM systems are typically accessed through a browser or dedicated client application.

Workspace Fabric introduces the possibility of treating those remote console sessions as routable resources.

Rather than presenting a browser window, the controller could receive the remote video stream and virtual USB devices, then present those resources through the local workspace.

In this model, Workspace Fabric would:

- Receive a remote video stream.
- Receive remote keyboard and mouse endpoints.
- Route the video stream to one or more local displays.
- Route local keyboards and pointing devices back to the remote system.
- Present the remote system as though it were physically attached to the local workspace.

From the user's perspective, interacting with a remote server could become indistinguishable from interacting with a locally connected computer.

This concept extends the resource-oriented philosophy beyond physical hardware.

Whether a computer is connected through a local HDMI cable, a PiKVM, an enterprise IP-KVM, or another remote console technology becomes an implementation detail managed by drivers rather than something exposed to the user.

Although this capability is well beyond the scope of the initial implementation, the architecture should avoid assumptions that distinguish local and remote console resources unnecessarily.

This concept also suggests that future Workspace Fabric controllers may expose their own local displays and USB ports as fabric resources, allowing the controller itself to become an endpoint within the workspace.

### Additional Operating System Agents

The Windows Display Agent established the precedent that software components may participate as drivers.

Future operating system agents may expose additional capabilities including:

- Linux display management.
- macOS display management.
- Audio device management.
- Peripheral discovery.
- Window placement.
- Operating system workspace profiles.

### Software-Defined Endpoint Agents

Workspace Fabric may eventually support operating system agents that expose approved local resources into the fabric.

These agents could provide capabilities beyond display management, including controlled access to local peripherals, software services, or encapsulated device streams.

This creates a potential path toward software-defined endpoints where resources are not limited to physical matrix ports.

Any such agent must be explicitly configured by the local system owner and should expose only approved resources and capabilities to the fabric.

### Additional Resource Types

Future versions may introduce new resource types including:

- Audio routing.
- Lighting.
- Motorized desks.
- Environmental controls.
- Stream Deck devices.
- Smart power distribution.
- Sensor integration.

These resources should follow the same architectural principles established by the initial resource model.

### Enterprise Integrations

Future driver development may include:

- Enterprise IP-KVM systems.
- Hypervisor management platforms.
- Out-of-band management controllers.
- Broadcast routing systems.
- Professional AV hardware.

These integrations should expand the available resource graph without requiring changes to the Workspace Fabric core.

## Decisions Requiring ADRs

The following architectural decisions have been identified as sufficiently significant to warrant Architecture Decision Records (ADRs):

- Adoption of a resource-oriented architecture.
- Separation of the orchestration core from hardware drivers.
- Capability negotiation model.
- Explicit resource attachment.
- Per-matrix USB host mappings.
- Transaction-oriented execution.
- Driver-based operating system integration.
- Remote Console abstraction.
- Multi-Fabric architecture.
- Reference hardware philosophy.

As the project matures, each of these decisions should be documented as an ADR to preserve both the decision and its rationale.

## Required Documentation Updates

The discussions captured within this document identified several areas where the permanent project documentation should be expanded.

New documents anticipated include:

- Resource Model
- Driver Contract
- Capability Model
- Transaction Model
- Hardware Reference Documentation
- Windows Display Agent Design
- Driver Development Guide

Existing documentation requiring revision includes:

- README
- Architecture
- Vision
- Glossary
- Roadmap

The Architecture Capture document should be treated as the source material for these updates rather than as permanent project documentation.

## Deferred Features

The following concepts are intentionally deferred beyond the initial implementation.

Their inclusion here is intended to preserve architectural intent rather than establish implementation priority.

Examples include:

- Multi-fabric federation.
- Enterprise IP-KVM drivers.
- Local presentation of remote consoles.
- Distributed controllers.
- Cross-fabric automation.
- Automatic resource discovery.
- Driver marketplace or plugin distribution.
- Workspace synchronization between multiple operators.
- Advanced policy engine.
- Transaction rollback.
- Mobile applications.
- Native desktop applications.
- Multi-user orchestration layer with external authentication, RBAC, resource locking, and reservations.
- Software-defined endpoint agents capable of exposing approved local devices or services into the fabric.
- TCP/IP encapsulation of local device resources between agents.

These features should not influence Version 1 scope except where architectural flexibility should be preserved.

## Questions Still Open

Several architectural questions remain intentionally unresolved.

Examples include:

- How should multiple Workspace Fabric instances discover one another?
- Should federation be peer-to-peer, hierarchical, or service-based?
- What authentication model should be used across fabrics?
- How should driver plugins be packaged and distributed?
- What is the long-term persistence model for workspace definitions?
- Should transactions eventually support rollback?
- Should automation policies become a first-class subsystem?
- How should permissions be modeled for multi-user environments?
- Should multi-user locking and reservations eventually live inside Workspace Fabric itself, or in a higher-level orchestration layer above independent fabric controllers?
- What security and permission model should govern operating system agents that expose local resources into the fabric?
- Should device encapsulation between agents be considered part of Workspace Fabric core, or a separate extension layer?

These questions are intentionally left open to allow practical implementation experience to guide future architectural decisions.
