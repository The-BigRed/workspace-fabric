# Phase 4 Implementation Checklist – Milestones 4.2–4.6

This checklist details the exact steps to execute after Milestone 4.1 audit completion.

---

## Milestone 4.2 – Monorepo Package Structure

### Preparation
- [ ] Review audit findings in `ai/implementation/milestone-4.1-audit.md`
- [ ] Verify all tests pass before restructuring
- [ ] Backup current source layout

### Package Directory Creation
- [ ] Create `packages/` directory at workspace root
- [ ] Create `packages/core/`
- [ ] Create `packages/driver-api/`
- [ ] Create `packages/driver-mock/`
- [ ] Create `packages/driver-orei-uhd808/`
- [ ] Create `packages/driver-orei-ukm404/`

### Core Package (`packages/core/`)
- [ ] Create `packages/core/pyproject.toml` (copy from root, adjust name/deps)
- [ ] Create `packages/core/src/workspace_fabric/`
- [ ] Move `src/workspace_fabric/api/` → `packages/core/src/workspace_fabric/api/`
- [ ] Move `src/workspace_fabric/cli/` → `packages/core/src/workspace_fabric/cli/`
- [ ] Move `src/workspace_fabric/config/` → `packages/core/src/workspace_fabric/config/`
- [ ] Move `src/workspace_fabric/core/` → `packages/core/src/workspace_fabric/core/`
- [ ] Move `src/workspace_fabric/integrations/` → `packages/core/src/workspace_fabric/integrations/`
- [ ] Move `src/workspace_fabric/__init__.py` → `packages/core/src/workspace_fabric/__init__.py`
- [ ] Update `packages/core/pyproject.toml`:
  - Set `name = "workspace-fabric"`
  - Add dependency: `workspace-fabric-driver-api`
  - Remove mock and vendor driver imports from entry points
- [ ] Create `packages/core/tests/` (copy from tests/)

### Driver API Package (`packages/driver-api/`)
- [ ] Create `packages/driver-api/pyproject.toml`
- [ ] Create `packages/driver-api/src/workspace_fabric_driver_api/`
- [ ] Copy `src/workspace_fabric/drivers/base/types.py` → `packages/driver-api/src/workspace_fabric_driver_api/types.py`
- [ ] Create `packages/driver-api/src/workspace_fabric_driver_api/__init__.py`
- [ ] Update `pyproject.toml`:
  - Set `name = "workspace-fabric-driver-api"`
  - Set `version = "1.0.0"` (independent versioning)
  - No dependencies except stdlib + PyYAML (for models)

### Mock Driver Package (`packages/driver-mock/`)
- [ ] Create `packages/driver-mock/pyproject.toml`
- [ ] Create `packages/driver-mock/src/workspace_fabric_driver_mock/`
- [ ] Move `src/workspace_fabric/drivers/mock/*` → `packages/driver-mock/src/workspace_fabric_driver_mock/`
- [ ] Update `pyproject.toml`:
  - Set `name = "workspace-fabric-driver-mock"`
  - Depend on: `workspace-fabric-driver-api`
- [ ] Create `packages/driver-mock/tests/` (copy mock tests)

### OREI UHD-808 Package (`packages/driver-orei-uhd808/`)
- [ ] Create `packages/driver-orei-uhd808/pyproject.toml`
- [ ] Create `packages/driver-orei-uhd808/src/workspace_fabric_driver_orei_uhd808/`
- [ ] Move `src/workspace_fabric/drivers/video/orei_uhd808.py` → `packages/driver-orei-uhd808/src/workspace_fabric_driver_orei_uhd808/driver.py`
- [ ] Create `packages/driver-orei-uhd808/src/workspace_fabric_driver_orei_uhd808/__init__.py`
- [ ] Update `pyproject.toml`:
  - Set `name = "workspace-fabric-driver-orei-uhd808"`
  - Depend on: `workspace-fabric-driver-api`
- [ ] Create `packages/driver-orei-uhd808/tests/` (copy UHD-808 tests)

