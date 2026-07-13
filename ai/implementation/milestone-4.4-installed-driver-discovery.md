# Milestone 4.4 - Installed-Driver Discovery

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.4 replaces the temporary hard-coded core driver registry with
standard Python package entry-point discovery.

Driver packages now register under the `workspace_fabric.drivers` entry-point
group. The active core factory discovers installed descriptors through
`importlib.metadata`, validates Driver API compatibility, rejects duplicate
driver type identifiers, isolates plugin-load failures, and constructs
configured drivers only through discovered `PluginDescriptor` factories.

## Deliverables

- Added entry points to:
  - `workspace-fabric-driver-mock`
  - `workspace-fabric-driver-orei-uhd808`
  - `workspace-fabric-driver-orei-ukm404`
- Rewrote `src/workspace_fabric/drivers/factory.py` to remove direct mock and
  OREI driver imports.
- Added discovery helpers:
  - `discover_drivers()`
  - `get_discovered_drivers()`
  - `get_driver_descriptors()`
  - `get_driver_types()`
- Added structured discovery diagnostics through `DriverDiscoveryIssue` and
  `DriverDiscoveryResult`.
- Added structured runtime errors:
  - `MissingDriverError`
  - `DuplicateDriverTypeError`
  - `IncompatibleDriverApiError`
  - `PluginLoadError`
- Preserved the existing `DRIVER_TYPES` export as a dynamic compatibility
  mapping over discovered drivers.

## Acceptance Criteria

- Installing a driver package makes its entry point discoverable.
- Removing an entry point removes that driver from the discovered catalog.
- The active core factory contains no vendor-specific driver imports.
- Discovery results are sorted and deterministic.
- Broken plugin entry points are reported without blocking unrelated compatible
  drivers.
- Duplicate driver type identifiers are reported and excluded from the usable
  catalog.
- Incompatible Driver API plugins are rejected before controller construction.

## Backward Compatibility

- Existing YAML configuration remains valid.
- Existing driver type identifiers remain stable:
  - `mock_video_matrix`
  - `mock_usb_matrix`
  - `orei_uhd808`
  - `orei_ukm404`
- Existing route payloads and transaction behavior remain unchanged.
- Existing `workspace_fabric.drivers.create_driver()` and `create_drivers()`
  callers continue to work when the required driver packages are installed.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-deps -e packages\driver-api -e packages\driver-mock -e packages\driver-orei-uhd808 -e packages\driver-orei-ukm404
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest packages\driver-api\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m pip wheel --no-deps --wheel-dir .tmp\wheelhouse packages\driver-api packages\driver-mock packages\driver-orei-uhd808 packages\driver-orei-ukm404 packages\core
```

Initial sandboxed editable-install attempt failed with a Windows venv launcher
access-denied error; the same command succeeded outside the sandbox.

Results:

- Editable install refresh: passed.
- Root driver suite: passed, 66 tests.
- Full root suite: passed, 120 tests.
- Black: passed after formatting two files.
- Ruff: passed.
- Driver API package tests: passed, 6 tests.
- Mock driver package tests: passed, 1 test.
- OREI UHD-808 package tests: passed, 1 test.
- OREI UKM404 package tests: passed, 1 test.
- Core scaffold/package tests: passed, 3 tests.
- Package wheel build: passed for all five packages.

Temporary wheel artifacts were removed after verification.

## Known Limitations

- Driver metadata catalog shaping is Milestone 4.5.
- Lifecycle tests for upgrade, rollback, uninstall, and broken-plugin
  deployment scenarios continue in Milestone 4.7.
- Legacy driver source modules remain in `src/workspace_fabric/drivers/` until
  the driver migration milestone removes them from the core distribution.
