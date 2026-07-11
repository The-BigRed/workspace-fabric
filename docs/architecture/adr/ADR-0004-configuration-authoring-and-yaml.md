# ADR-0004: Configuration Authoring and YAML Serialization

## Status
Accepted

## Context
The seed YAML file is useful because it exposes the full configuration and keeps Workspace Fabric transparent and customizable. However, hand-editing YAML becomes unwieldy as the model grows. It is easy to introduce typo, formatting, and reference errors when creating controllers, resources, physical mappings, workspaces, scenes, and patches manually.

The long-term product should allow users to configure physical reality through a purpose-built interface while preserving YAML as an inspectable and editable representation.

## Decision
YAML will be treated as a serialization format for the configuration model, not as the preferred long-term human authoring interface.

The preferred configuration experience is:

1. Select a supported device driver.
2. Configure a controller instance, including transport and connectivity details.
3. Verify connectivity.
4. Query the controller for available ports, endpoints, and capabilities where supported.
5. Create or select resources.
6. Map resources to discovered physical ports to reflect actual cabling.
7. Define workspaces, scenes, and patches from those resources.
8. Save the resulting model as YAML.

## Rationale
This approach keeps the system grounded in physical reality. Users should describe what is actually connected rather than manually authoring abstract routing tables.

Keeping YAML editable remains valuable because it allows advanced users to inspect, version, review, and modify configurations outside the UI. It also makes configurations suitable for Git and public examples.

## Consequences
- Public example YAML should avoid personal information and should use generic metadata.
- Real deployments can add owner, location, environment, and other metadata as needed.
- The configuration UI should be schema- and driver-driven where practical.
- The UI should prevent invalid references and incompatible connections when the driver exposes sufficient capability metadata.
- YAML validation should become part of the development workflow.
