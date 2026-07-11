# ADR-0006: Modular Driver Packaging, Discovery, and Versioning

## Status

Accepted

## Context

Workspace Fabric already separates high-level orchestration from vendor-specific
behavior through the driver/controller boundary. Phase 3 validated that model
against physical OREI UHD-808 and UKM404 hardware.

The initial implementation may keep driver code inside the same Python package
or register driver implementations through core-owned code. That arrangement is
acceptable during early development but does not provide the desired operational
lifecycle.

Drivers must be able to evolve independently from the core application. A user
who replaces an HDMI matrix should be able to uninstall the old driver without
modifying or upgrading the core. A driver bug fix, firmware compatibility
update, feature release, or rollback should not require a new core release when
the shared contract remains compatible.

The project will remain in one Git repository for the foreseeable future, but
repository location and runtime package boundaries are separate concerns.

## Decision

Workspace Fabric will use independently installable and independently versioned
driver packages discovered through standard Python package entry points.

The software will be divided into these logical package roles:

1. **Core application**
   - Configuration loading and validation
   - Resource graph
   - Transaction planning and execution
   - Desired and observed state
   - CLI, API, persistence, and interfaces

2. **Driver API**
   - Portable driver interfaces
   - Driver actions and results
   - Capability and state contracts
   - Structured issues and errors
   - Plugin descriptor and compatibility contract

3. **Driver implementations**
   - Vendor-, platform-, protocol-, or service-specific behavior
   - Independent package metadata and semantic version
   - Entry-point registration

4. **Driver packs**
   - Optional convenience metapackages that depend on multiple driver packages
   - Not the unit of runtime discovery or lifecycle management

The initial package direction is:

```text
workspace-fabric
workspace-fabric-driver-api
workspace-fabric-driver-mock
workspace-fabric-driver-orei-uhd808
workspace-fabric-driver-orei-ukm404
```

The repository remains a monorepo and may use a layout such as:

```text
packages/
  core/
  driver-api/
  driver-mock/
  driver-orei-uhd808/
  driver-orei-ukm404/
```

### Discovery

Driver packages register plugins through a Python entry-point group:

```toml
[project.entry-points."workspace_fabric.drivers"]
orei_uhd808 = "workspace_fabric_driver_orei_uhd808.plugin:get_plugin"
```

The core discovers installed entry points through `importlib.metadata` or the
stable equivalent for the supported Python version.

The core will not discover production drivers by recursively scanning folders,
importing arbitrary Python files, or maintaining a vendor-specific registry.

### Dependency Direction

Allowed dependencies:

```text
Core ───────────────┐
                    ├──> Driver API
Driver implementation┘
```

The core must not import vendor driver implementations. Driver implementations
must not import core orchestration modules.

### Compatibility

The Driver API has an explicit compatibility version independent of package
release versions. Each driver plugin declares the Driver API versions it
supports. The core declares the Driver API versions it accepts.

An incompatible driver must be rejected before controller construction with a
structured diagnostic.

The project should preserve compatibility with at least the immediately prior
Driver API major version when practical, but no permanent multi-version support
is required.

### Lifecycle Behavior

- Installing a compatible driver makes its driver type discoverable.
- An installed but unused driver has no effect on normal operation.
- Removing an unused driver does not affect the core or unrelated controllers.
- Removing a configured driver causes configuration validation to fail clearly.
- Updating or rolling back a compatible driver does not require a core release.
- A plugin-load failure should not prevent unrelated compatible plugins from
  loading where practical.
- Existing stable driver type identifiers should remain valid across packaging
  migration.

### Versioning

The core, Driver API, and every driver package use independent semantic
versioning.

Examples:

- A driver parser fix increments only the driver patch version.
- A driver capability added within the existing contract increments only the
  driver minor version.
- A backward-compatible core or Driver API extension increments the relevant
  minor version.
- A breaking public or Driver API change increments the relevant major version.

The first modularized driver packages may use pre-1.0 versions while their
package-specific support policies mature.

## Rationale

Standard package entry points provide a mature discovery mechanism without
inventing a custom plugin loader. Independent packages give operators normal
installation, upgrade, rollback, and removal workflows through Python package
tooling. A shared Driver API preserves type and contract consistency without
coupling drivers to core implementation details.

Keeping the packages in a monorepo initially reduces administrative overhead,
allows coordinated testing, and preserves a simple contribution workflow. The
package boundary allows individual drivers to move to separate repositories in
the future without changing runtime discovery or configuration semantics.

## Consequences

- The repository requires a package-oriented restructuring.
- Existing driver imports and registration must be audited and migrated.
- Tests must cover discovery, compatibility, missing drivers, broken plugins,
  upgrade, rollback, and removal.
- The Phase 5 configuration application can consume a dynamic driver catalog.
- Driver releases no longer require core version changes when the contract is
  unchanged.
- The core distribution does not need to contain vendor-specific drivers.
- Deployment documentation must identify which driver packages are required by
  a given configuration.
- The initial migration should preserve working protocol code rather than
  rewrite the physical drivers.

## Alternatives Considered

### Keep drivers inside the core package

Rejected because driver changes would remain tied to core releases and unused
vendor code could not be cleanly removed.

### Scan a configured drivers directory

Rejected as the primary production mechanism because arbitrary filesystem
loading complicates packaging, security, compatibility checks, upgrades, and
reliable metadata discovery.

### Create separate Git repositories immediately

Deferred. Independent package boundaries provide the required runtime and
release separation without multiplying repository administration before the
plugin model stabilizes.

### Use a custom plugin registry service

Rejected for the initial implementation. Python entry points already provide
the required installed-package discovery mechanism.
