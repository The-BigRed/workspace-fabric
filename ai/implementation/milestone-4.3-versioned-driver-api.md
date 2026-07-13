# Milestone 4.3 - Versioned Driver API

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.3 establishes the versioned Driver API contract used by the core
and independently packaged drivers.

The implementation keeps existing YAML configuration, driver type identifiers,
and Phase 3 route action payloads unchanged. Installed-driver discovery remains
deferred to Milestone 4.4; the current hard-coded registry now carries
`PluginDescriptor` metadata and validates Driver API compatibility before
driver construction.

## Deliverables

- Added `ApiCompatibilityVersion`, `PluginDescriptor`, `DriverPlugin`, and
  `validate_driver_api_compatibility()` to `workspace-fabric-driver-api`.
- Added the explicit `DRIVER_API_COMPATIBILITY_VERSION` contract version.
- Added shared lifecycle issue categories:
  - `missing_driver`
  - `incompatible_driver_api`
  - `plugin_load_failed`
- Converted the legacy `workspace_fabric.drivers.base.types` module into a
  compatibility re-export of `workspace_fabric_driver_api`.
- Added plugin descriptor modules for:
  - `workspace_fabric_driver_mock`
  - `workspace_fabric_driver_orei_uhd808`
  - `workspace_fabric_driver_orei_ukm404`
- Updated the current core factory to validate descriptor compatibility before
  constructing a driver.
- Added package and root tests for descriptor metadata, compatibility success,
  compatibility rejection, and route action payload stability.

## Acceptance Criteria

- Driver API imports neither core nor vendor implementations.
- Core and drivers compile against the Driver API.
- Existing `video_route` and `usb_route` actions remain compatible.
- API version validation is tested.
- Incompatible Driver API descriptors are rejected before factory invocation.

## Backward Compatibility

- Existing YAML configuration remains valid.
- Existing driver type identifiers remain stable:
  - `mock_video_matrix`
  - `mock_usb_matrix`
  - `orei_uhd808`
  - `orei_ukm404`
- Existing physical route payloads remain unchanged:
  - `video_route` with `input_port` and `output_port`
  - `usb_route` with `device_port` and `host_port`
- The legacy `workspace_fabric.drivers` import surface continues to work.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python.exe -m pytest packages\driver-api\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests --fix
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest packages\driver-api\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m pip wheel --no-deps --no-build-isolation --wheel-dir .tmp\wheelhouse packages\driver-api packages\driver-mock packages\driver-orei-uhd808 packages\driver-orei-ukm404 packages\core
.\.venv\Scripts\python.exe -m pip wheel --no-deps --wheel-dir .tmp\wheelhouse packages\driver-api packages\driver-mock packages\driver-orei-uhd808 packages\driver-orei-ukm404 packages\core
```

Results:

- Driver API package tests: passed, 6 tests.
- Mock driver package tests: passed, 1 test.
- OREI UHD-808 package tests: passed, 1 test.
- OREI UKM404 package tests: passed, 1 test.
- Root driver suite: passed, 58 tests.
- Full root suite: passed, 112 tests.
- Core scaffold/package tests: passed, 3 tests.
- Black: passed after formatting one new file.
- Ruff: passed after applying import-order fixes.
- Package wheel build with `--no-build-isolation`: failed because the venv
  could not import `setuptools.build_meta`.
- Package wheel build with normal build isolation: passed for all five
  packages.

Temporary wheel artifacts were removed after verification.

## Known Limitations

- Production entry-point discovery is still Milestone 4.4.
- The active root core still uses the temporary hard-coded registry, now backed
  by descriptors.
- Missing-driver and plugin-load-failure lifecycle behavior are still completed
  in the discovery and lifecycle milestones.
