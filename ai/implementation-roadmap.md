# Workspace Fabric Implementation Roadmap for AI

## Current Phase

Phase 3 – Hardware Integration

The foundation is complete. The current objective is to validate the architecture
against physical hardware while preserving the Driver → Controller → Resource →
Workspace → Scene → Patch object model.

## Implementation Order

1. Driver contract hardening.
2. Validate physical-lab.seed.yaml.
3. Implement the OREI UHD-808 driver.
4. Implement the OREI UKM404 driver.
5. Implement the Windows Display Agent.
6. Implement PiKVM integration.
7. Execute end-to-end physical smoke tests.
8. Implement safety and recovery behavior.

## Architectural Guidance

- Drivers are reusable code.
- Controllers are configured driver instances.
- Resources represent physical devices and endpoints.
- Workspaces describe reusable operating environments.
- Scenes compose one or more workspaces.
- Patches perform partial, non-destructive routing changes.

Preserve this model. Do not invent alternate abstractions.

## Deferred Until Phase 4

- Interactive configuration UI
- Driver discovery UI
- Controller onboarding UI
- Resource editor
- Workspace editor
- Scene editor
- Patch editor
- Web/Desktop/Tablet clients

Phase 3 should expose the metadata these future tools will consume.
