# Workspace Fabric Driver Contract

## Purpose

This document defines the behavioral and packaging contract between Workspace
Fabric, its shared Driver API, and independently distributed driver
implementations.

Drivers isolate vendor-, protocol-, platform-, and service-specific behavior
from the core orchestration engine. The core never directly speaks Telnet,
RS-232, Redfish, PiKVM APIs, Windows APIs, or other native interfaces.

## Package Roles

### Core Application

The core owns configuration, topology, policy, planning, execution,
persistence, and interfaces.

### Driver API Package

The Driver API owns portable contracts shared by the core and driver packages:

- Base driver interfaces
- Driver actions
- Driver results
- Health and state models
- Capabilities
- Structured issues and errors
- Plugin descriptor
- Compatibility version

The Driver API must not depend on the core application or vendor drivers.

### Driver Package

A driver package implements one hardware family, software agent, platform,
protocol, or service integration. It is independently installed and versioned.

Examples:

- `workspace-fabric-driver-orei-uhd808`
- `workspace-fabric-driver-orei-ukm404`
- `workspace-fabric-driver-mock`

A package may expose more than one closely related driver type when that design
is intentional and documented, but stable driver type identifiers remain the
runtime unit selected by controller configuration.

## Dependency Boundary

Allowed:

```text
core ───────────────┐
                    ├──> driver-api
implementation ─────┘
```

Forbidden:

- Core imports of vendor driver packages
- Driver imports of core orchestration modules
- Driver-to-driver coordination
- Vendor-specific types in core configuration or transaction models

## Plugin Discovery

Driver packages register through the entry-point group:

```text
workspace_fabric.drivers
```

Example:

```toml
[project.entry-points."workspace_fabric.drivers"]
orei_uhd808 = "workspace_fabric_driver_orei_uhd808.plugin:get_plugin"
```

The entry point returns a plugin descriptor or a callable producing one.

The core discovers installed packages through standard Python package metadata.
It must not rely on arbitrary filesystem scanning as the production plugin
contract.

## Plugin Descriptor

Each plugin must expose machine-readable metadata sufficient for compatibility
validation and future configuration authoring.

Conceptually:

```python
@dataclass(frozen=True)
class DriverPlugin:
    driver_type: str
    display_name: str
    driver_version: str
    supported_driver_api: str
    factory: DriverFactory
    configuration_schema: Mapping[str, object]
    port_metadata: Mapping[str, object]
    capability_metadata: Mapping[str, object]
```

Exact Python types may evolve, but the descriptor must include:

- Stable driver type identifier
- Human-readable display name
- Driver implementation version
- Supported Driver API version or range
- Factory for configured instances
- Configuration requirements
- Port or endpoint metadata where known
- Capability metadata where known

Optional metadata may include:

- Vendor and model family
- Documentation links or identifiers
- Supported transports
- Authentication requirements
- Identity discovery
- Connectivity tests
- Firmware compatibility notes
- Deprecation information

## Stable Driver Type Identifiers

Configuration refers to a stable driver type, for example:

```yaml
controllers:
  video_matrix_uhd808:
    driver: orei_uhd808
```

The identifier must not depend on installation path, Python module name, or
package repository location. Package restructuring must preserve stable driver
type identifiers whenever practical.

## Driver API Compatibility

The Driver API has an explicit compatibility version. Drivers declare the
versions they support. The core validates compatibility before creating a
controller.

An incompatible plugin must produce a structured diagnostic identifying:

- Driver type
- Driver package version
- Declared Driver API compatibility
- Driver API version supported by the core

The core must not attempt best-effort execution through an incompatible
contract.

## Driver Lifecycle Behavior

- Installing a compatible driver makes it discoverable.
- An installed but unused driver must have no side effects.
- Removing an unused driver must not affect the core.
- A configured but missing driver must fail configuration validation clearly.
- Compatible driver upgrades and rollbacks must not require a core release.
- One plugin failure should not prevent unrelated compatible plugins from
  loading where practical.
- Driver installation and removal must not silently rewrite user configuration.

## Driver Responsibilities

A driver is responsible for:

- Connecting to its target
- Reporting health
- Reporting capabilities
- Reporting observed state where possible
- Validating driver-specific actions
- Planning driver-specific operations
- Translating portable actions into native commands
- Applying assigned actions
- Returning structured results and diagnostics
- Preserving raw native responses when useful for troubleshooting

