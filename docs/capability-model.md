# Workspace Fabric Capability Model

## Purpose

This document defines how Workspace Fabric represents optional device and driver functionality.

Not all hardware exposes the same features. A simple HDMI matrix may only route video. A more advanced matrix may support EDID management, scaling, fast switching, CEC, or audio breakaway. Workspace Fabric must support advanced features without requiring every driver to implement them.

Capabilities allow drivers to advertise what they can do, while allowing workspace definitions to express whether those features are optional or required.

## Capability Definition

A capability is a function exposed by a driver, device, software agent, or remote service.

Examples:

- Video routing.
- USB routing.
- Route state query.
- EDID management.
- EDID cloning.
- Scaling.
- Fast switching.
- CEC control.
- Display enable/disable.
- Primary display selection.
- Remote console launch.
- Virtual media.
- Power control.
- Wake-on-LAN.

## Capability Status

Drivers should report capability status explicitly.

Recommended values:

```text
supported
unsupported
unknown
```

### Supported

The driver knows the feature is available.

### Unsupported

The driver knows the feature is not available.

### Unknown

The driver cannot determine whether the feature is available or has not implemented detection yet.

`unknown` should not be treated as `supported`.

## Capability Policy

Workspace definitions may request a capability with a policy.

Recommended policies:

```text
ignore
prefer
require
disable
```

### Ignore

Workspace Fabric does not manage the capability.

### Prefer

Workspace Fabric should use the capability when available but continue with a warning if it is unsupported.

### Require

Workspace Fabric must fail validation if the capability is not supported.

### Disable

Workspace Fabric should explicitly disable the capability when supported.

## Policy Behavior

```text
supported + prefer  -> apply
supported + require -> apply
supported + disable -> disable
unsupported + prefer -> warn and continue
unsupported + require -> fail validation
unsupported + ignore -> do nothing
unknown + prefer -> warn and continue
unknown + require -> fail validation
```

## Capability Scope

Capabilities belong to specific driver instances, not to the core globally.

Example:

```yaml
drivers:
  uhd808:
    capabilities:
      video_routing: supported
      edid_clone: supported
      scaler: supported
      fast_switching: supported
      hpd_control: unsupported

  simple_hdmi_matrix:
    capabilities:
      video_routing: supported
      edid_clone: unsupported
      scaler: unsupported
      fast_switching: unknown
```

Both drivers can participate in Workspace Fabric even though their capabilities differ.

## Capabilities Enhance Resources

Capabilities should enhance existing resources rather than redefine them.

For example:

- A display remains a display whether scaling is available or not.
- A video route remains a video route whether fast switching is available or not.
- A remote console remains a remote console whether virtual media is available or not.
- A host remains a host whether a Windows Display Agent is installed or not.

This keeps the resource model stable while allowing hardware and software integrations to provide richer behavior.

## Example: Video Route Capability Request

```yaml
workspaces:
  desktop_primary:
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

If the video matrix supports fast switching and scaler control, the driver applies them.

If not, the scene still applies with warnings because the policy is `prefer`.

## Example: Required Capability

```yaml
workspaces:
  calibrated_presentation:
    video:
      primary_4k:
        source: presentation_laptop
        edid_profile:
          profile: primary_4k_native
          policy: require
```

If the active video driver does not support EDID profiles, validation fails before hardware changes occur.

## Driver Requirements

A driver should expose:

- Capability inventory.
- Capability status.
- Capability-specific validation rules.
- Capability-specific state where available.
- Structured errors when a requested capability cannot be applied.

## Core Requirements

The core should:

- Query driver capabilities.
- Validate requested capabilities before execution.
- Distinguish warnings from hard failures.
- Include unsupported optional capabilities in transaction results.
- Avoid assuming optional features exist.

## V0 Requirements

V0 should implement capability validation against mock drivers.

V0 should support at least:

- `supported`
- `unsupported`
- `unknown`
- `ignore`
- `prefer`
- `require`
- `disable`

V0 does not need to implement real hardware capability commands.