### OREI UKM-404 Package (`packages/driver-orei-ukm404/`)
- [ ] Create `packages/driver-orei-ukm404/pyproject.toml`
- [ ] Create `packages/driver-orei-ukm404/src/workspace_fabric_driver_orei_ukm404/`
- [ ] Move `src/workspace_fabric/drivers/usb/orei_ukm404.py` → `packages/driver-orei-ukm404/src/workspace_fabric_driver_orei_ukm404/driver.py`
- [ ] Create `packages/driver-orei-ukm404/src/workspace_fabric_driver_orei_ukm404/__init__.py`
- [ ] Update `pyproject.toml`:
  - Set `name = "workspace-fabric-driver-orei-ukm404"`
  - Depend on: `workspace-fabric-driver-api`
- [ ] Create `packages/driver-orei-ukm404/tests/` (copy UKM-404 tests)

### Root Development Workspace
- [ ] Update root `pyproject.toml`:
  - Remove driver code, keep only CLI entry point
  - Add dev dependencies from all packages
  - Add notes about monorepo structure
- [ ] Create root-level test runner script (runs all package tests)
- [ ] Create root-level formatter/linter commands

### Cleanup and Verification
- [ ] Remove old `src/workspace_fabric/drivers/` directory
- [ ] Update all imports in core code to use new paths
- [ ] Run root linter: ensure all code is formatted
- [ ] Run root test suite: all tests must pass
- [ ] Verify each package can be built independently: `pip install -e packages/*/`
- [ ] Verify CLI entry point still works
- [ ] Verify example configurations still load

### Documentation
- [ ] Update `README.md` to document monorepo structure
- [ ] Create `PACKAGE_STRUCTURE.md` explaining each package role
- [ ] Update `CONTRIBUTING.md` with instructions for package development

---

## Milestone 4.3 – Versioned Driver API

### API Extraction
- [ ] Review current Driver base classes and contracts
- [ ] Create `PluginDescriptor` class in driver-api
- [ ] Create `ApiCompatibilityVersion` in driver-api
- [ ] Create `DriverPlugin` interface in driver-api
- [ ] Create `get_plugin_descriptor()` entry-point contract

### Driver API Package Updates
- [ ] Add `PluginDescriptor`, `ApiCompatibilityVersion`, `DriverPlugin` to driver-api
- [ ] Define semantic versioning policy in docstring
- [ ] Add version validation examples in driver-api docs
- [ ] Bump driver-api version to "1.0.0" (or appropriate initial version)
- [ ] Add docstring: "This API version is independent of package versions"

### Core Package Updates
- [ ] Update `src/workspace_fabric/drivers/factory.py` to accept `PluginDescriptor`
- [ ] Update factory to validate compatibility versions
- [ ] Remove direct imports of vendor drivers (replace with entry-point discovery)
- [ ] Add compatibility version to factory discovery result

### Driver Package Updates
- [ ] Each driver package: Create `plugin.py` module
- [ ] Each driver: Define `get_plugin_descriptor()` function
- [ ] Each driver: Declare supported API version
- [ ] Each driver: Return `PluginDescriptor` with metadata

### Testing
- [ ] Add tests for Driver API contracts
- [ ] Add tests for compatibility version validation
- [ ] Add tests for missing/incompatible drivers
- [ ] Run all package tests

### Documentation
- [ ] Document Driver API versioning policy
- [ ] Document how drivers declare compatibility
- [ ] Update driver template documentation

---

## Milestone 4.4 – Installed-Driver Discovery

### Entry Points
- [ ] Add entry-point group: `workspace_fabric.drivers`
- [ ] Add entry points to `packages/driver-mock/pyproject.toml`:
  ```toml
  [project.entry-points."workspace_fabric.drivers"]
  mock_video_matrix = "workspace_fabric_driver_mock.plugin:get_plugin"
  mock_usb_matrix = "workspace_fabric_driver_mock.plugin:get_plugin"
  ```
- [ ] Add entry points to `packages/driver-orei-uhd808/pyproject.toml`:
  ```toml
  [project.entry-points."workspace_fabric.drivers"]
  orei_uhd808 = "workspace_fabric_driver_orei_uhd808.plugin:get_plugin"
  ```
