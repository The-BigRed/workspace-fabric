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
- Scene and patch YAML schema expansion.
- Scene snapshot button.
- Automatic topology discovery.
- Driver-based hardware autodetection.
- Persistent configuration editing API beyond what is already required.

## Deferred Configuration-Model Evolution

Milestone 3.4 should remain scoped to a static physical-lab configuration using
the currently implemented V0 schema. The richer Controller -> Resource ->
Workspace -> Scene -> Patch object model remains the target architecture, but
the serialized YAML schema for scenes and patches should be introduced as a
versioned Phase 4 configuration-model evolution.

The Phase 4 schema work should include:

- Explicit typed models for controllers, grouped resources, hardware mappings,
  scenes, and patches.
- Loader validation for scene composition and patch scope.
- Planner support for activating scenes and applying patches without changing
  unrelated state.
- Migration from `version: 1` V0 files to the next schema version.
- Backward compatibility so existing V0 configurations such as
  `examples/local-workspace.yaml` and `examples/physical-local.yaml` continue
  to load or can be migrated deterministically.
- Preservation of the driver boundary: resource names may appear in plans and
  history as explanatory context, but drivers must continue to receive
  controller-local ports before invocation.

## Dependency Notes

Scene/workspace snapshotting depends on mature observed-state support. If a
driver cannot query current state, the system should not pretend it can safely
capture that state as a reusable scene.
