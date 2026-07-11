# ADR-0003: Workspaces, Scenes, and Patches

## Status
Accepted

## Context
Workspace Fabric needs to support both simple personal routing changes and larger coordinated room states. In a small home office, most configurations may involve a single host, one or two monitors, and a keyboard/mouse set. In larger rooms, a single requested state may need to coordinate multiple users, displays, cameras, microphones, capture devices, lighting, and other integrations.

The project also needs a way to apply small targeted changes without redefining an entire workspace or scene.

## Decision
Workspace Fabric will use three separate concepts:

### Workspace
A workspace is a reusable operating environment. It describes the resources needed by one user, host, or activity.

Examples:

- Personal desktop workspace
- Work laptop workspace
- Split desktop workspace
- Presenter workspace
- Recorder workspace

### Scene
A scene is a complete environment state. It applies one or more workspaces and may later include additional room-level behavior.

A scene containing a single workspace is valid and expected to be common in small deployments.

Examples:

- Desktop scene -> personal desktop workspace
- Work laptop scene -> work laptop workspace
- Dual operator scene -> primary operator workspace + secondary operator workspace
- Presentation scene -> presenter workspace + recorder workspace + capture routing

### Patch
A patch is a partial state change applied to the current fabric state. It changes only the specified subset of routing and leaves unrelated configuration untouched.

Examples:

- Switch from secondary keyboard/mouse to primary keyboard/mouse
- Add a Stream Deck to the current workspace
- Move webcam to the work laptop
- Mirror a display output to PiKVM capture
- Route drop microphone without changing displays

## Rationale
Workspaces and scenes solve different problems. A workspace is reusable and focused. A scene is the complete requested state of an environment. Patches provide macro-like behavior for small changes that should not require a full scene or workspace definition.

This keeps the API simple for automation systems: external tools can usually activate a scene. For targeted changes, they can apply a patch.

## Consequences
- Scenes should be optional from a modeling perspective but should remain the preferred activation target for API/CLI consistency.
- A one-workspace scene is not redundant; it gives the system a stable activation abstraction.
- Patches should be non-destructive by default and should only alter explicitly specified routes.
- Documentation should avoid presenting scenes as only useful for large rooms; they are also useful as stable named activation targets in small deployments.
