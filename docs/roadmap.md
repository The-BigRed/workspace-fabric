# Workspace Fabric Roadmap

## Current Status

**Current Phase:** Phase 3 – Hardware Integration

Phase 2 is complete. Phase 3 is validating the architecture against real
hardware and software-controlled endpoints.

## Phase 1 – Architecture ✅

Architecture, philosophy, engineering contracts, AI guidance, and reference
documentation are complete.

The architecture remains intentionally evolvable through accepted Architecture
Decision Records.

## Phase 2 – Foundation ✅

1. Repository Skeleton ✅
2. Configuration Loader ✅
3. Resource Graph ✅
4. Mock Drivers ✅
5. Capability Validation ✅
6. Transaction Planner ✅
7. Transaction Executor ✅
8. Minimal CLI/API ✅
9. Persistent Mock State ✅

Completion Criteria:

- Configuration loads and validates.
- Resource graph builds successfully.
- Workspace planning succeeds.
- Mock transactions execute successfully.
- Mock driver state persists across CLI invocations.
- Transaction history is recorded.

## Phase 3 – Hardware Integration (Current)

### Deliverables

1. Driver contract hardening.
2. Physical lab configuration.
3. OREI UHD-808 HDMI driver.
4. OREI UKM404 USB driver.
5. Windows Display Agent.
6. PiKVM integration.
7. End-to-end physical smoke test.
8. Safety and recovery behavior.

### Completion Criteria

- Driver contract is stable and documented.
- Driver implementations are selected through configured controller instances.
- Physical lab configuration validates.
- Physical resource-to-port mappings reflect the installed lab topology.
- UHD-808 driver is functional for required Phase 3 routing operations.
- UKM404 driver is functional for required Phase 3 routing operations.
- Windows Display Agent is operational for required display-state control.
- PiKVM integration is operational for required capture and HID behavior.
- End-to-end routing is verified on physical hardware.
- CLI operates physical hardware without mock drivers.
- Driver failures, timeouts, unsupported capabilities, and unknown observed
  state are handled clearly.
- Dry-run explains the controller actions that will be attempted.
- Safety and recovery behavior is documented and tested.

### Phase 3 Constraints

- The goal is to prove the driver/controller boundary and validate the core
  architecture against physical reality.
- The production configuration-authoring application is not a Phase 3
  deliverable.
- The physical lab seed may be maintained manually during Phase 3.
- Drivers should expose configuration, identity, port, capability, and state
  metadata needed by future configuration tooling where practical.
- DeviceGroup and composite endpoint support remain future model enhancements.
  Phase 3 may continue using descriptive routable resource names for composite
  USB endpoints.

## Phase 4 – API and Applications

### Deliverables

- Local API service.
- Authentication and operator permissions.
- Stable APIs for workspaces, scenes, patches, state, and transactions.
- Interactive configuration authoring.
- Driver catalog and device selection.
- Controller onboarding and connectivity validation.
- Driver-assisted identity, port, and capability discovery.
- Physical topology editor.
- Resource editor.
- Workspace editor.
- Scene editor.
- Patch editor.
- Web UI.
- Desktop client.
- Tablet UI.
- Automation integrations.
- Local Console Virtualization.

### Completion Criteria

- Stable local API is available.
- Authentication and operator permissions are implemented.
- All supported CLI functionality is available through the API.
- Users can create and validate controller instances without manually editing
  YAML.
- Users can map resources to discovered or declared controller endpoints.
- Users can author workspaces, scenes, and patches interactively.
- The resulting configuration can be serialized to and loaded from YAML.
- Web UI is operational.
- Desktop client is operational.
- Tablet UI is operational.
- External automation systems can request deterministic operations through the
  public API.

## Phase 5 – Ecosystem

### Deliverables

- Multi-fabric federation.
- Multi-user orchestration.
- Enterprise integrations.
- Plugin ecosystem.
- Additional third-party drivers and interfaces.
- Automation and AI consume the public API without special privileged
  interfaces.

### Completion Criteria

- Multiple fabrics can be orchestrated.
- Multi-user access control is implemented.
- External integrations are documented.
- Plugin API is stable.
- First third-party plugin is demonstrated.
- Third-party drivers can expose configuration and capability metadata without
  requiring device-specific changes to the core configuration UI.