## Driver Non-Responsibilities

A driver must not:

- Make global policy decisions
- Coordinate directly with other drivers
- Modify unrelated resources
- Interpret high-level workspace intent
- Assume global topology
- Own transaction execution
- Depend on deployment-specific logical resource names to operate
- Hide unsupported or unknown features by pretending they succeeded

## Common Runtime Interface

Drivers conceptually provide:

```text
connect()
disconnect()
health()
get_capabilities()
get_state()
validate_action(action)
plan_action(action)
apply_action(action)
```

The precise abstract interfaces live in the Driver API package.

### Method Requirements

| Method | Purpose | Side effects |
| --- | --- | --- |
| `connect()` | Establish communication. | May open connections; must not change workspace state. |
| `disconnect()` | Release communication resources. | Must not alter routes. |
| `health()` | Report `healthy`, `degraded`, `unreachable`, or `unknown`. | No route changes. |
| `get_capabilities()` | Return instance capability inventory. | No route changes. |
| `get_state()` | Return observed, last-known, assumed, or unknown state. | No route changes. |
| `validate_action()` | Validate an assigned action. | No hardware changes. |
| `plan_action()` | Describe the native operation. | No hardware changes. |
| `apply_action()` | Apply one assigned action. | May change only resources owned by that controller. |

## Stable Phase 3 Route Actions

| Action type | Interface | Required payload |
| --- | --- | --- |
| `video_route` | `VideoMatrixDriver` | `input_port`, `output_port` |
| `usb_route` | `UsbMatrixDriver` | `device_port`, `host_port` |

Video route helper:

```python
route_action(*, input_port: int, output_port: int) -> DriverAction
```

USB route helper:

```python
route_action(*, device_port: int, host_port: int) -> DriverAction
```

Logical names may be included for logging, dry-run, and transaction history,
but physical drivers operate on device-local ports resolved by the core.

## Health

Valid common states:

```text
healthy
degraded
unreachable
unknown
```

Health confirms communication status, not complete functional correctness.

## Capabilities

Valid capability statuses:

```text
supported
unsupported
unknown
```

Capabilities are controller-instance-specific. Drivers must not omit unknown or
unsupported required capabilities merely to pass validation.

## State

State labels:

```text
observed
last_known
assumed
unknown
```

If hardware cannot query current state, report that limitation. A successful
command send is not sufficient evidence for `observed` state.

## Validation and Planning

Driver validation should catch invalid ports, unsupported capabilities,
malformed actions, native constraints, and unavailable targets that are visible
to the driver.

Planning returns the native operation without applying it and must support
transaction dry-run.

## Applying

`apply_action()` applies only the single action assigned by the core. Results
must distinguish success, warning, failure, partial failure, and unknown
post-action state.

## Structured Issue Categories

Common categories include:

```text
connection_failed
timeout
unsupported_capability
invalid_resource
invalid_port
invalid_route
invalid_action
hardware_rejected_command
state_query_failed
partial_apply
authentication_failed
authorization_failed
missing_driver
incompatible_driver_api
plugin_load_failed
mock_failure
unknown_error
```

Drivers may add more specific categories later, but shared categories should be
used whenever applicable.

## Mock Drivers

Mock drivers are independently packaged, first-class implementations. They must
support capability reporting, state query, route application, dry-run planning,
failure injection, and unsupported-capability simulation.

Mock drivers should be installable through development or test extras rather
than being mandatory production dependencies.

## Versioning

Core, Driver API, and driver packages use independent semantic versioning.

- Driver fixes and compatible features change only the driver version.
- Backward-compatible Driver API additions change the Driver API minor version.
- Breaking Driver API changes change its major version.
- The core version changes only when the core changes.

## Testing Requirements

Every driver package should include:

- Unit tests for parsing and action behavior
- Mocked transport tests
- Configuration-schema tests
- Plugin descriptor tests
- Driver API compatibility tests
- Install/discovery tests
- Missing-dependency and plugin-load failure tests where applicable

The monorepo integration suite should verify:

- Dynamic discovery
- Duplicate driver type detection
- Missing-driver validation
- Incompatible Driver API handling
- Upgrade and rollback behavior
- Removal of unused drivers
- Preservation of physical smoke-test behavior