- [ ] Add entry points to `packages/driver-orei-ukm404/pyproject.toml`:
  ```toml
  [project.entry-points."workspace_fabric.drivers"]
  orei_ukm404 = "workspace_fabric_driver_orei_ukm404.plugin:get_plugin"
  ```

### Factory Refactoring
- [ ] Rewrite `workspace_fabric/drivers/factory.py`:
  - Remove hard-coded imports
  - Add `discover_drivers()` using `importlib.metadata.entry_points()`
  - Add plugin load error isolation and logging
  - Add duplicate driver type detection
  - Return dict of `{driver_type: PluginDescriptor}`
- [ ] Update `create_driver()` to use discovered drivers
- [ ] Add `get_discovered_drivers()` public function
- [ ] Add `get_driver_types()` public function
- [ ] Update error messages to include available drivers

### Mock Driver Detection
- [ ] Add `is_mock` field to `PluginDescriptor`
- [ ] Each mock driver sets `is_mock=True` in its descriptor
- [ ] Rewrite `is_mock_driver_type(driver_type)`:
  ```python
  def is_mock_driver_type(driver_type: str) -> bool:
      descriptor = DISCOVERED_DRIVERS.get(driver_type)
      return descriptor.is_mock if descriptor else False
  ```

### Error Handling
- [ ] Create `MissingDriverError` exception
- [ ] Create `IncompatibleDriverError` exception
- [ ] Create `PluginLoadError` exception
- [ ] Add structured error reporting with:
  - Driver type that failed
  - Available types
  - Suggested installation command
  - Root cause if available

### Testing
- [ ] Add tests for entry-point discovery
- [ ] Add tests for duplicate driver type detection
- [ ] Add tests for plugin load failure isolation
- [ ] Add tests for missing driver error messages
- [ ] Add tests for incompatible driver detection
- [ ] Run all package tests

### Documentation
- [ ] Document entry-point registration
- [ ] Document plugin descriptor contract
- [ ] Document error handling behavior
- [ ] Update deployment guide with required packages

---

## Milestone 4.5 – Driver Metadata and Catalog

### Driver Descriptor Metadata
- [x] Ensure each plugin descriptor reports a stable driver type
- [x] Ensure each plugin descriptor reports a display name
- [x] Ensure each plugin descriptor reports a driver package version
- [x] Ensure each plugin descriptor reports supported Driver API compatibility
- [x] Ensure each plugin descriptor reports a factory
- [x] Ensure each plugin descriptor reports configuration requirements
- [x] Ensure each plugin descriptor reports port metadata
- [x] Ensure each plugin descriptor reports capability metadata

### Catalog Projection
- [x] Add a core-facing driver catalog built from entry-point discovery
- [x] List compatible installed drivers as available catalog entries
- [x] List incompatible drivers as unavailable entries with diagnostics
- [x] List duplicate driver types as unavailable entries with diagnostics
- [x] Preserve plugin-load failures as catalog-level diagnostics
- [x] Provide a serializable catalog dump for future Phase 5 APIs

### Testing
- [x] Add tests for compatible catalog metadata
- [x] Add tests for incompatible Driver API catalog entries
- [x] Add tests for duplicate driver type catalog entries
- [x] Add tests for plugin-load failure catalog diagnostics
- [x] Add package tests for descriptor metadata
- [x] Add isolated-wheel regression coverage for core catalog packaging

### Documentation
- [x] Update Phase 4 milestone status
- [x] Add Milestone 4.5 implementation report
- [x] Document descriptor metadata expectations
- [x] Document core wheel packaging defect and fix

---

## Milestone 4.6 – Driver Migration

### Implementation Migration
- [x] Remove legacy mock driver implementation modules from the core package
- [x] Remove legacy OREI UHD-808 implementation module from the core package
- [x] Remove legacy OREI UKM404 implementation module from the core package
- [x] Keep implementation classes in their independently installable driver packages
- [x] Preserve stable driver type identifiers
- [x] Preserve existing protocol behavior and mocked transport tests

### Dependency Direction
- [x] Verify core source does not import driver implementation packages
- [x] Verify driver packages do not import core configuration or orchestration modules
- [x] Remove driver package test `pythonpath` entries that pointed at the core package
- [x] Keep driver packages dependent only on `workspace-fabric-driver-api` and runtime vendor dependencies

