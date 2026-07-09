# Workspace Fabric Configuration Model

## Purpose

This document defines the initial configuration model for Workspace Fabric.

The configuration model describes how fabrics, drivers, resources, capabilities, and workspaces are declared before they are loaded into the runtime resource graph.

This document is intentionally separate from the Resource Model.

- The Resource Model defines the logical objects Workspace Fabric understands.
- The Configuration Model defines how those objects are described in files.

## Goals

The configuration model should:

- Be readable by humans.
- Be friendly to source control.
- Be easy for AI tools to modify safely.
- Allow small deployments to use one file.
- Allow larger deployments to split configuration across multiple files.
- Support multiple fabrics.
- Support multiple driver instances.
- Support explicit resource attachment.
- Avoid requiring global port symmetry.
- Avoid vendor-specific assumptions in the core schema.

## Non-Goals for V0

V0 does not need:

- Dynamic discovery.
- Database-backed configuration.
- Multi-user configuration editing.
- Remote configuration synchronization.
- Secrets management beyond references/placeholders.
- Plugin-driven schema extension.

## File Format

YAML is the preferred initial configuration format.

Reasons:

- Human readable.
- Easy to review in Git.
- Familiar to infrastructure tools.
- Good fit for declarative desired state.
- Easy for AI coding tools to generate and edit.

JSON may be supported later for API import/export, but YAML should be the initial authoring format.

## Configuration Layout Options

Small deployments may use one file:

```text
config/workspace-fabric.yaml
```

Larger deployments may split configuration:

```text
config/
  fabrics.yaml
  drivers.yaml
  resources.yaml
  workspaces.yaml
```

V0 may start with a single file but should not prevent later splitting.

## Top-Level Sections

Recommended top-level sections:

```yaml
version: 1

fabrics: {}

drivers: {}

hosts: {}

video_sources: {}

video_outputs: {}

displays: {}

usb_matrices: {}

usb_devices: {}

remote_consoles: {}

workspaces: {}
```

## Version

Configuration should include a schema version.

```yaml
version: 1
```

This allows future migrations without ambiguity.

## Fabrics

A fabric is a managed resource domain.

```yaml
fabrics:
  local_workspace:
    display_name: Local Workspace
    description: Main desk workspace
```

## Drivers

Drivers declare concrete hardware, software agents, or remote services.

```yaml
drivers:
  uhd808:
    type: orei_uhd808
    fabric: local_workspace
    connection:
      method: tcp
      host: 192.0.2.10
      port: 23

  ukm404_a:
    type: orei_ukm404
    fabric: local_workspace
    connection:
      method: tcp
      host: 192.0.2.20
      port: 23
```

Mock drivers should be valid configuration targets:

```yaml
drivers:
  mock_video:
    type: mock_video_matrix
    fabric: local_workspace

  mock_usb:
    type: mock_usb_matrix
    fabric: local_workspace
```

## Hosts

Hosts represent computing targets.

```yaml
hosts:
  desktop:
    fabric: local_workspace
    display_name: Personal Desktop

  work_laptop:
    fabric: local_workspace
    display_name: Work Laptop

  pikvm:
    fabric: local_workspace
    display_name: PiKVM
```

## Video Sources

Video sources represent host video outputs or remote/presented sources.

```yaml
video_sources:
  desktop_dp1:
    fabric: local_workspace
    host: desktop
    driver: uhd808
    port: 1
    display_name: Desktop DP1

  work_laptop_dp1:
    fabric: local_workspace
    host: work_laptop
    driver: uhd808
    port: 3
    display_name: Work Laptop DP1
```

`driver` and `port` are optional for purely logical or mock configurations, but physical matrix
configurations should attach each source to the driver instance and input port that receives it.
The orchestration layer uses this attachment to translate user-facing source IDs into device-local
ports before invoking a hardware video driver.

## Video Outputs

Video outputs represent driver-owned outputs.

```yaml
video_outputs:
  uhd808_out1:
    fabric: local_workspace
    driver: uhd808
    port: 1

  uhd808_out2:
    fabric: local_workspace
    driver: uhd808
    port: 2
```

## Displays

Displays represent user-facing monitor resources.

```yaml
displays:
  primary_4k:
    fabric: local_workspace
    display_name: Primary 4K Monitor
    output: uhd808_out1

  secondary_2k:
    fabric: local_workspace
    display_name: Secondary 2K Monitor
    output: uhd808_out2
```

## USB Matrices

USB matrices are declared as resources attached to driver instances.

The host map is explicit per matrix.

```yaml
usb_matrices:
  ukm404_a:
    fabric: local_workspace
    driver: ukm404_a
    hosts:
      1: desktop
      2: work_laptop
      3: pikvm
      4: spare_laptop

  ukm404_b:
    fabric: local_workspace
    driver: ukm404_b
    hosts:
      1: desktop
      2: work_laptop
      3: controller
      4: rack_server
```

## USB Devices

USB devices belong to a specific USB matrix.

```yaml
usb_devices:
  keyboard:
    fabric: local_workspace
    display_name: Primary Keyboard
    matrix: ukm404_a
    device_port: 1

  camera:
    fabric: local_workspace
    display_name: Conference Camera
    matrix: ukm404_a
    device_port: 3

  speakers:
    fabric: local_workspace
    display_name: Speakers
    matrix: ukm404_b
    device_port: 1
```

## Remote Consoles

Remote consoles represent PiKVM, enterprise IP-KVM, BMC consoles, or future console providers.

```yaml
remote_consoles:
  pikvm:
    fabric: local_workspace
    display_name: PiKVM v4 Mini
    driver: pikvm
```

## Workspaces

Workspaces describe desired resource relationships.

```yaml
workspaces:
  hybrid_meeting:
    fabric: local_workspace
    display_name: Hybrid Meeting
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

## Capability Requests

Workspace definitions may request optional capabilities with policies.

```yaml
workspaces:
  desktop:
    video:
      primary_4k:
        source: desktop_dp1
        fast_switching:
          enabled: true
          policy: prefer
        scaler:
          mode: passthrough
          policy: prefer
```

Simple shorthand should be allowed where no capability options are required:

```yaml
video:
  primary_4k: desktop_dp1
```

The parser may normalize shorthand into full internal form.

## Validation Rules

The configuration loader should validate:

- Unique IDs.
- Required fields.
- References to existing resources.
- Resources belong to valid fabrics.
- Driver references exist.
- Physical video source attachments include both driver and port when either is configured.
- USB devices reference existing USB matrices.
- USB routes target hosts attached to the owning matrix.
- Video displays reference valid outputs.
- Workspaces reference valid resources.
- Capability policies use known values.

## Secrets

V0 should avoid embedding secrets directly in configuration examples.

Future options:

```yaml
connection:
  token_env: WORKSPACE_FABRIC_PIKVM_TOKEN
```

or

```yaml
connection:
  token_file: /etc/workspace-fabric/secrets/pikvm.token
```

Secrets management is not part of V0 but should not be precluded.

## Example V0 Config

See `examples/local-workspace.yaml`.

## Implementation Priority

V0 should implement:

1. Load a single YAML file.
2. Validate basic schema.
3. Build resource graph.
4. Load mock drivers.
5. Validate workspaces against graph.
6. Produce transaction plans.

Splitting files, plugin schemas, and dynamic discovery can wait.
