# Milestone 4.5 - Driver Metadata and Catalog

**Completion Date:** 2026-07-13
**Status:** Complete
**Milestone:** Phase 4 - Modular Driver Platform

## Overview

Milestone 4.5 adds a core-facing driver catalog built from the installed
entry-point discovery results introduced in Milestone 4.4.

The catalog projects `PluginDescriptor` data into serializable metadata that
future Phase 5 APIs and controller-onboarding tools can consume without
importing driver implementation packages directly. Driver construction remains
owned by the existing factory path.

## Deliverables

- Added `workspace_fabric.drivers.catalog` with:
  - `DriverCatalog`
  - `DriverCatalogEntry`
  - `DriverCatalogIssue`
  - `build_driver_catalog()`
  - `get_driver_catalog()`
  - `get_available_driver_catalog()`
- Exported the catalog API from `workspace_fabric.drivers`.
- Catalog entries include:
  - Driver type
  - Display name
  - Driver package version
  - Supported Driver API version
  - Package name
  - Mock-driver marker
  - Configuration requirements
  - Port metadata
  - Capability metadata
  - Availability state
  - Structured diagnostics
- Incompatible plugins are listed as unavailable with descriptor metadata and
  compatibility diagnostics.
- Duplicate driver type identifiers are listed as unavailable with duplicate
  diagnostics.
- Plugin-load failures remain catalog-level diagnostics so unrelated compatible
  drivers remain available.
- Mock, UHD-808, and UKM404 plugin descriptors now all report configuration,
  port, and capability metadata.

## Acceptance Criteria

- Core can list compatible installed drivers through `get_driver_catalog()` and
  `get_available_driver_catalog()`.
- Incompatible plugins appear as unavailable catalog entries with
  `incompatible_driver_api` diagnostics.
- Duplicate driver type identifiers appear as unavailable catalog entries with
  `duplicate_driver_type` diagnostics.
- Broken plugin entry points are isolated as `plugin_load_failed` diagnostics.
- Catalog entries are dumpable as plain dictionaries for future API use.
- Existing driver factory behavior and driver type identifiers are preserved.

## Backward Compatibility

- Existing YAML configuration remains unchanged.
- Existing driver type identifiers remain stable:
  - `mock_video_matrix`
  - `mock_usb_matrix`
  - `orei_uhd808`
  - `orei_ukm404`
- Existing `create_driver()`, `create_drivers()`, `get_driver_types()`, and
  `get_driver_descriptors()` behavior is preserved.
- The catalog is additive and does not change physical routing behavior.

## Packaging Defect Fix

After initial Milestone 4.5 completion, isolated-wheel validation found that
`workspace-fabric-core` still packaged only the Phase 4.2 scaffold under
`packages/core/src/workspace_fabric/__init__.py`.

Impact:

- Source-tree tests passed because root `pyproject.toml` placed repository
  `src/` on `PYTHONPATH`.
- The built `workspace-fabric-core` wheel installed successfully but omitted
  the real `workspace_fabric.drivers` package.
- `from workspace_fabric.drivers import get_driver_catalog` failed in an
  isolated environment installed only from wheels.

Root cause:

- `packages/core/pyproject.toml` used
  `[tool.setuptools.packages.find] where = ["src"]`, which pointed at the
  scaffold package in `packages/core/src`.
- The real core implementation still lives at repository `src/workspace_fabric`
  during the Phase 4 migration.

Fix:

- Updated `packages/core/pyproject.toml` so the core wheel packages the
  repository-level `src/workspace_fabric` implementation through
  `package-dir = {"" = "../../src"}` and `where = ["../../src"]`.
- Removed the stale scaffold `packages/core/src/workspace_fabric/__init__.py`
  so there is not a second authoritative `workspace_fabric` package.
- Added an isolated-wheel regression test that builds the core and driver
  wheels, installs them into a temporary virtual environment, imports
  `workspace_fabric.drivers`, calls `get_driver_catalog()`, confirms all
  expected installed driver entry points are discovered, and verifies
  `pip show -f workspace-fabric-core` lists the packaged driver catalog files.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\drivers\test_driver_catalog.py -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest tests\drivers -v
.\.venv\Scripts\python.exe -m pytest packages\driver-api\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-mock\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-uhd808\tests -v
.\.venv\Scripts\python.exe -m pytest packages\driver-orei-ukm404\tests -v
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
.\.venv\Scripts\python.exe -m pip wheel --no-deps --wheel-dir .tmp\wheelhouse packages\driver-api packages\driver-mock packages\driver-orei-uhd808 packages\driver-orei-ukm404 packages\core
Remove-Item -LiteralPath .tmp\wheelhouse -Recurse -Force
git diff --check
.\.venv\Scripts\python.exe -m black packages src tests
.\.venv\Scripts\python.exe -m ruff check packages src tests
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest packages\core\tests -v
```

Results:

- Targeted catalog tests: passed, 5 tests.
- Black: passed after formatting the new catalog module and catalog tests.
- Ruff: passed.
- Root driver suite: passed, 71 tests.
- Driver API package tests: passed, 6 tests.
- Mock driver package tests: passed, 1 test.
- OREI UHD-808 package tests: passed, 1 test.
- OREI UKM404 package tests: passed, 1 test.
- Full root suite: passed, 125 tests.
- Core scaffold/package tests: passed, 3 tests.
- Package wheel build: passed for all five packages.
- Temporary wheel artifacts were removed after verification.
- `git diff --check`: passed; Git reported only expected CRLF normalization
  warnings for touched text files.
- Packaging defect regression test: passed, 3 package tests.
- Post-fix Black: passed, 83 files unchanged.
- Post-fix Ruff: passed.
- Post-fix full root suite: passed, 125 tests.
- Post-fix isolated wheel validation initially hit a Windows venv launcher
  access-denied error in the sandbox, then passed outside the sandbox.
- Fresh wheel validation built and installed all five wheels into a clean
  temporary virtual environment.
- Installed `get_driver_catalog()` reported:
  `mock_usb_matrix,mock_video_matrix,orei_uhd808,orei_ukm404`.
- `pip show -f workspace-fabric-core` listed
  `workspace_fabric/drivers/__init__.py`,
  `workspace_fabric/drivers/catalog.py`,
  `workspace_fabric/drivers/factory.py`,
  `workspace_fabric/drivers/base/__init__.py`, and
  `workspace_fabric/drivers/base/types.py`.

## Known Limitations

- Catalog data is static descriptor metadata plus discovery diagnostics; runtime
  hardware probing remains future onboarding work.
- Full driver migration and removal of legacy in-core driver modules continue
  in Milestone 4.6.
- Lifecycle upgrade, rollback, uninstall, and configured-missing-driver
  deployment scenarios remain Milestone 4.7 work.
