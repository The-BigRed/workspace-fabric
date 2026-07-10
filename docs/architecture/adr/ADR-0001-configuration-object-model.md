# ADR-0001: Configuration Object Model

## Status
Accepted

## Context
Workspace Fabric needs a configuration model that can describe real-world devices, physical connections, reusable workspaces, whole-room scenes, and small targeted routing changes. The model must support simple personal workspaces while leaving room for larger rooms, conference spaces, automation platforms, and future graphical configuration tools.

Early configuration work showed that hand-editing YAML can quickly become error-prone when the file must remain internally congruent across controllers, resources, hardware mappings, workspaces, scenes, and partial changes.

## Decision
Workspace Fabric will use the following conceptual hierarchy:

```text
Driver
  -> Controller
  -> Physical ports / endpoints
  -> Resources
  -> Workspace
  -> Scene
  -> Patch
```

Definitions:

- **Driver**: Code-level implementation for a supported hardware or software integration, such as `orei-uhd-808`, `orei-ukm404`, `pikvm`, or a host display agent.
- **Controller**: A configured instance of a driver, including connection details such as transport, host, port, credentials, and timeouts.
- **Physical port / endpoint**: A concrete connection point exposed by a controller or resource, such as HDMI input 1, USB host port 2, DisplayPort output 1, or a USB HID endpoint.
- **Resource**: A named real-world thing or endpoint used by Workspace Fabric, such as a monitor, desktop display output, keyboard, mouse, webcam, microphone, or PiKVM capture input.
- **Workspace**: A reusable operating environment that binds a host or activity to the resources it needs.
- **Scene**: A complete environment state that applies one or more workspaces.
- **Patch**: A partial routing operation applied to the current state without redefining or reapplying a full workspace or scene.

## Rationale
This model separates code capability, configured hardware instances, physical topology, reusable environments, complete states, and partial changes. That separation keeps the project understandable as it grows.

The distinction between workspaces, scenes, and patches is especially important:

- A workspace describes what one operator, host, or activity needs.
- A scene describes what the overall environment should become.
- A patch describes a narrow change to whatever is currently active.

This allows small deployments to remain simple while still supporting larger multi-workspace rooms later.

## Consequences
- YAML should serialize this object model rather than become the primary human authoring interface.
- The CLI/API should generally activate scenes, even when a scene contains only one workspace.
- Patches should be available for small changes such as swapping keyboard/mouse sets, adding a Stream Deck, moving a webcam, or temporarily routing PiKVM capture.
- Future UI work should be designed around the object model, not around directly editing YAML.
