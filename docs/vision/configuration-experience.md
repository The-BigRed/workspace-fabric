# Configuration Experience Vision

Workspace Fabric should not require users to hand-edit YAML as the primary configuration method.

YAML is valuable and should remain fully exposed, versionable, and manually editable. It provides transparency, supports Git workflows, and allows advanced customization when the UI does not yet expose a needed feature. However, YAML should be treated as the serialized form of the configuration model rather than the main user experience.

## Desired user flow

The preferred configuration experience is physical and guided:

1. Add a controller by selecting a supported device driver.
2. Configure connection details such as transport, address, port, and credentials.
3. Test connectivity.
4. Let the driver identify the hardware and expose known or discovered ports and capabilities.
5. Create resources representing real-world endpoints such as displays, host video outputs, keyboards, mice, cameras, microphones, capture devices, and USB host connections.
6. Connect resources to controller ports to describe actual cabling.
7. Define workspaces from resources.
8. Define scenes that apply one or more workspaces.
9. Define patches for small, targeted changes to the current state.

## Design principles

- Users describe physical reality; Workspace Fabric derives the routing model.
- Drivers expose capabilities so the UI can remain generic.
- Controllers represent configured reachable instances of drivers.
- Resources represent real-world devices or endpoints.
- Workspaces describe reusable operating environments.
- Scenes describe complete environment states.
- Patches describe partial changes to the current state.
- YAML remains editable for transparency and advanced control.
- Public examples should avoid personal, location-specific, or secret information.

## Why this matters

As the system grows, manually maintaining a congruent YAML structure becomes fragile. A guided configuration interface can prevent invalid references, incompatible resource mappings, missing endpoints, and accidental topology drift.

This also aligns with the core Workspace Fabric vision: plug everything into the fabric once, describe how it is connected, and let software perform the rewiring.
