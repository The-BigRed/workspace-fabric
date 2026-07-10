# Configuration Authoring

## Goals

The preferred Workspace Fabric configuration experience is graphical.

YAML is retained as a serialization format and advanced editing mechanism,
not as the primary authoring interface.

## Workflow

1. Add a Controller.
2. Configure connectivity.
3. Validate connectivity.
4. Driver introspects hardware.
5. Driver reports ports and capabilities.
6. User maps physical resources to discovered endpoints.
7. Workspaces are created from resources.
8. Scenes compose one or more workspaces.
9. Patches provide partial, non-destructive routing changes.

## Design Principles

- Users describe physical reality.
- Drivers describe capabilities.
- The UI remains hardware-agnostic.
- Configuration is derived from discovery wherever possible.
- YAML faithfully represents the resulting object graph.
