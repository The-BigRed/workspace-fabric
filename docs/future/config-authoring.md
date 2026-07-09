# Future Configuration Authoring Tool

## Purpose

The Milestone 3.4 deliverable is static YAML for the physical lab. Long term,
Workspace Fabric should not require users to hand-author YAML.

This document captures the future product direction without expanding the
current milestone scope.

## Product Direction

A future configuration authoring tool should allow a user to:

1. Select available hardware from a driver-backed catalog.
2. Add one or more hardware instances.
3. Define connection details for each instance.
4. Assign hosts, displays, USB devices, and other resources to physical ports.
5. Validate the resulting resource graph.
6. Define workspaces and scenes.
7. Generate or update the Workspace Fabric configuration.
8. Optionally save the current observed state as a scene or workspace.

## API Boundary

The UI should not contain the real configuration logic.

The control plane should expose API operations for:

- Listing available driver types.
- Listing driver-declared port/capability metadata.
- Creating or updating hardware instances.
- Assigning resources to ports.
- Validating a candidate configuration.
- Producing a transaction preview.
- Saving a validated configuration.
- Capturing observed state when supported by drivers.

## Deferred Features

The following should not be part of Milestone 3.4:

- Interactive configuration UI.
- Config generation wizard.
- Scene snapshot button.
- Automatic topology discovery.
- Driver-based hardware autodetection.
- Persistent configuration editing API beyond what is already required.

## Dependency Notes

Scene/workspace snapshotting depends on mature observed-state support. If a
driver cannot query current state, the system should not pretend it can safely
capture that state as a reusable scene.
