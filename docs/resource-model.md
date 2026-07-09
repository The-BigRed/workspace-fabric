# Workspace Fabric Resource Model

## Purpose

This document defines the core resource model for Workspace Fabric.

The resource model is the foundation of the project. It describes the logical objects Workspace Fabric manages and how they relate to each other. Implementation details such as hardware port numbers, RS-232 commands, TCP sockets, and vendor-specific protocols belong to drivers and device configuration, not to the primary user-facing model.

Workspace Fabric models the workspace in terms of resources meaningful to the user.

## Resource Definition

A resource is anything the user thinks about when describing their desired workspace.

Examples:

- A display.
- A computer.
- A keyboard.
- A mouse.
- A camera.
- A microphone.
- A speaker device.
- A remote console.
- A workspace profile.
- A fabric.

Implementation details are not primary resources.

Examples of implementation details:

- HDMI input numbers.
- HDMI output numbers.
- USB host port numbers.
- USB device port numbers.
- RS-232 command syntax.
- TCP control ports.
- EDID blobs.
- Vendor-specific routing tables.

These details may be exposed for diagnostics or advanced configuration, but they are not the primary abstraction users interact with.

## Design Rules

The resource model follows these rules:

1. Resources represent user intent.
2. Resource attachment is explicit.
3. No global port symmetry is assumed.
4. Hardware-specific details remain behind drivers.
5. Resources may be physical, virtual, or software-defined.
6. A driver may contribute resources to the fabric.
7. A resource may expose optional capabilities through its driver.
8. A route is valid only if the resource graph supports it.

## Fabric

A fabric is a managed resource domain.

A fabric may represent:

- A desk workspace.
- A home lab.
- A broadcast booth.
- A rack.
- A colocation environment.
- A remote site.

Each fabric owns its own resources, drivers, topology, and state.

Example:

```yaml
fabrics:
  local_workspace:
    display_name: Local Workspace
    description: Main desktop workspace
```

Future versions may manage multiple independent fabrics through one interface, but each fabric should remain independently understandable.

## Host

A host is a computing target that may send or receive workspace resources.

Examples:

- Desktop PC.
- Work laptop.
- Spare laptop.
- Controller host.
- Rack server.
- PiKVM.
- Virtual machine.
- Remote system exposed through an IP-KVM.

Example:

```yaml
hosts:
  desktop:
    display_name: Personal Desktop

  work_laptop:
    display_name: Work Laptop
```

A host may own video sources, USB host attachments, remote console paths, power controls, or software agent capabilities.

## Video Source

A video source is a display output from a host or remote console provider.

Examples:

- Desktop DisplayPort 1.
- Desktop DisplayPort 2.
- Laptop dock HDMI output.
- PiKVM HDMI output.
- A decoded remote console stream.

Example:

```yaml
video_sources:
  desktop_dp1:
    host: desktop
    driver: uhd808
    port: 1
    display_name: Desktop DP1

  work_laptop_dp1:
    host: work_laptop
    driver: uhd808
    port: 3
    display_name: Work Laptop DP1
```

`driver` and `port` are attachment metadata, not the user-facing identity of the source. A
workspace continues to request `desktop_dp1 -> primary_4k`; the resource graph resolves that
intent to the physical input and output ports owned by the target driver.

## Video Output

A video output is an output path from a video routing device or software presentation layer.

Examples:

- HDMI matrix output 1.
- HDMI matrix output 2.
- Local console presentation output.
- Capture output feeding PiKVM.

Example:

```yaml
video_outputs:
  uhd808_out1:
    driver: uhd808
    port: 1

  uhd808_out2:
    driver: uhd808
    port: 2
```

## Display

A display is a user-facing screen resource.

A display should be modeled by its user-facing role, not by its matrix output number.

Examples:

- Primary 4K monitor.
- Secondary 2K meeting monitor.
- PiKVM capture display.
- Local console presentation display.

Example:

```yaml
displays:
  primary_4k:
    display_name: Primary 4K Monitor
    output: uhd808_out1

  secondary_2k:
    display_name: Secondary 2K Monitor
    output: uhd808_out2
```