### Testing
- [x] Update root tests to import driver implementations from driver packages
- [x] Add migration regression tests for source/package boundaries
- [x] Extend core isolated-wheel coverage to verify migrated implementation modules are absent from `workspace-fabric-core`
- [x] Add portable sdist-to-wheel regression coverage for `workspace-fabric-core`
- [x] Verify a core-only install does not install implementation driver packages
- [x] Run root unit and driver tests
- [x] Run package tests

### Documentation
- [x] Update Phase 4 milestone status
- [x] Add Milestone 4.6 implementation report
- [x] Record generated build-artifact cleanup required after implementation migration
- [x] Record core sdist packaging defect and fix

---

## Physical Regression Testing

### Before Phase 4.2
- [ ] Run physical smoke tests with current monolithic structure
- [ ] Document baseline behavior
- [ ] Record any pre-existing issues

### After Phase 4.5
- [ ] Run physical smoke tests with all packages installed
- [ ] Verify UHD-808 routing still works
- [ ] Verify UKM-404 routing still works
- [ ] Verify mock drivers still work
- [ ] Compare results to baseline (should be identical)

---

## Post-Phase 4 Acceptance

### Code Review
- [ ] Review all package structures
- [ ] Review dependency direction (core → driver-api; drivers → driver-api; no other cross-package imports)
- [ ] Review entry-point registration
- [ ] Review error handling and reporting

### Integration Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Physical smoke tests pass
- [ ] CLI tests pass
- [ ] State replay tests pass

### Documentation Review
- [ ] PACKAGE_STRUCTURE.md updated
- [ ] README.md updated
- [ ] CONTRIBUTING.md updated
- [ ] Deployment guide updated
- [ ] Driver template documentation created

### Sign-Off
- [ ] ADR-0006 implementation complete
- [ ] Package independence verified
- [ ] No vendor code remains in core
- [ ] Entry points discoverable and working
- [ ] Plugin lifecycle tested
- [ ] Backward compatibility maintained

---

## Files Created/Updated Summary

### New Files (4.2)
- `packages/core/pyproject.toml`
- `packages/driver-api/pyproject.toml`
- `packages/driver-mock/pyproject.toml`
- `packages/driver-orei-uhd808/pyproject.toml`
- `packages/driver-orei-ukm404/pyproject.toml`
- `PACKAGE_STRUCTURE.md`

### New Files (4.3)
- `packages/driver-api/src/workspace_fabric_driver_api/plugin.py`
- Driver-specific `plugin.py` files in each driver package

### Updated Files (4.2)
- Root `pyproject.toml`
- All package imports
- README.md, CONTRIBUTING.md

### Updated Files (4.4)
- `src/workspace_fabric/drivers/factory.py` (major rewrite)
- All driver `pyproject.toml` files (add entry points)

### Updated Files (4.5)
- `src/workspace_fabric/drivers/catalog.py`
- Driver package `plugin.py` metadata descriptors
- Driver catalog and package plugin tests
- Phase 4 status and implementation documentation

### Updated Files (4.6)
- Moved core source to `packages/core/src/workspace_fabric/`
- Removed legacy implementation modules under `workspace_fabric/drivers/mock/`
- Removed legacy implementation modules under `workspace_fabric/drivers/video/`
- Removed legacy implementation modules under `workspace_fabric/drivers/usb/`
- Updated root tests to use driver package imports
- Updated driver package factories to avoid runtime core model imports
- Updated `packages/core/pyproject.toml` to use package-local `src`
- Updated root `pyproject.toml` development paths to use `packages/core/src`
- Added `tests/drivers/test_driver_migration.py`

---

## Success Criteria

✅ Phase 4 is complete when:
1. All code builds independently
2. All tests pass (unit, integration, physical)
3. No vendor code is imported into core
4. All configured drivers can be discovered
5. Missing/incompatible drivers fail validation gracefully
6. ADR-0006 requirements are met
7. Physical hardware behaves identically to Phase 3
8. Driver types remain stable
9. Configuration format is unchanged
10. Backward compatibility is maintained
