# Workspace Fabric Glossary

This glossary defines the core vocabulary used by Workspace Fabric.
These terms are intended to stay stable as the project evolves.

## Fabric

The complete managed environment controlled by Workspace Fabric.

A fabric may include physical devices, virtual resources, management
controllers, remote consoles, automation platforms, and user-facing
workspaces.

## Control Plane

The software layer that understands the fabric, tracks state, makes
routing decisions, and sends commands to devices through drivers.

The control plane does not directly represent a single hardware device.
It coordinates many devices as one logical system.

## Driver

A software module that communicates with a specific device, platform,
protocol, or service.

Examples:

-   OREI UHD-808 HDMI matrix driver
-   OREI UKM-404 USB matrix driver
-   Dell iDRAC driver
-   HPE iLO driver
-   Proxmox API driver
-   Home Assistant API driver

Drivers translate Workspace Fabric actions into native commands.

## Device

A physical or virtual component managed by Workspace Fabric.

Examples:

-   HDMI matrix
-   USB matrix
-   Audio processor
-   IP KVM
-   Server BMC
-   Proxmox host
-   Virtual machine
-   Smart power controller

## Endpoint

Anything that can participate in a connection.

An endpoint may be a source, destination, or both.

Examples:

-   Desktop PC HDMI output
-   Laptop USB connection
-   Monitor HDMI input
-   Keyboard and mouse set
-   iDRAC remote console
-   Proxmox VM console

## Source

An endpoint that originates a signal, session, or resource.

Examples:

-   Computer video output
-   USB host
-   Server console
-   Remote desktop session
-   Virtual machine console

## Sink

An endpoint that receives a signal, session, or resource.

Examples:

-   Monitor
-   Keyboard and mouse
-   Speakers
-   Microphone input
-   Browser-based remote console window

## Capability

A specific function exposed by a device or driver.

Examples:

-   Route video
-   Route USB
-   Open remote console
-   Power on device
-   Query power state
-   Launch SSH session
-   Launch RDP session

Capabilities allow Workspace Fabric to reason about what a device can do
without hard-coding vendor-specific behavior into the core model.

## Toolkit

A collection of non-routing actions that support operating the fabric.

Toolkit actions may prepare devices, recover from errors, query status, launch access methods, or perform operational tasks that are related to a workspace but are not themselves routes.

## Toolkit Action

A specific non-routing action exposed by Workspace Fabric.

Examples:

-   Send Wake-on-LAN magic packet
-   Power on device through BMC
-   Open iDRAC console
-   Launch SSH session
-   Send CEC monitor power command
-   Refresh device status
-   Run health check

## Wake Action

A toolkit action that attempts to make a device available.

Examples:

-   Send Wake-on-LAN magic packet
-   Power on through iDRAC, iLO, IMM, or Redfish
-   Trigger smart plug power
-   Resume a virtual machine

## Route

An active connection between endpoints.

Examples:

-   Desktop PC video to center monitor
-   Laptop USB to keyboard and mouse
-   Server HDMI to capture device
-   iDRAC console to browser session

A route may be physical, virtual, or logical.

## Scene

A named collection of routes and device states.

Examples:

-   Work mode
-   Gaming mode
-   Server maintenance mode
-   Dual laptop mode
-   Presentation mode

Applying a scene changes the fabric into a known arrangement.

## Scene Scope

The subset of the fabric that a scene is intended to control.

A scene should only modify endpoints, routes, device states, or toolkit actions that are explicitly included in its scope.

Anything outside the scene scope should be left unchanged.

## Mask

A rule that tells Workspace Fabric to ignore part of the fabric when applying a scene.

Masks prevent scenes from unintentionally disturbing unrelated sources, sinks, routes, or devices.

Example:

```text
Scene: Work Mode
```

Included:
-   center_monitor video
-   keyboard_mouse USB
-   speakers audio

Masked / ignored:
-   left_monitor
-   right_monitor
-   capture_card
-   lab_server_console

## Workspace

The user-facing arrangement of resources for a particular task.

A workspace describes what the user wants to accomplish, not necessarily
which hardware commands are required.

Example:

> "Use the main desktop on the center monitor with keyboard, mouse,
> speakers, and webcam."

## Path

The actual sequence of devices, ports, protocols, or services used to
satisfy a route.

Example:

``` text
Desktop PC HDMI output
  -> OREI UHD-808 input 1
  -> OREI UHD-808 output 3
  -> Center monitor HDMI input
```

A user may request a route or workspace without needing to know the
path.

## Port

A physical or logical connection point on a device.

Examples:

-   HDMI input 1
-   HDMI output 3
-   USB host port 2
-   USB device port 4
-   TCP port for telnet control
-   API endpoint for a management controller

## Friendly Name

A human-readable name assigned to a device, endpoint, port, scene, or
workspace.

Example:

Instead of:

``` text
input 1 -> output 3
```

Workspace Fabric should allow:

``` text
gaming_pc -> center_monitor
```

## State

Workspace Fabric's understanding of the current fabric arrangement.

State may include active routes, device availability, power status,
selected inputs, known errors, and last-seen information.

State may be observed from hardware, inferred from commands, or stored
locally.

## Desired State

The arrangement Workspace Fabric is trying to apply.

Example:

``` text
desktop_pc video -> center_monitor
desktop_pc usb -> keyboard_mouse
speakers -> desktop_pc
```

The control plane compares desired state to current state and decides
what actions are required.

## Reconciliation

The process of comparing current state with desired state and taking
action to bring the fabric into alignment.

This concept becomes important for automation, reliability, and recovery
after hardware or network failures.

## Integration

A connection between Workspace Fabric and another system.

Examples:

-   Home Assistant integration
-   OpenClaw integration
-   Discord bot integration
-   Voice assistant integration
-   Zabbix monitoring integration

Integrations consume or expose Workspace Fabric functionality but are
not the core fabric model.

## Physical Path

A path that uses physical signal routing hardware.

Examples:

-   HDMI matrix switching
-   USB matrix switching
-   Audio matrix routing
-   Relay-controlled power

## Virtual Path

A path that uses software, network protocols, or management systems
instead of direct physical switching.

Examples:

-   iDRAC remote console
-   iLO remote console
-   Proxmox VM console
-   RDP
-   SSH
-   VNC
-   SPICE

## Best Available Path

The route Workspace Fabric chooses based on availability, capability,
policy, and user intent.

Example:

If a server is powered on and connected to the HDMI/USB fabric,
Workspace Fabric may use the physical path.

If the server is powered off or disconnected, Workspace Fabric may use
iDRAC, iLO, or another remote console path instead.

## Policy

A rule that influences what Workspace Fabric is allowed or preferred to
do.

Examples:

-   Prefer physical video when available.
-   Use BMC console if the server is powered off.
-   Never expose management interfaces outside the trusted network.
-   Require confirmation before power-cycling a server.
-   Do not allow voice assistants to perform destructive actions.

## Operator

A person or system requesting changes to the fabric.

Examples:

-   Human user
-   Web UI
-   CLI
-   OpenClaw
-   Home Assistant
-   Voice assistant
-   Scheduled automation