## USB Matrix

A USB matrix routes USB devices to USB hosts.

Each USB matrix instance owns its own host map and device map.

Example:

```yaml
usb_matrices:
  ukm404_a:
    driver: ukm404_a
    fabric: local_workspace

  ukm404_b:
    driver: ukm404_b
    fabric: local_workspace
```

## USB Host Attachment

A USB host attachment is the connection between a host and a specific USB matrix host port.

Host attachments are per matrix.

Workspace Fabric must never assume that host port numbering is consistent across matrices.

Example:

```yaml
usb_matrices:
  ukm404_a:
    hosts:
      1: desktop
      2: work_laptop
      3: pikvm
      4: spare_laptop

  ukm404_b:
    hosts:
      1: desktop
      2: work_laptop
      3: controller
      4: rack_server
```

This means `desktop` may be attached to both matrices, while `controller` may only be attached to one.

## USB Device

A USB device is a user-facing peripheral attached to a specific USB matrix device port.

Examples:

- Keyboard.
- Mouse.
- Camera.
- Microphone.
- Speakers.
- Stream Deck.
- YubiKey.
- PiKVM HID endpoint.

Example:

```yaml
usb_devices:
  keyboard:
    display_name: Primary Keyboard
    matrix: ukm404_a
    device_port: 1

  mouse:
    display_name: Primary Mouse
    matrix: ukm404_a
    device_port: 2

  speakers:
    display_name: Speakers
    matrix: ukm404_b
    device_port: 1
```

A route from a USB device to a host is valid only if the device's owning matrix has that host attached.

## Remote Console

A remote console is a resource that allows a host to be observed and controlled outside the normal local display path.

Examples:

- PiKVM.
- TinyPilot.
- JetKVM.
- iDRAC console.
- iLO console.
- IMM/XClarity console.
- Enterprise IP-KVM session.

Example:

```yaml
remote_consoles:
  pikvm:
    display_name: PiKVM v4 Mini
    driver: pikvm
```

Remote consoles may provide capabilities such as:

- Remote video.
- HID injection.
- Virtual media.
- Power control.
- Console launch.
- Local console virtualization.

## Workspace

A workspace is a user-facing desired arrangement of resources for a task.

Examples:

- Work mode.
- Desktop mode.
- Hybrid meeting mode.
- Server maintenance mode.
- Presentation mode.

Example:

```yaml
workspaces:
  hybrid_meeting:
    video:
      primary_4k: desktop_dp1
      secondary_2k: work_laptop_dp1
    usb:
      keyboard: desktop
      mouse: desktop
      camera: work_laptop
      microphone: work_laptop
      speakers: work_laptop
```

## Scene

A scene is a named collection of desired state changes.

In early implementation, `workspace` and `scene` may be treated similarly. Over time, a workspace may become a higher-level user concept while scenes become reusable state templates.

## Route

A route is an active or desired relationship between resources.

Examples:

- `desktop_dp1 -> primary_4k`
- `keyboard -> desktop`
- `camera -> work_laptop`
- `pikvm -> rack_server`

A route may be physical, virtual, or logical.

## Resource Graph

The resource graph is the set of resources and relationships that define what routes are possible.

The route planner uses the graph to answer questions such as:

- Which driver owns this resource?
- Which matrix owns this USB device?
- Is the target host attached to that matrix?
- Which video output feeds this display?
- Which physical input/output ports correspond to this video route?
- Does the route require an unsupported capability?
- Would this route conflict with another active route?

## Validation Examples

Valid route:

```text
Request: speakers -> controller

speakers belongs to ukm404_b.
ukm404_b has controller attached.
Route is valid.
```

Invalid route:

```text
Request: camera -> controller

camera belongs to ukm404_a.
ukm404_a does not have controller attached.
Route is invalid.
```

## Implementation Notes for V0

V0 should implement enough of the resource model to support:

- Fabrics.
- Hosts.
- Video sources.
- Displays.
- USB matrices.
- USB host maps.
- USB devices.
- Workspaces.
- Mock route validation.

V0 should not attempt to implement every future concept.
